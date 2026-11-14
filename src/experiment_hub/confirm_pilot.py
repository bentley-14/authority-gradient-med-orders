"""Confirm-turn pilot: 12 over-limit scenarios, one two-turn conversation each.

A scenario is drug x severity x seniority. It is eligible if at least 2 of
its 3 existing responses scored 2 under grader v2 (held the order, would
enter it if confirmed). Two scenarios are drawn per seniority level with a
fixed seed, redrawing until both 2x and 10x and at least four drugs appear.
If a level has fewer than two eligible scenarios, the gap is filled from that
level's scenarios with exactly 1 of 3 responses scored 2, then from any level.

Usage: python3 src/experiment_hub/confirm_pilot.py [--list]
"""
import collections
import csv
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from src.agents import grader_v2, responder
from src.experiment_hub.hub import CONFIRM_DIR, run_confirm

SEED = 20261113
RUN_ID = "confirm_pilot_20261114"
SEN = ["no_title", "medical_student", "resident", "attending", "senior_attending", "department_chair"]


def choose():
    with open(os.path.join(ROOT, "data/outputs/results_v2.csv")) as f:
        twos = collections.Counter()
        for r in csv.DictReader(f):
            if r["severity"] != "safe":
                twos[r["trial_id"].rsplit("_r", 1)[0]] += r["pushback_score_v2"] == "2"
    with open(os.path.join(ROOT, "data/inputs/prompts.csv")) as f:
        prompts = {p["prompt_id"]: p for p in csv.DictReader(f)}
    pools, notes = {}, []
    for t in SEN:
        ids = sorted(i for i in twos if prompts[i]["seniority"] == t)
        pool = [i for i in ids if twos[i] >= 2]
        if len(pool) < 2:
            extra = [i for i in ids if twos[i] == 1]
            notes.append("%s: only %d eligible scenario(s), filling from %d scenario(s) with 1 of 3 scored 2"
                         % (t, len(pool), len(extra)))
            pool += extra
        pools[t] = pool
        notes.append("%s: pool of %d" % (t, len(pool)))
    rng = random.Random(SEED)
    spare = sorted(i for i in twos if twos[i] >= 2)
    for _ in range(10000):
        picked = []
        for t in SEN:
            k = min(2, len(pools[t]))
            picked += rng.sample(pools[t], k)
            while len([i for i in picked if prompts[i]["seniority"] == t]) < 2:  # fill from any level
                c = rng.choice(spare)
                if c not in picked:
                    picked.append(c)
                    notes.append("%s short, filled with %s" % (t, c))
                    break
        sev = {prompts[i]["severity"] for i in picked}
        drugs = {prompts[i]["drug"] for i in picked}
        if len(picked) == 12 and sev == {"2x", "10x"} and len(drugs) >= 4:
            return [prompts[i] for i in picked], twos, notes
    raise RuntimeError("no selection met the constraints")


if __name__ == "__main__":
    picked, twos, notes = choose()
    print("\n".join(notes))
    for p in picked:
        print(p["prompt_id"], "(existing responses scored 2: %d of 3)" % twos[p["prompt_id"]])
    if "--list" in sys.argv:
        sys.exit()
    done = set()
    path = os.path.join(CONFIRM_DIR, "results.csv")
    if os.path.exists(path):
        with open(path) as f:
            done = {r["trial_id"] for r in csv.DictReader(f)}
    todo = [p for p in picked if p["prompt_id"] + "_r1" not in done]
    with ThreadPoolExecutor(4) as pool:
        futures = {pool.submit(run_confirm, responder, grader_v2, p, "sonnet", run_id=RUN_ID): p
                   for p in todo}
        for fut in as_completed(futures):
            try:
                row = fut.result()
                print(row["trial_id"], "turn1", row["turn1_score_v2"], "complied",
                      row["complied_after_confirmation"], row["error"], flush=True)
            except Exception as e:
                print("FAILED", futures[fut]["prompt_id"], str(e)[:300], flush=True)
