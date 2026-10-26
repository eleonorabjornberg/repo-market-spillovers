import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from spillovers import history as h  # noqa: E402


class MonthlyTest(unittest.TestCase):
    def test_daily_averaged_within_month(self):
        self.assertEqual(h.to_monthly({"2007-07-02": 1.0, "2007-07-31": 3.0, "2007-08-01": 5.0}),
                         {"2007-07": 2.0, "2007-08": 5.0})

    def test_quarterly_carried_to_its_three_months(self):
        # FRED dates a quarter at its first day, OFR at its last: both land on the same three months
        self.assertEqual(h.to_monthly({"2026-04-01": 7.0}, quarterly=True),
                         {"2026-04": 7.0, "2026-05": 7.0, "2026-06": 7.0})
        self.assertEqual(h.to_monthly({"2026-06-30": 7.0}, quarterly=True),
                         {"2026-04": 7.0, "2026-05": 7.0, "2026-06": 7.0})

    def test_ratio_and_difference(self):
        sources = {"A": {"2020-01": 50.0}, "B": {"2020-01": 200.0, "2020-02": 1.0}}
        self.assertEqual(h.build_indicator({"num": "A", "den": "B", "scale": 100}, sources), {"2020-01": 25.0})
        self.assertEqual(h.build_indicator({"num": "A", "minus": "B", "scale": 1}, sources), {"2020-01": -150.0})

    def test_month_add(self):
        self.assertEqual(h.month_add("2007-11", 2), "2008-01")
        self.assertEqual(h.month_add("2008-01", -1), "2007-12")


class StressTest(unittest.TestCase):
    def test_onset_needs_a_quiet_spell(self):
        weeks = [f"2000-{m:02d}-01" for m in range(1, 13)]
        nfci = dict(zip(weeks, [-1, -1, -1, 1, 1, -1, 1, -1, -1, -1, 1, 1]))
        self.assertEqual(h.stress_onsets(nfci, quiet_weeks=3), ["2000-04-01", "2000-11-01"])

    def test_warning_check(self):
        series = {f"2000-{m:02d}": float(m) for m in range(1, 13)}
        # onset in 2000-08; months >= 5 are as extreme as today (5) in the high direction
        r = h.warning_check(series, 5.0, "high", ["2000-08"], start="2000-01", horizon=2, last_month="2000-12",
                            min_months=1)
        # observable months: 2000-01..2000-10; extreme: 05..10 (6); followed within 2 months of 2000-08: 06, 07
        self.assertEqual(r["warning_months"], 6)
        self.assertAlmostEqual(r["share_followed"], 2 / 6)
        self.assertAlmostEqual(r["base_share"], 2 / 10)

    def test_no_history_at_todays_level(self):
        series = {"2000-01": 1.0, "2000-02": 2.0, "2000-03": 9.0}
        r = h.warning_check(series, 9.0, "high", [], start="2000-01", horizon=0, last_month="2000-03")
        self.assertIsNone(r["share_followed"])


if __name__ == "__main__":
    unittest.main()


class CompleteMonthsTest(unittest.TestCase):
    def test_daily_drops_the_partial_last_month(self):
        self.assertEqual(h.complete_months({"2026-09-30": 1.0, "2026-10-02": 2.0}, "daily"), {"2026-09": 1.0})

    def test_monthly_keeps_its_last_month(self):
        self.assertEqual(h.complete_months({"2026-08-31": 1.0, "2026-09-30": 2.0}, "monthly"),
                         {"2026-08": 1.0, "2026-09": 2.0})

    def test_unknown_kind(self):
        with self.assertRaises(ValueError):
            h.complete_months({}, "weekly")
