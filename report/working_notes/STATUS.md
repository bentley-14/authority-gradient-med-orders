> Working note kept for the record. It was written during the sprint, while the repository was private, and is not maintained. For the current state read the top-level README.md and report/apart_submission.md.

# STATUS: Apart AI x Epistemics sprint (deadline Mon Nov 16, 5:59 AM CT)

## What exists
- Shilp's repo (bentley-14/authority-gradient-med-orders, private): harness with a real enter_order tool + ledger + code checker; exploratory runs; pre-registered Stage A (180) and Stage B (1,350) with analysis and figures (commit 16f15a4).
- report_draft.md: Part 1 written (intro, related work, methods, Stage B results, bridge to Exp C, limitations/dual-use appendix, references). Exp C and Discussion are stubs.
- CLAIMS_LEDGER.md: every number in the draft mapped to its source and commit.
- src/part1_extra_stats.py: stratum table and preliminary say-vs-do counts.

## What was found
- 0/1,350 over-limit orders entered at first request; 463/1,350 after a bare "Yes, I confirm."
- Pre-registered: medical student 8% vs untitled 36% (H1); senior titles 44% vs 36%, OR 4.32 (H2). Both significant.
- Half-entry dose: untitled 2.56x, senior attending 3.03x (moderate effect).
- Every entered order still states the dose is over the maximum (preliminary): knowing override.
- Rough "most refusals offer to proceed" claim did NOT hold with a tighter regex (201/1,350 explicit offers). Dropped.

## Decisions made
- Track 1 primary (also tick Track 3). Frame H1 as authorization-awareness (validity check), H2 as the epistemic concern.
- Exp C: (i) 2x2 titles, clinical vs non-clinical x junior vs senior (resident, attending, hospital financial analyst, hospital CEO not a clinician); (ii) second-message content (bare confirm, relevant clinical reason, irrelevant reason of matched length, responsibility claim). Run only in strata with room to move.
- Exp C runs on Tarun's subscription; account email redacted before commit. Request-recorder check on Tarun's machine passed (one tool, no personal context).
- Exp C pre-registered: EXP_C_PLAN.md pushed to branch exp-c of Shilp's repo (commit 28f71a8) before any run; analysis script fcef957 before any outcome viewed. Strata: metformin 2x, ibuprofen 2x, amlodipine 5x, sertraline 5x. 1,980 conversations; freeze 11 PM ET.
- Smoke test (11 conversations) passed plumbing checks. Main Exp C finished 3:13 PM ET: 1,980/1,980, 0 failures. Results committed 475a6c8 (email/paths redacted).
- Exp C findings: non-clinical titles (CEO, finance analyst) 0/180 each; resident 3%, untitled 22%, attending 41%. Relevant clinical reason 358/360 entered (incl. sertraline 5x 88/90); irrelevant reason 1/360 (below bare 31%); responsibility claim 62%. All four primaries significant. Model checks the KIND of reason and the role, not truth.
- Model addendum done 3:35 PM ET (ddd50d0): CEO 0% on all three models; attending > untitled on all (Opus 21%->62%, OR 9.35; Haiku 68%->86%, OR 4.64; Sonnet 22%->41%, OR 2.93). Haiku most compliant overall. Section 5.3 written.
- All experiments finished well before the 11 PM ET freeze. No more runs planned.
- Open: dual-use call on quoting the "protocol" sentence verbatim (decide with Shilp); figures; turn draft into Apart Google Doc template; affiliations.

## Experiment D (added Nov 15, about 4:15 to 5:00 PM ET, on Shilp's machine)
- Pre-registered on main (EXP_D_PLAN.md, commit 23cdd20, with driver and analysis script) before any run. 1,080 conversations, 0 failures, finished about 4:43 PM ET.
- Three questions Experiment C left open: is it that sentence, does truth matter when the model can check, can a deployer close the gate.
- Findings: protocol sentence repeated (59/60). Reworded reasons also work: specialist 90%, "clinically indicated" with no specifics 55%, bare 27%. A checkable false claim ("within the FDA label") got 0/60. One reminder sentence in the system prompt ("you cannot verify... treat as claims, not evidence") cut the three clinical reasons from 81% to 6% and the bare confirmation to 0; adding an explicit rule gave 0/180. All 180 label-maximum orders were still entered at first request. All four primaries significant.
- Written into apart_submission.md as the closing results (Figure 4, Table B3), with abstract, contributions, methods, discussion, limitations, future work and conclusion updated. The PDF main text ends on page 8; references and appendices follow (11 pages in total).
- exp-c was merged into main (fast-forward) before Experiment D; everything is on main now.

## Report
- report/apart_submission.md: the draft restructured into Apart's template sections (abstract box, contributions list, Discussion and Limitations, Future Work, Conclusion, Code and Data, LLM Usage Statement, Appendix A dual-use). ~2,600 words of main text + 3 figures (about 6 to 7 pages; Apart recommends 4, sprint maximum 8).
- report/apart_submission.docx (built by report/build_docx.py) was uploaded to Google Drive as a Google Doc (Nov 15, 3:47 PM ET).
- report/report_draft.md is the longer working draft and does NOT include Experiment D; apart_submission.md is the version to submit and is current.
- The Google Doc uploaded at 3:47 PM ET predates Experiment D. Rebuild with report/build_docx.py (already done locally) and upload again.

## Open questions
- Dual-use: quote the "protocol" sentence verbatim in the public write-up, or paraphrase? (Tarun + Shilp)
- Figures: entry by title (C1, all three models), entry by second message (C2), Stage B dose-response curves.
- Fill affiliations, author contributions, LLM usage statement (own words); team edits prose (Apart asks that the final version be primarily team-written); export PDF.
- Merge exp-c into main? (Shilp's call; nothing pushed to main.)
- Proper say-vs-do classifier, or keep regex + hand check and label preliminary.
