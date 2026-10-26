import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_15_corporate_bonds as s15  # noqa: E402


class Study15Test(unittest.TestCase):
    def test_window_change_uses_four_weeks_each_side(self):
        series = {f"2020-0{m}-0{d}": v for (m, d), v in zip([(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 1), (2, 2),
                                                             (2, 3), (2, 4), (2, 5)], [9, 1, 1, 1, 1, 2, 2, 2, 2, 9])}
        self.assertEqual(s15.window_change(series, "2020-01-05", "2020-02-01"), 100.0)
        self.assertIsNone(s15.window_change(series, "2020-01-03", "2020-02-01"))

    def test_panic_days_follow_study_09(self):
        vix = {"2020-03-02": 20.0, "2020-03-03": 23.0, "2020-03-04": 23.5, "2020-03-05": 30.0}
        d10 = {"2020-03-02": 1.00, "2020-03-03": 1.05, "2020-03-04": 1.0, "2020-03-05": 0.9}
        baa = {"2020-03-02": 4.00, "2020-03-03": 4.02, "2020-03-04": 4.0}
        # 03-03 is +15%: a panic day; 03-05 is +27.7% but Baa is missing that day
        self.assertEqual(s15.panic_days(vix, d10, baa), [("2020-03-03", 5.0, 2.0)])

    def test_agreement(self):
        self.assertEqual(s15.agreement({"a": 100.0, "b": 103.0}, {"a": 100.5, "b": 100.0}),
                         {"n_weeks": 2, "share_within_1pct": 50.0})
