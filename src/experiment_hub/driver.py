"""Loops over prompts.csv and calls run() for each trial. Resumable.

Usage:
  python3 src/experiment_hub/driver.py                 full run (90 prompts x 3 repeats)
  python3 src/experiment_hub/driver.py --pilot         6 trials only
  python3 src/experiment_hub/driver.py --run-id ID     reuse a run id when resuming
"""
import argparse
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from src.agents import grader_agent, responder
from src.experiment_hub.hub import RESULTS, run

RESPONDER_MODEL = "sonnet"
GRADER_MODEL = "opus"
EFFORT = "medium"
REPEATS = 3
WORKERS = 4
PILOT = ["ibuprofen_safe_no_title", "ibuprofen_safe_department_chair",
         "ibuprofen_10x_no_title", "ibuprofen_10x_department_chair",
         "sertraline_safe_department_chair", "sertraline_10x_medical_student"]

ap = argparse.ArgumentParser()
ap.add_argument("--pilot", action="store_true")
ap.add_argument("--run-id", default=time.strftime("run_%Y%m%d_%H%M%S"))
ap.add_argument("--responder-model", default=RESPONDER_MODEL)
ap.add_argument("--grader-model", default=GRADER_MODEL)
ap.add_argument("--effort", default=EFFORT)
args = ap.parse_args()

done = set()
if os.path.exists(RESULTS):
    with open(RESULTS) as f:
        done = {r["trial_id"] for r in csv.DictReader(f)}

with open(os.path.join(ROOT, "data/inputs/prompts.csv")) as f:
    prompts = list(csv.DictReader(f))

todo = []
for p in prompts:
    if args.pilot and p["prompt_id"] not in PILOT:
        continue
    for rep in ([1] if args.pilot else range(1, REPEATS + 1)):
        if "%s_r%d" % (p["prompt_id"], rep) not in done:
            todo.append((p, rep))
print("run_id %s: %d trials to do, %d already in results.csv" % (args.run_id, len(todo), len(done)))

failed = 0
with ThreadPoolExecutor(WORKERS) as pool:
    futures = {pool.submit(run, responder, grader_agent, p, args.responder_model,
                           args.grader_model, run_id=args.run_id, repeat=rep,
                           effort=args.effort): (p, rep) for p, rep in todo}
    for n, fut in enumerate(as_completed(futures), start=1):
        p, rep = futures[fut]
        try:
            row = fut.result()
            print("%d/%d %s score=%s %s" % (n, len(todo), row["trial_id"],
                                            row["pushback_score"], row["error"]), flush=True)
        except Exception as e:  # persistent CLI failure: stop, keep partial results
            failed += 1
            print("FAILED %s_r%d: %s" % (p["prompt_id"], rep, str(e)[:300]), flush=True)
            for other in futures:
                other.cancel()
print("finished. failed (not written, rerun with --run-id %s to resume): %d" % (args.run_id, failed))
