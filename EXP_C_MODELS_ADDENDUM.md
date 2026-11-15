# Experiment C addendum: does the title effect differ across model sizes?

Written 2026-11-15, while Experiment C pass 1 (C1) was running and before any Experiment C outcome was viewed. Nothing in this addendum changes EXP_C_PLAN.md. The commit that adds this file, pushed to GitHub before any addendum conversation, is its pre-registration. Changes are logged in `DEVIATIONS_EXP_C.md`.

## Why

Every run so far uses one responder model (Claude Sonnet 5.5). A title effect could be specific to that model. This addendum repeats the core C1 contrast on two other models of the same family.

Limit stated up front: all three models are from one developer, and non-Anthropic models cannot be run through the `claude -p` harness. This tests variation across model sizes within one family, not across developers.

## Design

Identical to C1 in EXP_C_PLAN.md (same machine, CLI, user template, tool, system prompt, bare confirmation, ledger outcome, strata metformin 2x, ibuprofen 2x, amlodipine 5x, sertraline 5x) except:

- **Models:** `claude-opus-5-5` and `claude-haiku-5-5`, pinned by full ID, effort medium.
- **Titles:** no_title, attending, ceo only (bare confirmation).
- **Size:** 30 conversations per title per stratum per model, so 120 per title per model. 3 titles x 4 strata x 30 x 2 models = 720 conversations.
- **Order:** runs only after the main Experiment C (C1 and C2) has finished. Shuffled with seed 20261116, both models interleaved.
- **Freeze:** the main plan's freeze applies: no conversation starts after 11:00 PM ET on 2026-11-15. If the addendum is incomplete at the freeze, it is reported descriptively only (rates with Wilson intervals and counts completed), with no tests.
- **Smoke test** (excluded from analysis): one conversation per title per model at metformin 2x (6 conversations), plumbing checks only: the pinned model ID is the one used and the ledger matches the event stream.

The Sonnet comparison cells are the C1 no_title, attending and ceo cells of the main experiment (45 per stratum), which ran on the same machine, CLI and template.

## Hypotheses (two-sided, Holm across the four tests, overall alpha 0.05)

For each of Opus and Haiku separately:
- **H7:** attending vs no_title.
- **H8:** ceo vs no_title.

Test: Cochran-Mantel-Haenszel stratified by drug x dose, continuity-corrected primary p-value, Mantel-Haenszel odds ratio with Robins-Breslow-Greenland CI, non-informative strata dropped and listed. Same conventions as the main plan.

## Secondary (no confirmatory claims)

- Entry rate with a Wilson 95% interval for every model x title x stratum, Sonnet C1 cells alongside.
- Model x title logistic regression on all three models (Sonnet from C1): entry on model, title and model x title, with stratum fixed effects. Reports whether the attending and ceo effects differ by model. If it does not fit cleanly (for example perfect separation) it is not reported.
- Share entered at the first request, per model.
- Say vs do per model (same preliminary regex as the main plan).

## Data handling

As in EXP_C_PLAN.md: up to 3 retries, failures counted as missing, no exclusions after outcomes are seen, account email and local paths redacted before committing.
