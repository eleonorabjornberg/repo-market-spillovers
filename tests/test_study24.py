import csv
import io
import pathlib
import random
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_study24 as f24  # noqa: E402
import study_24_swap_spread_visibility as s24  # noqa: E402

HEADER = ["UPI FISN", "UPI Underlier Name", "Action type", "Event type", "Notional currency-Leg 1",
          "Execution Timestamp", "Effective Date", "Expiration Date", "Notional amount-Leg 1", "Fixed rate-Leg 1",
          "Fixed rate-Leg 2", "Package indicator", "Package transaction spread", "Platform identifier"]


def row(ts="2026-11-06T10:00:00Z", years=10, notional="100,000,000", package="TRUE", spread="0.01", platform="TWSF",
        rate="0.04", fisn="NA/Swap OIS USD", action="NEWT"):
    exp = f"{2026 + years}-11-10"
    return dict(zip(HEADER, [fisn, "USD-SOFR-COMPOUND", action, "TRAD", "USD", ts, "2026-11-10", exp, notional, rate,
                             "", package, spread, platform]))


class ClassifyTest(unittest.TestCase):
    def test_single_and_curve_packages(self):
        rows = [row(), row(ts="2026-11-06T11:00:00Z", years=2), row(ts="2026-11-06T11:00:00Z", years=10)]
        totals, _ = f24.classify_day(rows)
        cats = {(c, b): t[0] for (c, b), t in totals.items()}
        self.assertEqual(cats[("single_spread", "8-15y")], 1)
        self.assertEqual(cats[("curve_spread", "1.5-4y")], 1)
        self.assertEqual(cats[("curve_spread", "8-15y")], 1)

    def test_package_without_spread_and_outright(self):
        rows = [row(spread=""), row(package="FALSE", spread="")]
        totals, tens = f24.classify_day(rows)
        self.assertIn(("package_no_spread", "8-15y"), totals)
        self.assertIn(("outright", "8-15y"), totals)
        self.assertEqual(tens, [0.04])

    def test_excluded_trades(self):
        rows = [row(fisn="NA/Swap Fixed-Float USD"), row(action="TERM"), row(years=40), row(notional="")]
        totals, _ = f24.classify_day(rows)
        self.assertEqual(dict(totals), {})

    def test_capped_notional_and_dv01(self):
        self.assertEqual(f24.notional("650,000,000+"), (650000000.0, True))
        self.assertEqual(f24.notional("25,000,000"), (25000000.0, False))
        totals, _ = f24.classify_day([row(notional="100,000,000+", rate="0")])
        t = totals[("single_spread", "8-15y")]
        self.assertEqual(t[3], 1)
        self.assertAlmostEqual(t[2], 100e6 * 3653 / 365.25 * 1e-4 / 1e6, places=9)
        self.assertAlmostEqual(t[4], t[2])

    def test_reads_dictreader(self):
        buf = io.StringIO()
        w = csv.DictWriter(buf, HEADER)
        w.writeheader()
        w.writerow(row())
        buf.seek(0)
        totals, _ = f24.classify_day(csv.DictReader(buf))
        self.assertIn(("single_spread", "8-15y"), totals)


class StatsTest(unittest.TestCase):
    def test_spearman_ties_and_order(self):
        self.assertAlmostEqual(s24.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(s24.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertEqual(s24.ranks([5, 5, 1]), [2.5, 2.5, 1.0])

    def test_block_bootstrap_interval(self):
        xs = list(range(20))
        r, ci = s24.block_boot_corr(xs, [2 * x + 1 for x in xs], 3, 200, random.Random(1))
        self.assertAlmostEqual(r, 1.0)
        self.assertLessEqual(ci[0], ci[1])

    def test_quarter_and_week(self):
        self.assertEqual(s24.quarter("2025-04-03"), "2025Q2")
        self.assertEqual(s24.week("2025-04-03"), "2025-03-31")


if __name__ == "__main__":
    unittest.main()
