"""Driver for EXP_D_PLAN.md. Same two-turn tool conversation as Experiment C
(hub.run_tool), outcomes from the order ledger and the checker only. Resumable.

Usage:
  python3 src/experiment_hub/exp_d_driver.py smoke     18 conversations at metformin, plumbing check only
  python3 src/experiment_hub/exp_d_driver.py D [N]     Experiment D, 15 repeats (optional: at most N this pass)

All conversations run in one shuffled order (fixed seed 20261117). A
conversation is retried up to 3 times; if it still fails it goes to failed.csv
and is counted as missing, not as "not entered".
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

MODEL = "claude-sonnet-5-5"  # pinned full ID, as in Experiment C
STAGES = {
    "smoke": {"repeats": 1, "out": "data/outputs/exp_d/smoke", "run_id": "exp_d_smoke_20261115",
              "only_drug": "metformin"},
    "D": {"repeats": 15, "out": "data/outputs/exp_d", "run_id": "exp_d_20261115", "only_drug": None},
}
stage = STAGES[sys.argv[1]]
hub.TOOL_DIR = os.path.join(ROOT, stage["out"])
isolated_claude.RETRY_WAITS = [30, 120, 300]
results = os.path.join(hub.TOOL_DIR, "results.csv")
failed_path = os.path.join(hub.TOOL_DIR, "failed.csv")

with open(os.path.join(ROOT, "data/inputs/drugs.csv")) as f:
    drugs = {d["drug"]: d for d in csv.DictReader(f)}
with open(os.path.join(ROOT, "data/inputs/prompts_exp_d.csv")) as f:
    prompts = list(csv.DictReader(f))
if stage["only_drug"]:
    prompts = [p for p in prompts if p["drug"] == stage["only_drug"]]


def requested(p):
    d = drugs[p["drug"]]
    return {"drug": p["drug"],
            "dose_mg": float(d["safe_dose_per_administration_mg"]) * int(p["severity"].rstrip("x")),
            "frequency_per_day": int(d["doses_per_day"])}


done = set()
if os.path.exists(results):
    with open(results) as f:
        done = {r["trial_id"] for r in csv.DictReader(f)}
todo = [(p, rep) for p in prompts for rep in range(1, stage["repeats"] + 1)]
random.Random(20261117).shuffle(todo)
todo = [(p, rep) for p, rep in todo if "%s_r%d" % (p["prompt_id"], rep) not in done]
if len(sys.argv) > 2:  # optional cap on conversations for this pass
    todo = todo[:int(sys.argv[2])]
print("run_id %s: %d conversations to do, %d already done" % (stage["run_id"], len(todo), len(done)))

lock, failed = threading.Lock(), 0
os.makedirs(hub.TOOL_DIR, exist_ok=True)
with ThreadPoolExecutor(6) as pool:
    futures = {pool.submit(hub.run_tool, responder, grader_v2, p, requested(p), MODEL,
                           grader_models=[], run_id=stage["run_id"], repeat=rep,
                           effort="medium"): (p, rep) for p, rep in todo}
    for n, fut in enumerate(as_completed(futures), start=1):
        p, rep = futures[fut]
        try:
            fut.result()
            if n % 20 == 0 or n == len(todo):  # progress only, no outcomes are printed
                print("%d/%d done" % (n, len(todo)), flush=True)
        except Exception as e:
            failed += 1
            with lock, open(failed_path, "a", newline="") as f:
                csv.writer(f).writerow(["%s_r%d" % (p["prompt_id"], rep), str(e)[:500]])
            print("FAILED %s_r%d: %s" % (p["prompt_id"], rep, str(e)[:200]), flush=True)
print("finished. failed this pass: %d" % failed)
