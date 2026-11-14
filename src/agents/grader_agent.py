"""Grader agent: scores a response 0 to 3 on the pushback rubric, title hidden."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from environment.isolated_claude import call_claude
from src.prompts.prompt_builder import grader_prompt, read_text


def parse_grade(text):
    """Returns (score, reason) or raises ValueError."""
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("no JSON object in grader output")
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise ValueError("bad JSON: %s" % e)
    score = obj.get("score")
    if isinstance(score, bool) or score not in (0, 1, 2, 3):
        raise ValueError("score not in 0..3: %r" % (score,))
    return int(score), str(obj.get("reason", "")).strip()


def grade(title_free_request, response, model, effort):
    """Returns (score or None, reason, error note, list of call records).

    One retry if the output does not parse. After that the score stays None
    and the error note says why.
    """
    prompt = grader_prompt(title_free_request, response)
    calls, error = [], ""
    for _ in range(2):
        rec = call_claude(read_text("grader_system.txt"), prompt, model, effort)
        calls.append(rec)
        try:
            score, reason = parse_grade(rec["raw_output"]["result"])
            return score, reason, "", calls
        except ValueError as e:
            error = "grader parse failure: %s" % e
    return None, "", error, calls
