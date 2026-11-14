"""Drivers for CONFIRMATORY_PLAN.md. Same two-turn tool conversation as the
tool run (hub.run_tool), with no grader panel: outcomes come from the order
ledger and the checker only. Resumable.

Usage:
  python3 src/experiment_hub/dose_driver.py A     Stage A, dose finding (3x and 5x, 3 repeats)
  python3 src/experiment_hub/dose_driver.py B     Stage B, confirmatory (15 repeats)

A conversation is retried up to 3 times. If it still fails it is written to
failed.csv in the output folder and is not counted as "not entered".
Running the driver again tries the conversations that are not in results.csv.
"""
import csv
import os
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import environment.isolated_claude as isolated_claude
from src.agents import grader_v2, responder
from src.experiment_hub import hub

STAGES = {
    "A": {"prompts": "prompts_dose_finding.csv", "repeats": 3, "workers": 6,
          "out": "data/outputs/dose_finding", "run_id": "dose_finding_20261114"},
    "B": {"prompts": "prompts_confirmatory.csv", "repeats": 15, "workers": 6,
          "out": "data/outputs/confirmatory", "run_id": "confirmatory_20261114"},
}
stage = STAGES[sys.argv[1]]
hub.TOOL_DIR = os.path.join(ROOT, stage["out"])
isolated_claude.RETRY_WAITS = [30, 120, 300]  # 3 retries, as the plan says
results = os.path.join(hub.TOOL_DIR, "results.csv")
failed_path = os.path.join(hub.TOOL_DIR, "failed.csv")

with open(os.path.join(ROOT, "data/inputs/drugs.csv")) as f:
    drugs = {d["drug"]: d for d in csv.DictReader(f)}
with open(os.path.join(ROOT, "data/inputs", stage["prompts"])) as f:
    prompts = list(csv.DictReader(f))


def requested(p):
    d = drugs[p["drug"]]
    return {"drug": p["drug"],
            "dose_mg": float(d["safe_dose_per_administration_mg"]) * int(p["severity"].rstrip("x")),
            "frequency_per_day": int(d["doses_per_day"])}


done = set()
if os.path.exists(results):
    with open(results) as f:
        done = {r["trial_id"] for r in csv.DictReader(f)}
todo = [(p, rep) for p in prompts for rep in range(1, stage["repeats"] + 1)
        if "%s_r%d" % (p["prompt_id"], rep) not in done]
random.Random(20261114).shuffle(todo)  # run order is mixed so time is not tied to drug or title
print("run_id %s: %d conversations to do, %d already done" % (stage["run_id"], len(todo), len(done)))

lock, failed = threading.Lock(), 0
os.makedirs(hub.TOOL_DIR, exist_ok=True)
with ThreadPoolExecutor(stage["workers"]) as pool:
    futures = {pool.submit(hub.run_tool, responder, grader_v2, p, requested(p), "sonnet",
                           grader_models=[], run_id=stage["run_id"], repeat=rep,
                           effort="medium"): (p, rep) for p, rep in todo}
    for n, fut in enumerate(as_completed(futures), start=1):
        p, rep = futures[fut]
        try:
            row = fut.result()
            if n % 10 == 0 or n == len(todo):  # progress only, no outcomes are printed
                print("%d/%d done" % (n, len(todo)), flush=True)
        except Exception as e:
            failed += 1
            with lock, open(failed_path, "a", newline="") as f:
                csv.writer(f).writerow(["%s_r%d" % (p["prompt_id"], rep), str(e)[:500]])
            print("FAILED %s_r%d: %s" % (p["prompt_id"], rep, str(e)[:200]), flush=True)
print("finished. failed this pass: %d" % failed)
