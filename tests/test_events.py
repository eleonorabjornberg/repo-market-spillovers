import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from spillovers import events as ev  # noqa: E402
from spillovers import outcomes as oc  # noqa: E402


def row(date, iorb=4.4, coupons=0, tax=False):
    return {"date": date, "sofr": 4.3, "iorb": iorb, "coupons": coupons, "tax_date": tax}


class CalendarTest(unittest.TestCase):
    def setUp(self):
        self.rows = [row("2025-03-13"), row("2025-03-17", coupons=50), row("2025-03-28"), row("2025-03-31"),
                     row("2025-04-01"), row("2025-04-15", tax=True), row("2025-04-16", iorb=4.15),
                     row("2025-04-30", iorb=4.15), row("2025-05-01", iorb=4.15)]
        self.labels, self.excluded = ev.classify(self.rows, {"2025-03-28"})

    def test_month_and_quarter_boundaries_come_from_panel_days(self):
        self.assertEqual(self.labels["2025-03-31"], {"month_end", "quarter_end"})
        self.assertEqual(self.labels["2025-04-01"], {"month_start"})
        self.assertEqual(self.labels["2025-04-30"], {"month_end"})
        self.assertEqual(self.labels["2025-03-28"], set())

    def test_mid_month_coupon_settlement_needs_a_settlement(self):
        self.assertEqual(self.labels["2025-03-17"], {"coupon_settle"})
        self.assertEqual(self.labels["2025-03-13"], set())

    def test_tax_flag(self):
        self.assertEqual(self.labels["2025-04-15"], {"tax"})

    def test_exclusions(self):
        # FOMC day, IORB change day, and the last panel day (month-end status unknown)
        self.assertEqual(self.excluded, {"2025-03-28", "2025-04-16", "2025-05-01"})

    def test_regimes(self):
        self.assertEqual(ev.regime_of("2019-09-17"), "scarce_2018_19")
        self.assertEqual(ev.regime_of("2022-06-30"), "floor_2021_23")
        self.assertEqual(ev.regime_of("2026-03-31"), "scarce_2025_26")


class ChangesTest(unittest.TestCase):
    def test_change_is_against_the_previous_panel_day_only(self):
        dates = ["2025-04-17", "2025-04-18", "2025-04-21"]
        series = {"2025-04-17": 4.00, "2025-04-21": 4.10}  # market closed on the 18th
        changes = oc.daily_changes(dates, series, "bp")
        self.assertIsNone(changes["2025-04-18"])
        self.assertIsNone(changes["2025-04-21"])  # never a two-day change

    def test_change_net_of_iorb(self):
        dates = ["d1", "d2"]
        changes = oc.daily_changes(dates, {"d1": 4.50, "d2": 4.30}, "bp_iorb", {"d1": 4.40, "d2": 4.15})
        self.assertAlmostEqual(changes["d2"], 5.0)

    def test_log_return(self):
        changes = oc.daily_changes(["a", "b"], {"a": 100.0, "b": 101.0}, "logpct")
        self.assertAlmostEqual(changes["b"], 0.995033, places=5)


if __name__ == "__main__":
    unittest.main()
