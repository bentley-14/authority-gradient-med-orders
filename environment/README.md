# environment

Everything that defines how the two agents (responder and grader) are run.

- `isolated_claude.py`: the only code that calls the `claude` CLI. Both agents use it.
- `capture_request.py`: a local recorder used once to see the exact request the CLI builds.
- `evidence/`: saved results of the isolation checks.

## The exact command

Run with the working directory set to `/private/tmp/w` (an empty directory outside any git repo, created if missing) and with the user prompt on stdin:

```
env -i HOME=$HOME USER=$USER PATH=/usr/bin:/bin \
  ~/.local/bin/claude -p \
  --safe-mode \
  --system-prompt "<our system prompt text>" \
  --tools "" \
  --strict-mcp-config \
  --setting-sources "" \
  --disable-slash-commands \
  --no-session-persistence \
  --model <sonnet for responder, opus for grader> \
  --effort medium \
  --output-format json
```

CLI version 2.1.325, logged in through the subscription (no API key). `--bare` is not used because it needs an API key.

## What is isolated

- No CLAUDE.md (global or project), no skills, no plugins, no hooks, no MCP servers, no custom agents (`--safe-mode`, `--strict-mcp-config`, `--setting-sources ""`, `--disable-slash-commands`).
- No tools (`--tools ""`): the request carries an empty tool list.
- No memory directory and no project files: the working directory is empty and is not the repo.
- No inherited environment variables: `env -i` passes only HOME, USER and PATH. The parent shell had about 34 CLAUDE_* and ANTHROPIC_* variables set, including CLAUDE_EFFORT.
- No saved session (`--no-session-persistence`), so trials cannot see each other.
- Effort is passed explicitly and shows up in the request as `output_config.effort = medium`.

## How it was verified

1. Exact request body. The CLI was pointed at `capture_request.py` on 127.0.0.1 through ANTHROPIC_BASE_URL. The recorder stores the JSON body only (never headers), forwards nothing, and answers with an error. The body is saved in `evidence/captured_request_body_probe.json` (the `metadata` field dropped, the email redacted). In that body: the strings "Karpathy", "CLAUDE.md", "skill", "MEMORY" and "mcp__" do not occur, the em-dash and en-dash characters do not occur, the username and the repo name do not occur, `tools` is `[]`, the working directory shown is `/private/tmp/w` and "Is a git repository" is false.
2. Self-report. The same isolated command was run for real with a probe prompt asking the model to list everything it was given, once with sonnet and once with opus. Saved in `evidence/probe_response_sonnet.json` and `evidence/probe_response_opus.json`. Both report no tools, skills, MCP servers, memory or files, no rule about dashes, and no mention of Karpathy.

## Known limitation: three things the CLI always injects

The system prompt the model sees is not only ours. These three items are added by the CLI itself, could not be switched off under subscription login, and are the same in every trial:

1. Two extra system prompt blocks before ours: a billing header line (`x-anthropic-billing-header: cc_version=2.1.325.325; cc_entrypoint=sdk-cli;`) and the line `You are a Claude agent, built on Anthropic's Claude Agent SDK.`
2. A system-reminder placed in front of the user message that gives the email address of the logged-in account and says to keep it private.
3. An "Environment" block placed after the user message: working directory (`/private/tmp/w`), not a git repo, platform, shell, OS version, a paragraph about treating downloaded files as untrusted, the model name and ID, the knowledge cutoff, and today's date.

Because they are constant they are not confounded with seniority or severity, but they are part of what the responder and grader see. Whether they change behavior was not measured.

## Two-turn conversations (confirm pilot)

`call_claude_conversation()` in `isolated_claude.py` uses the same command, working directory and environment, with `--output-format json` replaced by `--input-format stream-json --output-format stream-json --verbose`. The process stays open, each user turn is written to stdin as one JSON line only after the previous reply has arrived, and nothing is saved to disk (`--no-session-persistence` is still set, no `--resume`).

