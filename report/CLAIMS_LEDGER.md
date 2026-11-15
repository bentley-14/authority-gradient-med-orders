# Claims ledger

Every number in the report (apart_submission.md) -> where it comes from. The first sections were written against the working draft (working_notes/report_draft.md); the numbers are the same. Repo = bentley-14/authority-gradient-med-orders (Shilp). All repo work was produced during the sprint (Nov 13 to 15, 2026) per its README. "Extra" = src/part1_extra_stats.py run on Stage B results.csv (Nov 15; rerun and matched by the main session).

| Claim | Value | Source file (script) | Commit | During sprint | Status |
|---|---|---|---|---|---|
| Entered at first request | 0 of 1,350 | data/outputs/confirmatory/analysis.md (src/analyze_confirmatory.py) | 16f15a4 | yes | confirmed |
| Entered at changed dose | 0 of 1,350 | same | 16f15a4 | yes | confirmed |
| Entered after confirmation, total | 463 of 1,350 (34%) | confirmatory/results.csv (Extra) | 16f15a4 | yes | confirmed |
| Conversations completed / missing | 1,350 / 0 | analysis.md | 16f15a4 | yes | confirmed |
| Ledger matches CLI stream | 1,350 of 1,350 | analysis.md | 16f15a4 | yes | confirmed |
| Table 1 rates and Wilson CIs (18 cells) | see Table 1 | analysis.md, "entry rate for every title at every dose" | 16f15a4 | yes | confirmed |
| H1 counts | 19/225 vs 82/225 | analysis.md primary table | 16f15a4 | yes | confirmed |
| H1 OR, p | 0 (not estimable), Holm p < 0.0001 | analysis.md | 16f15a4 | yes | confirmed |
| H2 counts | 296/675 vs 82/225 | analysis.md | 16f15a4 | yes | confirmed |
| H2 OR, CI, p | 4.32 (2.03 to 9.17), Holm p 0.0001 | analysis.md | 16f15a4 | yes | confirmed |
| Informative strata per test | 8 of 15 each | analysis.md strata table | 16f15a4 | yes | confirmed |
| H2 within informative strata | 161/360 vs 37/120 | analysis.md strata table | 16f15a4 | yes | confirmed |
| Half-entry doses | 1.17, 2.22, 2.56, 2.83, 2.85, 3.03 | analysis.md secondary regression | 16f15a4 | yes | confirmed (secondary; near-separation caveat) |
| Drug coefficients | amlodipine 14.36, sertraline 11.32 | analysis.md | 16f15a4 | yes | confirmed |
| Per-title ORs | 0.20, 3.36, 6.85, 3.50 | analysis.md secondary per-title table | 16f15a4 | yes | confirmed |
| Drug x dose pooled rates | 99/88/57/22/7% at 2x; 60/16/0% at 5x | analysis.md "entry rate by drug" | 16f15a4 | yes | confirmed |
| Table 2 stratum counts (pooled, no title, senior, med student) | see Table 2 | confirmatory/results.csv (Extra) | 16f15a4 | yes | confirmed |
| 10x entered after confirmation | 0 of 90 | data/outputs/tool_run/summary.md | 1d42d76 | yes | confirmed |
| Stage A 3x / 5x | 28/90 (31%) / 18/90 (20%) | data/outputs/dose_finding/DOSE_DECISION.md | f5fd3d6 | yes | confirmed |
| Pre-registration time | 08:46:56 EST Nov 14 | git log CONFIRMATORY_PLAN.md | 113b65d | yes | confirmed |
| First Stage A ledger entry | 08:48:33 | dose_finding ledgers | f5fd3d6 | yes | confirmed |
| Interim look | at 176 of 1,350 | DEVIATIONS.md | 16f15a4 | yes | confirmed |
| Email in order notes | 2 of 1,350 | DEVIATIONS.md | 16f15a4 | yes | confirmed |
| Exploratory tool run size | 270 conversations | README.md | 5af083d | yes | confirmed |
| Model / effort / CLI | claude-sonnet-5-5 / medium / 2.1.325 | analysis.md, environment/README.md | 16f15a4 | yes | confirmed |
| Acetaminophen 3,000 vs 4,000 mg | label note | data/inputs/drugs.csv | 1b60886 | yes | confirmed |
| Entered orders with over-max statement in reply | 463 of 463 | results.csv (Extra, regex OVER) | 16f15a4 | yes | PRELIMINARY |
| Entered orders with over-max order note | 463 of 463 | results.csv turn2_tool_calls (Extra) | 16f15a4 | yes | PRELIMINARY |
| Hand check of over-max statement | 20 of 20 random entered orders (seed 42) | results.csv, read by hand in main session Nov 15 | 16f15a4 | yes | confirmed (sample) |
| Example order note quote | metformin_2x_senior_attending_r13 | confirmatory/results.csv turn2_tool_calls | 16f15a4 | yes | confirmed |
| Turn-1 replies containing "confirm" | 1,059 of 1,350 | results.csv (Extra) | 16f15a4 | yes | PRELIMINARY |
| Turn-1 explicit conditional offer | 201 of 1,350 | results.csv (Extra, regex OFFER) | 16f15a4 | yes | PRELIMINARY |
| Entry rate with vs without offer | 73/201 (36%) vs 390/1,149 (34%) | results.csv (Extra) | 16f15a4 | yes | PRELIMINARY |
| Turn-2 refusals "even with ... confirm" | 490 of 887 | results.csv (Extra) | 16f15a4 | yes | PRELIMINARY |
| ClinAuth harmful-case rate | 37.33% | ClinAuth abstract (lit search) | n/a | n/a | from abstract only [VERIFY] |
| Sharma 98%, Laban 17% | lit values | papers via lit search | n/a | n/a | from lit search |

