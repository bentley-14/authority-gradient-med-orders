"""The one place that defines how `claude -p` is called for this experiment.

Both agents (responder and grader) go through call_claude(). See README.md in
this folder for what is and is not isolated.
"""
import json
import os
import subprocess
import time

CLAUDE_BIN = os.path.expanduser("~/.local/bin/claude")
WORKDIR = "/private/tmp/w"  # empty, neutral path, not a git repo
RETRY_WAITS = [30, 120, 300, 600]  # seconds, for usage or rate limit errors


def clean_env():
    # Nothing from the parent shell is passed on except what auth needs.
    return {"HOME": os.environ["HOME"], "USER": os.environ.get("USER", ""), "PATH": "/usr/bin:/bin"}


def build_command(system_prompt, model, effort):
    return [
        CLAUDE_BIN, "-p",
        "--safe-mode",
        "--system-prompt", system_prompt,
        "--tools", "",
        "--strict-mcp-config",
        "--setting-sources", "",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--model", model,
        "--effort", effort,
        "--output-format", "json",
    ]


def cli_version():
    out = subprocess.run([CLAUDE_BIN, "--version"], capture_output=True, text=True, env=clean_env())
    return out.stdout.strip()


def call_claude(system_prompt, user_prompt, model, effort):
    """Run one isolated call. The user prompt goes in on stdin.

    Returns a dict with the exact command, cwd, prompts, attempt count and the
    parsed JSON output of the CLI. Raises RuntimeError if every retry fails.
    """
    os.makedirs(WORKDIR, exist_ok=True)
    if os.listdir(WORKDIR):
        raise RuntimeError(WORKDIR + " is not empty")
    cmd = build_command(system_prompt, model, effort)
    last = ""
    for attempt, wait in enumerate([0] + RETRY_WAITS, start=1):
        time.sleep(wait)
        try:
            p = subprocess.run(cmd, input=user_prompt, capture_output=True, text=True,
                               cwd=WORKDIR, env=clean_env(), timeout=600)
            out = json.loads(p.stdout)
            if p.returncode == 0 and not out.get("is_error") and out.get("result"):
                return {"command": cmd, "cwd": WORKDIR, "system_prompt": system_prompt,
                        "user_prompt": user_prompt, "attempts": attempt, "raw_output": out}
            last = p.stdout[:2000] + p.stderr[:500]
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            last = repr(e)[:2000]
    raise RuntimeError("claude call failed after retries: " + last)


def resolved_model(raw_output):
    """Full model ID(s) the CLI reports it used, taken from modelUsage."""
    return ";".join(sorted(raw_output.get("modelUsage", {})))


def call_claude_conversation(system_prompt, user_turns, model, effort):
    """Run one isolated conversation with several real user turns.

    Same flags, cwd and environment as call_claude(), plus stream-json input
    and output so the process stays open between turns. Each user turn is
    sent only after the reply to the previous one has arrived. No session is
    saved. Returns the command, the turns, every raw event line from the CLI
    and the final "result" event of each turn. Raises RuntimeError if every
    retry fails.
    """
    os.makedirs(WORKDIR, exist_ok=True)
    if os.listdir(WORKDIR):
        raise RuntimeError(WORKDIR + " is not empty")
    cmd = build_command(system_prompt, model, effort)
    i = cmd.index("--output-format")
    cmd[i:i + 2] = ["--input-format", "stream-json", "--output-format", "stream-json", "--verbose"]
    last = ""
    for attempt, wait in enumerate([0] + RETRY_WAITS, start=1):
        time.sleep(wait)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, cwd=WORKDIR, env=clean_env())
        events, results = [], []
        try:
            for text in user_turns:
                msg = {"type": "user", "message": {"role": "user", "content": text}}
                p.stdin.write(json.dumps(msg) + "\n")
                p.stdin.flush()
                while True:
                    line = p.stdout.readline()
                    if not line:
                        raise RuntimeError("CLI exited early: " + p.stderr.read()[:500])
                    ev = json.loads(line)
                    events.append(ev)
                    if ev.get("type") == "result":
                        break
                if ev.get("is_error") or not ev.get("result"):
                    raise RuntimeError("error result: " + line[:1500])
                results.append(ev)
            p.stdin.close()
            p.wait(timeout=60)
            return {"command": cmd, "cwd": WORKDIR, "system_prompt": system_prompt,
                    "user_turns": user_turns, "attempts": attempt,
                    "raw_events": events, "results": results}
        except (RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            last = repr(e)[:2000]
            p.kill()
    raise RuntimeError("claude conversation failed after retries: " + last)
