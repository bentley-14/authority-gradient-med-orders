"""Run with: python3 -m unittest src.test_analyze_confirmatory

Checks the Cochran-Mantel-Haenszel statistic and the Mantel-Haenszel odds
ratio used by analyze_confirmatory.py against a case computed by hand from
the textbook formulas, and checks which strata are dropped.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_confirmatory as a


def make(drug, mult, title, entered, total):
    return [{"drug": drug, "mult": mult, "seniority": title, "y": int(i < entered)} for i in range(total)]


# stratum 1: group 10 of 15 entered, reference 4 of 15. stratum 2: group 6 of 15, reference 2 of 15.
ROWS = (make("d1", 2, "medical_student", 10, 15) + make("d1", 2, "no_title", 4, 15) +
        make("d2", 2, "medical_student", 6, 15) + make("d2", 2, "no_title", 2, 15) +
        make("d3", 2, "medical_student", 0, 15) + make("d3", 2, "no_title", 0, 15))  # nobody entered


class CMH(unittest.TestCase):
    def setUp(self):
        self.c = a.cmh(ROWS, ["medical_student"])

    def test_strata(self):
        self.assertEqual(self.c["used"], ["d1 2x", "d2 2x"])
        self.assertEqual(len(self.c["dropped"]), 1)

    def test_odds_ratio_by_hand(self):
        # MH OR = sum(a*d/n) / sum(b*c/n) = (10*11/30 + 6*13/30) / (5*4/30 + 9*2/30)
        self.assertAlmostEqual(self.c["or"], (110 / 30 + 78 / 30) / (20 / 30 + 18 / 30), places=10)

    def test_chi_square_by_hand(self):
        # observed a = 16. E = 15*14/30 + 15*8/30 = 11. V = sum(r1*r2*c1*c2 / (n^2 (n-1)))
        v = 15 * 15 * 14 * 16 / (900 * 29) + 15 * 15 * 8 * 22 / (900 * 29)
        self.assertAlmostEqual(self.c["chi2_nocc"], (16 - 11) ** 2 / v, places=10)
        self.assertAlmostEqual(self.c["chi2"], (abs(16 - 11) - 0.5) ** 2 / v, places=10)

    def test_interval_contains_estimate(self):
        self.assertLess(self.c["lo"], self.c["or"])
        self.assertGreater(self.c["hi"], self.c["or"])

    def test_holm(self):
        adj = a.holm([0.01, 0.04])
        self.assertAlmostEqual(adj[0], 0.02)
        self.assertAlmostEqual(adj[1], 0.04)


if __name__ == "__main__":
    unittest.main()
