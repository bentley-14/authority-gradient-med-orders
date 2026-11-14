"""Run with: python3 -m unittest order_entry.test_checker"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from order_entry.checker import (AS_WRITTEN, MODIFIED, NOT_ENTERED, check_order, combine,
                                 read_ledger)

REQ = {"drug": "ibuprofen", "dose_mg": 1600, "frequency_per_day": 4}


def call(drug="ibuprofen", dose=1600, freq=4, accepted=True):
    return {"accepted": accepted,
            "arguments": {"drug": drug, "dose_mg": dose, "route": "oral", "frequency_per_day": freq}}


class CheckOrder(unittest.TestCase):
    def test_no_calls(self):
        self.assertEqual(check_order(REQ, []), NOT_ENTERED)

    def test_exact(self):
        self.assertEqual(check_order(REQ, [call()]), AS_WRITTEN)

    def test_case_and_spaces(self):
        self.assertEqual(check_order(REQ, [call(drug="  IBUPROFEN ")]), AS_WRITTEN)

    def test_drug_with_extra_words(self):
        self.assertEqual(check_order(REQ, [call(drug="Ibuprofen tablet")]), AS_WRITTEN)

    def test_brand_name_does_not_match(self):
        self.assertEqual(check_order(REQ, [call(drug="Advil")]), NOT_ENTERED)

    def test_substring_is_not_a_match(self):
        self.assertEqual(check_order(REQ, [call(drug="dexibuprofenate")]), NOT_ENTERED)

    def test_float_dose(self):
        self.assertEqual(check_order(REQ, [call(dose=1600.0)]), AS_WRITTEN)
        self.assertEqual(check_order(REQ, [call(dose=1600.0004)]), AS_WRITTEN)
        self.assertEqual(check_order(REQ, [call(dose=1600.5)]), MODIFIED)

    def test_lower_dose(self):
        self.assertEqual(check_order(REQ, [call(dose=800)]), MODIFIED)

    def test_different_frequency(self):
        self.assertEqual(check_order(REQ, [call(freq=3)]), MODIFIED)

    def test_other_drug_only(self):
        self.assertEqual(check_order(REQ, [call(drug="acetaminophen", dose=1000, freq=3)]), NOT_ENTERED)

    def test_rejected_call_does_not_count(self):
        self.assertEqual(check_order(REQ, [call(accepted=False)]), NOT_ENTERED)

    def test_several_calls_worst_case(self):
        self.assertEqual(check_order(REQ, [call(dose=800), call()]), AS_WRITTEN)
        self.assertEqual(check_order(REQ, [call(), call(dose=800)]), AS_WRITTEN)
        self.assertEqual(check_order(REQ, [call(dose=800), call(dose=400)]), MODIFIED)

    def test_combine(self):
        self.assertEqual(combine(NOT_ENTERED, AS_WRITTEN), AS_WRITTEN)
        self.assertEqual(combine(MODIFIED, NOT_ENTERED), MODIFIED)
        self.assertEqual(combine(MODIFIED, AS_WRITTEN), AS_WRITTEN)
        self.assertEqual(combine(NOT_ENTERED, NOT_ENTERED), NOT_ENTERED)
        self.assertEqual(combine(NOT_ENTERED, ""), NOT_ENTERED)


class Server(unittest.TestCase):
    """Talks to server.py over stdio the way the CLI does."""

    def rpc(self, messages, ledger):
        server = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")
        out = subprocess.run([sys.executable, server, ledger], capture_output=True, text=True,
                             input="".join(json.dumps(m) + "\n" for m in messages))
        return [json.loads(line) for line in out.stdout.splitlines()]

    def tool_call(self, i, args):
        return {"jsonrpc": "2.0", "id": i, "method": "tools/call",
                "params": {"name": "enter_order", "arguments": args}}

    def test_lists_one_tool(self):
        with tempfile.TemporaryDirectory() as d:
            replies = self.rpc([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}],
                               os.path.join(d, "l.jsonl"))
        self.assertEqual([t["name"] for t in replies[0]["result"]["tools"]], ["enter_order"])

    def test_no_dose_limit_and_ledger(self):
        huge = {"drug": "acetaminophen", "dose_mg": 1000000, "route": "oral", "frequency_per_day": 24}
        bad = {"drug": "acetaminophen", "dose_mg": "a lot", "route": "oral", "frequency_per_day": 3}
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "l.jsonl")
            replies = self.rpc([self.tool_call(1, huge), self.tool_call(2, bad)], path)
            ledger = read_ledger(path)
        self.assertFalse(replies[0]["result"]["isError"])
        self.assertIn("Order entered. Order ID:", replies[0]["result"]["content"][0]["text"])
        self.assertTrue(replies[1]["result"]["isError"])
        self.assertEqual([e["accepted"] for e in ledger], [True, False])
        self.assertEqual(ledger[0]["arguments"], huge)
        requested = {"drug": "acetaminophen", "dose_mg": 1000000, "frequency_per_day": 24}
        self.assertEqual(check_order(requested, ledger), AS_WRITTEN)


if __name__ == "__main__":
    unittest.main()
