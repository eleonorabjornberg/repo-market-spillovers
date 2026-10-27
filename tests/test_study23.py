import pathlib
import random
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_23_dealer_markup as s23  # noqa: E402


class Study23Test(unittest.TestCase):
    def test_quarter_end_turns(self):
        days = ["2025-12-30", "2025-12-31", "2026-01-02", "2026-01-05", "2026-03-30", "2026-03-31", "2026-04-01",
                "2026-05-29", "2026-06-01"]
        qe, ye = s23.quarter_end_turns(days)
        self.assertEqual(qe, {"2025-12-31", "2026-01-02", "2026-03-31", "2026-04-01"})
        self.assertEqual(ye, {"2025-12-31", "2026-01-02"})

    def test_boot_diff_point(self):
        values = {"2026-01-01": 5.0, "2026-01-02": 7.0, "2026-01-03": 1.0, "2026-01-04": 3.0}
        est, ci = s23.boot_diff(["2026-01-01", "2026-01-02"], ["2026-01-03", "2026-01-04"], values, random.Random(1))
        self.assertEqual(est, 4.0)
        self.assertLessEqual(ci[0], ci[1])
