# Deviations from EXP_C_PLAN.md

Every change to, or departure from, the Experiment C plan, with the time and the reason.

## Deviations

None so far.

## Notes fixed before any Experiment C conversation was run

- **Isolation re-check on the new machine (2026-11-15, about 2:30 PM ET).** The tool-run command was pointed at `environment/capture_request.py` in reply mode with a CEO prompt at sertraline 5x and a bare confirmation. Both recorded request bodies (`environment/evidence/exp_c_tool_two_turn_request_1.json`, `_2.json`, account email redacted) show: model `claude-sonnet-5-5`, exactly one tool (`mcp__order_entry__enter_order`), the same three constant CLI system blocks as Stage B (billing header with `cc_version=2.1.280`, the Agent SDK line, our system prompt), and none of the local user's CLAUDE.md, memory, skills, plugins, MCP connectors, name, or project files. No em or en dash characters. The account-email reminder is present, as on Stage B's machine.
- **CLI path.** `environment/isolated_claude.py` now takes `CLAUDE_BIN` from the environment, else the original `~/.local/bin/claude`, else `claude` on PATH. On this machine it resolves to `/opt/homebrew/bin/claude` (a native binary, so the cleaned PATH is not a problem).
- **hub.run_tool.** Uses a prompt's own `confirmation` text when the prompt has one (Experiment C), else the fixed confirmation as before, and records the `message` label. Earlier runs are unaffected.
