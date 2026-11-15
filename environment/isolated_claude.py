"""The one place that defines how `claude -p` is called for this experiment.

Both agents (responder and grader) go through call_claude(). See README.md in
this folder for what is and is not isolated.
"""
import json
import os
import subprocess
import time

import shutil

# Experiment C runs on a second machine where the CLI is installed elsewhere.
# CLAUDE_BIN can be set explicitly; otherwise the original path, then PATH.
CLAUDE_BIN = (os.environ.get("CLAUDE_BIN")
              or (os.path.expanduser("~/.local/bin/claude")
                  if os.path.exists(os.path.expanduser("~/.local/bin/claude")) else None)
              or shutil.which("claude"))
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


TOOL_NAME = "mcp__order_entry__enter_order"  # how the CLI names the enter_order tool


def tool_env():
    # Two extra switches for tool runs: no deferred-tool placeholder in the tool list,
    # and no CLAUDE.md loading (safe mode cannot be used with an MCP server, see README).
    env = clean_env()
    env.update({"ENABLE_TOOL_SEARCH": "false", "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"})
    return env


def build_tool_command(system_prompt, model, effort, ledger_path):
    """Same flags as build_command() except: no --safe-mode (it blocks every MCP
    server, including one passed explicitly), plus the order-entry server and
    permission to call its one tool. Stream-json in and out for real turns."""
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mcp = {"mcpServers": {"order_entry": {
        "command": sys.executable,
        "args": [os.path.join(root, "order_entry", "server.py"), ledger_path]}}}
    return [
        CLAUDE_BIN, "-p",
        "--system-prompt", system_prompt,
        "--tools", "",
        "--mcp-config", json.dumps(mcp),
        "--strict-mcp-config",
        "--allowedTools", TOOL_NAME,
        "--setting-sources", "",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--model", model,
        "--effort", effort,
        "--input-format", "stream-json",
        "--output-format", "stream-json",
        "--verbose",
    ]


def call_claude_tool_conversation(system_prompt, first_turn, next_turn, model, effort,
                                  ledger_path, extra_env=None):
    """One isolated conversation in which the model can call enter_order.

    first_turn is the first user message. After each reply, next_turn(n) is
    called with the number of turns done so far and returns the next user
    message, or None to end the conversation. The order-entry server writes
    every tool call to ledger_path. Returns the command, the user turns sent,
    and for each turn the list of raw CLI events. Raises RuntimeError if every
    retry fails. A failed attempt's ledger is kept under a .failed name.
    """
    import threading
    os.makedirs(WORKDIR, exist_ok=True)
    if os.listdir(WORKDIR):
        raise RuntimeError(WORKDIR + " is not empty")
    cmd = build_tool_command(system_prompt, model, effort, ledger_path)
    env = tool_env()
    env.update(extra_env or {})
    last = ""
    for attempt, wait in enumerate([0] + RETRY_WAITS, start=1):
        time.sleep(wait)
        if os.path.exists(ledger_path):
            os.rename(ledger_path, "%s.failed_attempt%d" % (ledger_path, attempt - 1))
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True, cwd=WORKDIR, env=env)
        watchdog = threading.Timer(900, p.kill)
        watchdog.start()
        user_turns, turns = [], []
        try:
            text = first_turn
            while text is not None:
                p.stdin.write(json.dumps({"type": "user",
                                          "message": {"role": "user", "content": text}}) + "\n")
                p.stdin.flush()
                user_turns.append(text)
                events = []
                while True:
                    line = p.stdout.readline()
                    if not line:
                        raise RuntimeError("CLI exited early: " + p.stderr.read()[:500])
                    ev = json.loads(line)
                    events.append(ev)
                    if ev.get("type") == "result":
                        break
                if ev.get("is_error"):
                    raise RuntimeError("error result: " + line[:1500])
                turns.append(events)
                text = next_turn(len(turns))
            p.stdin.close()
            p.wait(timeout=60)
            return {"command": cmd, "cwd": WORKDIR, "env_names": sorted(env),
                    "system_prompt": system_prompt, "user_turns": user_turns,
                    "attempts": attempt, "turn_events": turns}
        except (RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            last = repr(e)[:2000]
            p.kill()
        finally:
            watchdog.cancel()
    raise RuntimeError("claude tool conversation failed after retries: " + last)


def turn_text(events):
    """The visible reply text of one turn: every assistant text block, in order."""
    parts = []
    for ev in events:
        if ev.get("type") == "assistant":
            for block in ev["message"].get("content", []):
                if block.get("type") == "text" and block.get("text", "").strip():
                    parts.append(block["text"].strip())
    return "\n\n".join(parts)


def turn_tool_calls(events):
    """The tool calls the model made in one turn, as seen in the CLI event stream."""
    calls = []
    for ev in events:
        if ev.get("type") == "assistant":
            for block in ev["message"].get("content", []):
                if block.get("type") == "tool_use":
                    calls.append({"name": block.get("name"), "input": block.get("input")})
    return calls
