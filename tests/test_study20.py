import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_20_allotment_and_threshold as s20  # noqa: E402


class Study20Test(unittest.TestCase):
    def test_quarterly_as_of(self):
        f = s20.quarterly_as_of({"2025-04-01": 1.0, "2025-07-01": 2.0})
        self.assertIsNone(f("2025-03-31"))
        self.assertEqual(f("2025-06-30"), 1.0)
        self.assertEqual(f("2025-07-01"), 2.0)

    def test_all_month_jumps_keeps_rate_change_months(self):
        days = [f"2025-03-{d:02d}" for d in range(1, 21)] + ["2025-04-01"]
        s = {d: -5.0 for d in days}
        s["2025-03-20"], s["2025-04-01"] = 3.0, 1.0
        j = s20.all_month_jumps(days, s)["2025-03"]
        self.assertEqual((j["J"], j["B"], j["qe"]), (7.0, -5.0, True))
