"""Prints 10 randomly chosen rows (fixed seed) so a person can check the grader by eye."""
import csv
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "data/outputs/results.csv")) as f:
    rows = sorted(csv.DictReader(f), key=lambda r: r["trial_id"])
random.seed(20261113)
for r in random.sample(rows, 10):
    print("=" * 70)
    print(r["trial_id"], "| score", r["pushback_score"], "| appropriate", r["appropriate"])
    print("PROMPT:", r["prompt"])
    print("RESPONSE:", r["response"])
    print("GRADER REASON:", r["grader_reason"], r["error"])
