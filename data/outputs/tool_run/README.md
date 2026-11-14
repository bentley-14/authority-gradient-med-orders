# Tool run outputs

Two-turn experiment in which the responder can call the `enter_order` tool (see `order_entry/README.md`). Run id `tool_run_20261114`.

- `results.csv`: one row per conversation. Both turns' visible reply text, the tool call arguments taken from the ledger, `turn1_outcome`, `turn2_outcome` and `final_outcome` (from the ledger and `order_entry/checker.py` only), the grader panel's answers, and the paths of the logs and the ledger.
- `summary.md`: the tables. Written by `src/summarize_tool_run.py`.
- `figures/`: written by `src/make_tool_figures.py`.
- `logs/tool_run_20261114/`: per conversation, `<trial_id>_responder.json` (the exact command, the user turns, and every raw CLI event of each turn, including tool calls and tool results) and one `<trial_id>_grader_<model>.json` per grader.
- `ledgers/tool_run_20261114/`: per conversation, the JSON-lines ledger written by the tool itself. An empty file means no call was made.
- `smoke/`: the 6-conversation smoke test run before the full run, same layout.

Column notes:

- `confirmation_sent` is "yes" when the order was not entered as written at turn 1, so the fixed confirmation was sent as turn 2.
- `ledger_matches_stream` compares the ledger with the tool calls seen in the CLI event stream.
- `judge_*` columns are the panel's majority answer (or median score). They are blank if one of the three graders gave no usable answer. Grader inputs contain only the visible reply text, never the tool calls or the ledger.
- En-dashes and em-dashes in model text are written as hyphens in the CSV. The logs keep the raw text.
