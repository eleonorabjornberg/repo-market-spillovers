import datetime as dt
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_16_data_centre_debt as s16  # noqa: E402

D = dt.date.fromisoformat


class Study16Test(unittest.TestCase):
    def test_shift_skips_weekends(self):
        self.assertEqual(s16.shift(D("2026-10-23"), 1), D("2026-10-26"))  # Friday -> Monday
        self.assertEqual(s16.shift(D("2026-10-26"), -1), D("2026-10-23"))

    def test_deal_days(self):
        filings = [("Meta", "FWP", D("2026-03-02")), ("Meta", "424B2", D("2026-03-04")),  # same deal, FWP wins
                   ("Oracle", "424B2", D("2026-03-05")),  # within 5 business days of Meta's: merged
                   ("Amazon", "424B2", D("2026-04-15"))]  # no FWP: one business day earlier
        self.assertEqual(s16.deal_days(filings), [D("2026-03-02"), D("2026-04-14")])

    def test_ols_recovers_coefficients(self):
        rows = [(1.0 + 2.0 * x, [1.0, x]) for x in (0.0, 1.0, 2.0, 3.0)]
        beta = s16.ols(rows, 2)
        self.assertAlmostEqual(beta[0], 1.0)
        self.assertAlmostEqual(beta[1], 2.0)

    def test_event_coefficient(self):
        # event days are exactly twice the others, within each month and weekday pattern
        obs = [(m, wd, (2.0 if e else 1.0) * (1 + wd), e) for m in ("a", "b") for wd in range(5) for e in (False, True)]
        self.assertAlmostEqual(s16.event_coefficient(obs), 0.6931471805599453)

    def test_annual_keeps_full_years_and_latest_filing(self):
        facts = {"facts": {"us-gaap": {"X": {"units": {"USD": [
            {"form": "10-K", "start": "2024-01-01", "end": "2024-12-31", "val": 10, "filed": "2025-02-01"},
            {"form": "10-K", "start": "2024-01-01", "end": "2024-12-31", "val": 11, "filed": "2026-02-01"},
            {"form": "10-K", "start": "2024-10-01", "end": "2024-12-31", "val": 3, "filed": "2025-02-01"},
            {"form": "10-Q", "start": "2025-01-01", "end": "2025-03-31", "val": 4, "filed": "2025-04-01"}]}}}}}
        self.assertEqual(s16.annual(facts, "X"), {2024: 11})