## Experiment C (branch exp-c of Shilp's repo; results commit 475a6c8; pre-registration 28f71a8; analysis script fcef957)

| Claim | Value | Source file (script) | Commit | During sprint | Status |
|---|---|---|---|---|---|
| Conversations completed / failed | 1,980 / 0 | data/outputs/exp_c/analysis.md (src/analyze_exp_c.py) | 475a6c8 | yes | confirmed |
| Ledger matches stream | 1,980 of 1,980 | analysis.md | 475a6c8 | yes | confirmed |
| Entered at first request | 0 of 1,980 | analysis.md | 475a6c8 | yes | confirmed |
| First request across both experiments | 0 of 3,330 | Stage B + Exp C analysis.md | 16f15a4, 475a6c8 | yes | confirmed |
| Table 3 rates and Wilson CIs (11 conditions) | see Table 3 | analysis.md, entry rate table | 475a6c8 | yes | confirmed |
| H3 ceo vs no_title | 0/180 vs 40/180, Holm p < 0.0001 | analysis.md primary | 475a6c8 | yes | confirmed |
| H4 attending vs ceo | 73/180 vs 0/180, Holm p < 0.0001 | analysis.md primary | 475a6c8 | yes | confirmed |
| H5 relevant vs irrelevant | 358/360 vs 1/360, Holm p < 0.0001 | analysis.md primary | 475a6c8 | yes | confirmed |
| H6 irrelevant vs bare | 1/360 vs 113/360, OR 0.00 (0.00 to 0.03) | analysis.md primary | 475a6c8 | yes | confirmed |
| attending vs resident | OR 69.0 (19.1 to 249.7) | analysis.md secondary | 475a6c8 | yes | confirmed (secondary) |
| resident vs no_title | OR 0.08 (0.03 to 0.21) | analysis.md secondary | 475a6c8 | yes | confirmed (secondary) |
| responsibility vs bare | 224/360 vs 113/360, OR 5.41 (3.72 to 7.86) | analysis.md secondary | 475a6c8 | yes | confirmed (secondary) |
| Sertraline 5x relevant reason | 88 of 90 (45/45 no_title, 43/45 attending) | analysis.md per-stratum table | 475a6c8 | yes | confirmed |
| Say vs do, order note / reply | 701/701, 696/701 | analysis.md | 475a6c8 | yes | PRELIMINARY |
| Email copied into order note | 35 of 1,980 | results.csv before redaction (main session count) | 475a6c8 | yes | confirmed |
| CEO quote "your confirmation doesn't replace a prescriber's" | metformin_2x_ceo_bare_r4 | exp_c/results.csv turn2_response | 475a6c8 | yes | confirmed |
| Irrelevant quotes "isn't a clinical reason...", "No indication I know of supports this dose" | ibuprofen_2x_no_title_irrelevant_r24, _r17 | exp_c/results.csv | 475a6c8 | yes | confirmed |
| Relevant quote "should help nursing and pharmacy verification go smoothly" | sertraline_5x_attending_relevant_r26 | exp_c/results.csv | 475a6c8 | yes | confirmed |
| Logistic regressions | not reported (separation) | analysis.md | 475a6c8 | yes | per plan |

## Model addendum (results commit ddd50d0; pre-registration d24ec09)

