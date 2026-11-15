# Deviations from EXP_D_PLAN.md

Every change to, or departure from, the Experiment D plan, with the time and the reason.

## Deviations

None so far.

## Notes fixed before any Experiment D conversation was run

- **Code changes (2026-11-15, about 4:40 PM ET).** `responder.respond_with_tool` takes an optional system prompt file, and `hub.run_tool` passes a prompt's own `system_file` when it has one and records the `system` label. Earlier runs are unaffected (the default file is unchanged).
- **Analysis script.** `src/analyze_exp_d.py` reuses the test functions of `src/analyze_exp_c.py`. It was run on synthetic data with a planted pattern before any Experiment D conversation existed, and it is committed with the plan.

## Notes added during the run
