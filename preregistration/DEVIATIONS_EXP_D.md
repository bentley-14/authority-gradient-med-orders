# Deviations from EXP_D_PLAN.md

Every change to, or departure from, the Experiment D plan, with the time and the reason.

## Deviations

None so far.

## Notes fixed before any Experiment D conversation was run

- **Code changes (2026-11-15, about 4:15 PM ET).** `responder.respond_with_tool` takes an optional system prompt file, and `hub.run_tool` passes a prompt's own `system_file` when it has one and records the `system` label. Earlier runs are unaffected (the default file is unchanged).
- **Analysis script.** `src/analyze_exp_d.py` reuses the test functions of `src/analyze_exp_c.py`. It was run on synthetic data with a planted pattern before any Experiment D conversation existed, and it is committed with the plan.

## Notes added during the run

- **Smoke test (2026-11-15, about 4:16 PM ET).** 18 of 18 conversations completed, ledger matched the event stream in all, model `claude-sonnet-5-5` in all, and each recorded command carried the system prompt its label names. The check script also printed the first-request outcome of the three label-maximum smoke conversations (all entered). No over-limit smoke outcome was viewed, and nothing was changed after the smoke test.
- **Main run finished (2026-11-15, about 4:43 PM ET).** One pass, 1,080 of 1,080, 0 failures, well before the 11:00 PM freeze. Outcomes were first viewed after the pass finished, by running `src/analyze_exp_d.py` unchanged from the pre-registration commit (23cdd20).
- **Independent recount.** Every outcome was recounted from the ledger files directly (not from results.csv): 0 of 1,080 disagreed.
- **Redaction.** In 1 of 1,080 conversations the model wrote the account email into the order note. It is replaced with `[REDACTED_EMAIL]`, and the local home path and username with `[HOME]` and `[USER]`, in results.csv, logs and ledgers (main run and smoke test) before committing. The analysis was re-run after redaction and is byte-identical.
- **Figure footnote.** `src/make_exp_d_figures.py` was written during the run and tried on synthetic data. Its footnote was corrected before any real outcome was plotted (the false label claim is the one reason the model can check).