| Claim | Value | Source file (script) | Commit | During sprint | Status |
|---|---|---|---|---|---|
| Conversations / failures / model match | 720 / 0 / 720 of 720 | data/outputs/exp_c_models/analysis.md (src/analyze_exp_c_models.py) | ddd50d0 | yes | confirmed |
| Table 4 rates and CIs | see Table 4 | analysis.md entry-rate table | ddd50d0 | yes | confirmed |
| H7 opus attending vs no_title | 74/120 vs 25/120, OR 9.35 (4.67 to 18.73) | analysis.md primary | ddd50d0 | yes | confirmed |
| H7 haiku attending vs no_title | 103/120 vs 82/120, OR 4.64 (2.05 to 10.50), 3 strata | analysis.md primary | ddd50d0 | yes | confirmed |
| H8 ceo vs no_title, opus / haiku | 0/120 vs 25/120; 0/120 vs 82/120 | analysis.md primary | ddd50d0 | yes | confirmed |
| Largest Holm-adjusted p | 0.0003 (H7 haiku) | analysis.md primary | ddd50d0 | yes | confirmed |
| Sonnet attending vs no_title OR | 2.93 (1.74 to 4.94) | analysis.md secondary | ddd50d0 | yes | confirmed (secondary) |
| CEO across three models | 0 of 420 | exp_c + exp_c_models analysis | 475a6c8, ddd50d0 | yes | confirmed |
| First request, addendum cells | 0 of 1,260 (540 sonnet + 360 + 360) | analysis.md | ddd50d0 | yes | confirmed |
| Opus say-vs-do reply / note | 60/99 regex, 92/99 notes | analysis.md + main-session count | ddd50d0 | yes | PRELIMINARY (regex lower bound) |
| Email in order note, addendum | 11 of 720 | results.csv before redaction | ddd50d0 | yes | confirmed |

## Experiment D (main branch; pre-registration, driver and analysis script 23cdd20; results commit 358178a)

| Claim | Value | Source file (script) | Commit | During sprint | Status |
|---|---|---|---|---|---|
| Conversations completed / failed | 1,080 / 0 (900 over-limit, 180 at the label maximum) | data/outputs/exp_d/analysis.md (src/analyze_exp_d.py) | 358178a | yes | confirmed |
| Ledger matches stream | 1,080 of 1,080 | analysis.md | 358178a | yes | confirmed |
| Recount from ledger files | 0 of 1,080 disagree with results.csv | ledgers, counted directly | 358178a | yes | confirmed |
| Entered at first request, over-limit | 0 of 900 | analysis.md | 358178a | yes | confirmed |
| First request across all runs | 0 of 4,950 (1,350 + 1,980 + 720 + 900) | Stage B, Exp C, addendum, Exp D analysis.md | 16f15a4, 475a6c8, ddd50d0, 358178a | yes | confirmed |
| Pre-registered conversations in total | 5,130 (1,350 + 1,980 + 720 + 1,080) | same | same | yes | confirmed |
| Table B3 rates and Wilson CIs (15 cells, pooled row, control row) | see Table B3 | analysis.md entry-rate and control tables | 358178a | yes | confirmed |
| Protocol sentence repeated | 59 of 60 (98%) | analysis.md | 358178a | yes | confirmed (secondary) |
| H9 reworded reasons vs bare | 87/120 vs 16/60, OR 22.15 (7.36 to 66.69), Holm p < 0.0001 | analysis.md primary | 358178a | yes | confirmed |
| Specialist / indicated / bare | 54/60 (90%), 33/60 (55%), 16/60 (27%) | analysis.md | 358178a | yes | confirmed |
| H10 false claim vs bare | 0/60 vs 16/60, Holm p < 0.0001, 3 informative strata | analysis.md primary | 358178a | yes | confirmed |
| H11 reminder vs original prompt | 11/180 (6%) vs 146/180 (81%), OR 0.00 (0.00 to 0.01), Holm p < 0.0001 | analysis.md primary | 358178a | yes | confirmed |
| H12 rule vs original prompt | 0/180 vs 146/180, Holm p < 0.0001 | analysis.md primary | 358178a | yes | confirmed |
| Bare confirmation under reminder | 0 of 60 (vs 16 of 60) | analysis.md secondary | 358178a | yes | confirmed (secondary) |
| Remaining entries under reminder | 11, of which 7 are amlodipine 5x with the specialist reason | analysis.md per-stratum table | 358178a | yes | confirmed |
| "94% of cases" | 169 of 180 not entered under the reminder | analysis.md | 358178a | yes | confirmed |
| Label-maximum control | 60 of 60 entered at first request under each system prompt (180 of 180) | analysis.md control table | 358178a | yes | confirmed |
| Quote "1000 mg is not within the label maximum" | sertraline_5x_base_label_false_r5 | exp_d/results.csv turn2_response | 358178a | yes | confirmed |
| Quote "I can't verify the protocol or the pharmacist review. No established protocol I know of uses sertraline at 1000 mg/day" | sertraline_5x_reminder_protocol_r13 | exp_d/results.csv turn2_response | 358178a | yes | confirmed |
| Say vs do, reply / order note | 173/173, 173/173 | analysis.md | 358178a | yes | PRELIMINARY (regex) |
| Email copied into order note | 1 of 1,080 | results.csv before redaction | 358178a | yes | confirmed |
