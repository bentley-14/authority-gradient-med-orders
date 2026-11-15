# Deviations from EXP_C_PLAN.md

Every change to, or departure from, the Experiment C plan, with the time and the reason.

## Deviations

None so far.

## Notes fixed before any Experiment C conversation was run

- **Isolation re-check on the new machine (2026-11-15, about 2:30 PM ET).** The tool-run command was pointed at `environment/capture_request.py` in reply mode with a CEO prompt at sertraline 5x and a bare confirmation. Both recorded request bodies (`environment/evidence/exp_c_tool_two_turn_request_1.json`, `_2.json`, account email redacted) show: model `claude-sonnet-5-5`, exactly one tool (`mcp__order_entry__enter_order`), the same three constant CLI system blocks as Stage B (billing header with `cc_version=2.1.280`, the Agent SDK line, our system prompt), and none of the local user's CLAUDE.md, memory, skills, plugins, MCP connectors, name, or project files. No em or en dash characters. The account-email reminder is present, as on Stage B's machine.
- **CLI path.** `environment/isolated_claude.py` now takes `CLAUDE_BIN` from the environment, else the original `~/.local/bin/claude`, else `claude` on PATH. On this machine it resolves to `/opt/homebrew/bin/claude` (a native binary, so the cleaned PATH is not a problem).
- **hub.run_tool.** Uses a prompt's own `confirmation` text when the prompt has one (Experiment C), else the fixed confirmation as before, and records the `message` label. Earlier runs are unaffected.

## Notes added during the run

- **Model addendum (2026-11-15, during pass 1, before any outcome was viewed).** `EXP_C_MODELS_ADDENDUM.md` adds a pre-registered repeat of the core C1 contrast (no_title, attending, ceo; bare confirmation) on `claude-opus-5-5` and `claude-haiku-5-5`, 720 conversations, run after the main experiment and before the freeze. It does not change EXP_C_PLAN.md. Driver stages `msmoke` and `M` and `src/analyze_exp_c_models.py` (tested on synthetic data) were added in the same commit. The C stage's run order is unchanged (the new stage uses its own seed).
- **Main experiment finished (2026-11-15, 3:13 PM ET).** Pass 1 (900 C1) and pass 2 (1,080 C2) completed with 0 failures; the ledger matched the event stream in 1,980 of 1,980. Outcomes were first viewed after both passes finished, by running `src/analyze_exp_c.py` unchanged.
- **Email redaction.** In 35 of 1,980 conversations the model wrote the account email (the CLI's constant reminder) into the order note, usually as the ordering user. It is replaced with `[REDACTED_EMAIL]` in results.csv, logs and ledgers, and the local home path and username with `[HOME]` and `[USER]`, before committing. Outcomes are unaffected (the analysis was re-run after redaction and gives the same numbers).
- **Logistic regressions not reported.** Both secondary logistic regressions (2x2 titles; title x message) failed to converge because several cells are at 0% or 100% (perfect separation). The plan says they are then not reported.
- **Model addendum finished (2026-11-15, 3:35 PM ET).** 720 of 720, 0 failures, requested model equals the model used in all 720, ledger matched in all 720. Analysed with `src/analyze_exp_c_models.py` unchanged. The model x title logistic regression did not converge (cells at 0%: every ceo cell) and is not reported, per the addendum. In 11 of 720 conversations the model wrote the account email into the order note (redacted, with local paths).
- **Say-vs-do regex undercounts for Opus.** The preliminary regex finds an over-maximum statement in 60 of 99 Opus final replies but 92 of 99 Opus order notes. Reading a sample of the misses shows phrasings the regex does not match ("twice the labeled maximum", "5 times the 10 mg/day maximum", "about twice the usual maximum"). The Opus reply figure is a lower bound. The regex was not changed.
- **File moves after the runs (no change to any pre-registered file).** The say-vs-do regex that EXP_C_PLAN.md refers to as the `hackathons` script `part1_extra_stats.py` now lives in this repo as `src/part1_extra_stats.py` (same regex). The report draft, claims ledger and status note were added under `report/`, and Experiment C figures under `data/outputs/exp_c/figures/` (`src/make_exp_c_figures.py`).
