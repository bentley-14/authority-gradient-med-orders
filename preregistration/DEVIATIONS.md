# Deviations from CONFIRMATORY_PLAN.md

This file logs every change to, or departure from, the pre-registered plan, with the time and the reason. It also records choices the plan left open, with the time they were fixed, so that a reader can see they were made before the Stage B data existed.

## Deviations

None so far.

## Status notes

- 2026-11-14, after Stage A finished: Stage B has not been started. The user put a usage cap on the account and asked for work to stop after Stage A. No Stage B conversation has been run and no Stage B data exists. The Stage B inputs (`data/inputs/prompts_confirmatory.csv`), driver, analysis script and figure script were prepared without any model call. The figure layout was tried on Stage A data, with the images saved outside the repo.

## Choices the plan left open, fixed before any Stage B conversation was run

Fixed 2026-11-14 08:50 EST, while Stage A was still running and before Stage B was started. This file was committed together with Stage A, before the Stage B run.

1. **Continuity correction.** The plan says "Cochran-Mantel-Haenszel test" without saying whether the chi-square uses the continuity correction. The primary p-value for H1 and H2 uses the continuity-corrected statistic (the more conservative of the two and the default of R's `mantelhaen.test`). The uncorrected statistic and p-value are reported beside it.
2. **H2 grouping.** Attending, senior attending and department chair conversations are pooled into one group and compared with no title within each drug x dose stratum, as the plan's wording says.
3. **Non-informative strata.** A drug x dose stratum is dropped from a test when, among the two groups being compared, nobody or everybody entered the order. Dropped strata are listed in the output.
4. **Odds ratio at the boundary.** If the Mantel-Haenszel odds ratio is 0 or infinite, the Robins-Breslow-Greenland interval does not exist and is reported as not estimable. The test p-value is still reported.
5. **Half-entry dose.** From the logistic regression of entry on log dose, title and drug, the half-entry dose for a title is exp(-(intercept + title effect + average drug effect) / log-dose coefficient), where the average is taken with equal weight over the drugs kept in the regression. If the regression does not fit cleanly (for example perfect separation), no half-entry doses are reported.
6. **Trend test.** The linear trend across the five titled ranks is a logistic regression of entry on rank (1 to 5) with a separate intercept for each informative drug x dose stratum. The untitled user is not in it.
7. **Run order.** The Stage B conversations are run in a shuffled order (fixed seed 20261114), so that time of day is not tied to drug or title. The Stage B driver prints progress counts only, no outcomes.
8. **Failures.** A conversation is attempted once and retried up to 3 times (waits of 30, 120 and 300 seconds). If a usage limit stops the run, the driver is run again later and tries only the conversations not yet in results.csv. Conversations still failing are listed in `failed.csv` and counted as missing.

## Notes added during the Stage B run

- **Batched running (2026-11-14).** Because of an account usage cap, Stage B is run in passes of 270 conversations using an optional pass-size argument added to `dose_driver.py`. The total stays 1,350, the order is still shuffled with the fixed seed, and no trials are added or dropped based on results.
- **Interim look (2026-11-14, at 176 of 1,350 conversations).** At the user's request, entry counts were viewed by dose and by drug only. Counts by title were not viewed, no test was run, and no design decision was made from the look. This departs from the plan's "no looking at results part-way".
- **Email redaction (2026-11-14, after the run).** In 2 of 1,350 conversations the model wrote the account email address (which the CLI injects as a constant reminder) into the order note. The address was replaced with [REDACTED_EMAIL] in results.csv and in those two conversations' ledger and log files before committing. Outcomes are unaffected.
