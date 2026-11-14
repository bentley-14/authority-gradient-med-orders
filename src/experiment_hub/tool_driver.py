"""Two-turn experiment with the enter_order tool. Loops over prompts.csv and
calls run_tool() for each conversation. Resumable.

Usage:
  python3 src/experiment_hub/tool_driver.py --smoke     6 conversations
  python3 src/experiment_hub/tool_driver.py             all 270 (90 prompts x 3 repeats)
"""
import argparse
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from src.agents import grader_v2, responder
from src.experiment_hub import hub

RESPONDER_MODEL = "sonnet"
EFFORT = "medium"
REPEATS = 3
WORKERS = 4  # each conversation also runs its three graders side by side
MULTIPLIER = {"safe": 1, "2x": 2, "10x": 10}
SMOKE = ["ibuprofen_safe_no_title", "sertraline_safe_department_chair",
         "amlodipine_2x_no_title", "metformin_2x_department_chair",
         "acetaminophen_10x_medical_student", "ibuprofen_10x_department_chair"]

ap = argparse.ArgumentParser()
ap.add_argument("--smoke", action="store_true")
ap.add_argument("--run-id", default="tool_run_20261114")
args = ap.parse_args()
if args.smoke:
    hub.TOOL_DIR = os.path.join(ROOT, "data/outputs/tool_run/smoke")
    args.run_id = "tool_smoke_20261114"
results = os.path.join(hub.TOOL_DIR, "results.csv")

with open(os.path.join(ROOT, "data/inputs/drugs.csv")) as f:
    drugs = {d["drug"]: d for d in csv.DictReader(f)}
with open(os.path.join(ROOT, "data/inputs/prompts.csv")) as f:
    prompts = list(csv.DictReader(f))


def requested(p):
    d = drugs[p["drug"]]
    return {"drug": p["drug"],
            "dose_mg": float(d["safe_dose_per_administration_mg"]) * MULTIPLIER[p["severity"]],
            "frequency_per_day": int(d["doses_per_day"])}


done = set()
if os.path.exists(results):
    with open(results) as f:
        done = {r["trial_id"] for r in csv.DictReader(f)}
todo = []
for p in prompts:
    if args.smoke and p["prompt_id"] not in SMOKE:
        continue
    for rep in ([1] if args.smoke else range(1, REPEATS + 1)):
        if "%s_r%d" % (p["prompt_id"], rep) not in done:
            todo.append((p, rep))
print("run_id %s: %d conversations to do, %d already done" % (args.run_id, len(todo), len(done)))

failed = 0
with ThreadPoolExecutor(WORKERS) as pool:
    futures = {pool.submit(hub.run_tool, responder, grader_v2, p, requested(p), RESPONDER_MODEL,
                           run_id=args.run_id, repeat=rep, effort=EFFORT): (p, rep)
               for p, rep in todo}
    for n, fut in enumerate(as_completed(futures), start=1):
        p, rep = futures[fut]
        try:
            row = fut.result()
            print("%d/%d %s turn1=%s turn2=%s final=%s %s" % (
                n, len(todo), row["trial_id"], row["turn1_outcome"], row["turn2_outcome"] or "none",
                row["final_outcome"], row["error"]), flush=True)
        except Exception as e:  # persistent failure: stop, keep partial results
            failed += 1
            print("FAILED %s_r%d: %s" % (p["prompt_id"], rep, str(e)[:300]), flush=True)
            for other in futures:
                other.cancel()
print("finished. failed (not written, rerun to resume): %d" % failed)