Verified with `capture_request.py` in reply mode, which answers with a fixed fake assistant message so the CLI goes on to the next turn. `evidence/two_turn_request_1.json` and `evidence/two_turn_request_2.json` are the two request bodies. The second one contains, in order: user turn 1 (with the same account-email reminder in front), the same Environment block, the assistant reply, user turn 2. The system prompt blocks are identical in both requests and `tools` is `[]`. Two differences from the single-turn command were seen: the `thinking` setting is sent with `display: updates` instead of `display: omitted`, and the last part of the version number in the billing header line differed between captures (325.325 and 325.451). With a real model the assistant turn that is sent back also carries the model's thinking block. That was seen in the event log of the pilot, not in a recorded request.

## Tool run: the same isolation with one MCP tool

`--safe-mode` cannot be used with the order-entry tool. Tested with the request recorder: with `--safe-mode`, a server passed explicitly through `--mcp-config` is not started and the request has an empty tool list. So the tool run drops `--safe-mode` and relies on the other switches. The command (`build_tool_command()` in `isolated_claude.py`), again with cwd `/private/tmp/w`:

```
env -i HOME=$HOME USER=$USER PATH=/usr/bin:/bin \
  ENABLE_TOOL_SEARCH=false CLAUDE_CODE_DISABLE_CLAUDE_MDS=1 \
  ~/.local/bin/claude -p \
  --system-prompt "<responder system prompt for the tool run>" \
  --tools "" \
  --mcp-config '{"mcpServers":{"order_entry":{"command":"<python3>","args":["<repo>/order_entry/server.py","<ledger path>"]}}}' \
  --strict-mcp-config \
  --allowedTools mcp__order_entry__enter_order \
  --setting-sources "" \
  --disable-slash-commands \
  --no-session-persistence \
  --model sonnet --effort medium \
  --input-format stream-json --output-format stream-json --verbose
```

What keeps the local setup out without safe mode: `--setting-sources ""` loads no user, project or local settings (so none of their hooks, plugins or MCP servers), `--strict-mcp-config` allows only the server named on the command line, `--tools ""` removes every built-in tool, `--disable-slash-commands` removes skills and commands, and `CLAUDE_CODE_DISABLE_CLAUDE_MDS=1` switches off CLAUDE.md loading. `ENABLE_TOOL_SEARCH=false` is there because without it the CLI adds a second entry to the tool list, a placeholder named `DeferredToolPlaceholder`.

Evidence:

- `evidence/tool_two_turn_request_1.json` and `_2.json`: the two request bodies of a two-turn conversation run through `call_claude_tool_conversation()` against the recorder. In both, the only tool is `mcp__order_entry__enter_order` with the description and fields from `order_entry/server.py`. The system blocks and the three constant injections are the same as in the earlier runs. The strings "Karpathy", "CLAUDE.md", "skill", "memory", "plugin", "hook", "deferred", the username and the repo name do not occur, and there is no em-dash or en-dash. The second request contains user turn 1, the Environment block, the assistant reply, user turn 2.
- `evidence/tool_probe_response_sonnet.json`: the CLI's own start-up event and the model's self-report from a real call. The start-up event lists `tools: ["mcp__order_entry__enter_order"]`, one MCP server (`order_entry`), no skills and no slash commands. The plugins and agents it lists are the CLI's built-in ones. The model reports one tool, no skills, no memory, no files, no rule about dashes and no mention of Karpathy.
- In that self-report the model also describes two generic tool-use instructions (make independent tool calls together, and a note about deferred tools). These are not in the request body the CLI sends, so they are added on the API side when a tool list is present. They are the same in every tool-run conversation.
- The start-up event names an auto-memory path under `~/.claude/projects/` for the working directory. No such directory was created by these runs (checked), and the model has no file tools.

The graders in the tool run use the original safe-mode command with no tools.

## Other notes

- The per-trial logs record the command, which contains the absolute path of the CLI binary (and so the local username).
- The email address is redacted as `[REDACTED_EMAIL]` in everything saved here.
