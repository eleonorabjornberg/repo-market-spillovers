import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import study_21_reserves_gauge as s21  # noqa: E402


class Study21Test(unittest.TestCase):
    def test_zones(self):
        self.assertEqual([s21.zone(x) for x in (9.9, 10.0, 10.99, 11.0)], ["scarce", "no call", "no call", "ample"])

    def test_debt_is_used_only_once_public(self):
        pub = s21.public_debt({"2026-04-01": 30.0e6, "2026-07-01": 31.0e6})
        self.assertEqual(pub("2026-08-31"), None)       # Q2 public from 1 September
        self.assertEqual(pub("2026-09-01"), 30.0e6)
        self.assertEqual(pub("2026-12-01"), 31.0e6)     # Q3 public from 1 December

    def test_score_matches_and_verdict(self):
        weekly = {f"2026-{m:02d}-07": 9.5 for m in (11, 12)}
        weekly.update({f"2027-{m:02d}-07": 9.5 for m in range(1, 5)})
        measures = {"2026-11": (-12.0, 5.0), "2026-12": (-12.0, 5.0), "2027-01": (-12.0, 5.0),
                    "2027-02": (-12.0, 5.0), "2027-03": (-12.0, 5.0), "2027-04": (-18.0, 1.0)}
        st = s21.score(weekly, measures, "2027-05-10")
        self.assertEqual(st["zone_months"], 6)
        self.assertEqual(st["match_share_pct"], 83.3)
        self.assertEqual(st["verdict"], "the gauge holds (interim)")

    def test_pending_with_few_months(self):
        st = s21.score({"2026-11-07": 9.5}, {"2026-11": (-12.0, 5.0)}, "2026-12-10")
        self.assertEqual(st["verdict"], "pending")
