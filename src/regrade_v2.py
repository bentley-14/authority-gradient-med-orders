"""Regrades the existing responses with grader v2 using three graders, then
writes data/outputs/results_v2.csv. Does not call the responder and does not
touch results.csv. Resumable: a (trial, grader) pair with a log file is skipped.

Usage: python3 src/regrade_v2.py
"""
import csv
import json
import os
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from environment.isolated_claude import resolved_model
from src.agents import grader_v2
from src.experiment_hub.hub import appropriate

GRADERS = ["opus", "sonnet", "haiku"]
EFFORT = "medium"
WORKERS = 6


def log_path(row, grader):
    return os.path.join(os.path.dirname(row["responder_log"]),
                        "%s_grader_v2_%s.json" % (row["trial_id"], grader))


def grade_one(row, title_free, grader):
    path = os.path.join(ROOT, log_path(row, grader))
    if os.path.exists(path):
        return
    answers, score, error, calls = grader_v2.grade(title_free, row["response"], grader, EFFORT)
    with open(path, "w") as f:
        json.dump({"calls": calls, "answers": answers, "score": score, "error": error,
                   "grader_model": resolved_model(calls[-1]["raw_output"]), "effort": EFFORT},
                  f, indent=1)
    print(row["trial_id"], grader, score, error, flush=True)


def combine(scores):
    """Median of the available scores. Blank unless a clear median exists."""
    s = [x for x in scores if x is not None]
    if len(s) == 3 or (len(s) == 2 and s[0] == s[1]):
        return int(statistics.median(s))
    return None


def main():
    with open(os.path.join(ROOT, "data/outputs/results.csv")) as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(ROOT, "data/inputs/prompts.csv")) as f:
        title_free = {p["prompt_id"]: p["title_free_prompt"] for p in csv.DictReader(f)}

    with ThreadPoolExecutor(WORKERS) as pool:
        jobs = [pool.submit(grade_one, r, title_free[r["trial_id"].rsplit("_r", 1)[0]], g)
                for r in rows for g in GRADERS]
        failures = [j.exception() for j in jobs if j.exception()]
    if failures:
        print("%d grader calls failed, rerun to resume: %s" % (len(failures), failures[0]))
        return

    out = []
    for r in rows:
        new = {k: v for k, v in r.items() if k not in ("pushback_score", "appropriate")}
        new["pushback_score_v1"] = r["pushback_score"]
        new["appropriate_v1"] = r["appropriate"]
        scores, errors = [], []
        for g in GRADERS:
            with open(os.path.join(ROOT, log_path(r, g))) as f:
                log = json.load(f)
            a = log["answers"] or {}
            for k in grader_v2.FLAGS:
                new["%s_%s" % (g, k)] = a.get(k, "")
            new["%s_score" % g] = "" if log["score"] is None else log["score"]
            # dashes in a grader reason are written as hyphens here; the log keeps the raw text
            new["%s_reason" % g] = a.get("reason", "").replace("\u2013", "-").replace("\u2014", "-")
            new["%s_model" % g] = log["grader_model"]
            new["%s_log" % g] = log_path(r, g)
            scores.append(log["score"])
            if log["error"]:
                errors.append("%s: %s" % (g, log["error"]))
        final = combine(scores)
        new["pushback_score_v2"] = "" if final is None else final
        new["appropriate_v2"] = appropriate(r["severity"], final)
        new["n_graders_agreeing"] = "" if final is None else sum(s == final for s in scores)
        new["error_v2"] = "; ".join(errors)
        out.append(new)
    with open(os.path.join(ROOT, "data/outputs/results_v2.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote results_v2.csv with %d rows" % len(out))


if __name__ == "__main__":
    main()
