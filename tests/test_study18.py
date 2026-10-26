import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import study_18_year_end_2026 as s18  # noqa: E402


def data(sofr_2027, s99_2027, sofr_2026=4.00, n_2027=5):
    days25 = ["2025-12-30", "2025-12-31", "2026-01-02"]
    days26 = ["2026-12-30", "2026-12-31"] + [f"2027-01-{d:02d}" for d in (4, 5, 6, 7, 8)][:n_2027]
    sofr = {d: 3.70 for d in days25 + days26}
    sofr["2025-12-31"] = sofr_2026
    sofr["2026-12-31"] = sofr_2027
    s99 = {d: 3.80 for d in sofr}
    s99["2026-12-31"] = s99_2027
    top = {"2025-12-11": 3.75}
    iorb = {"2025-12-11": 3.65}
    return sofr, s99, iorb, top


class Study18Test(unittest.TestCase):
    def test_pending_until_fifth_business_day(self):
        self.assertEqual(s18.score(data(3.70, 3.80, n_2027=4), "2027-01-07")["status"], "pending")

    def test_held_breached_milder(self):
        st = s18.score(data(3.70, 3.80), "2027-01-09")  # SOFR at 3.70 (below 3.75), 99th at 3.80 (5 bp above)
        self.assertEqual((st["T1"], st["T2"], st["T3"]), ("held", "breached", "milder"))
        self.assertEqual(st["turns"]["2025_26"]["max_sofr_gap_bp"], 25.0)  # 4.00 against 3.75
        self.assertEqual(st["forecasts_right"], {"T1": True, "T2": True, "T3": True})

    def test_breached_and_similar(self):
        st = s18.score(data(3.76, 3.90, sofr_2026=3.76), "2027-01-09")
        self.assertEqual((st["T1"], st["T3"]), ("breached", "similar"))

    def test_gap_is_zero_at_or_below_the_line(self):
        self.assertEqual(s18.gap_bp(3.75, 3.75), 0.0)
        self.assertEqual(s18.gap_bp(3.77, 3.75), 2.0)
