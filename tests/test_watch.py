import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import watch  # noqa: E402


def readings(**kw):
    base = {"sofr_iorb_month_avg_bp": -2.0, "sofr_iorb_month_max_bp": 1.0, "swap_spread_10y_month_min_bp": -45.0,
            "ofr_fsi_month_avg": -2.0, "baa_10y_bp": {"percentile": 50.0}}
    base.update(kw)
    return base


QUARTERLY = {"2026-01": 10.0, "2026-02": 10.0, "2026-03": 10.0, "2026-04": 11.0, "2026-05": 11.0, "2026-06": 11.0}
FUT = {"2026-04": 3.0, "2026-05": 4.0, "2026-06": 3.5}
SPONSORED = {"2026-03": 47.0, "2026-04": 46.5, "2026-05": 46.0, "2026-06": 46.2}


class FlagsTest(unittest.TestCase):
    def flags(self, r=None, hf=QUARTERLY, fut=FUT, sp=SPONSORED, month="2026-06"):
        return watch.flags_from(r or readings(), hf, fut, sp, month)

    def test_quiet_month(self):
        self.assertEqual([k for k, v in self.flags(hf={**QUARTERLY, "2025-12": 12.0}).items() if v], [])

    def test_thresholds(self):
        f = self.flags(readings(sofr_iorb_month_avg_bp=0.5, sofr_iorb_month_max_bp=10.0,
                                swap_spread_10y_month_min_bp=-60.0, ofr_fsi_month_avg=0.1,
                                baa_10y_bp={"percentile": 5.0}))
        for k in ("F1", "F2", "F6", "F7", "F8"):
            self.assertTrue(f[k], k)
        f = self.flags(readings(sofr_iorb_month_avg_bp=0.0, sofr_iorb_month_max_bp=9.9,
                                swap_spread_10y_month_min_bp=-59.9, ofr_fsi_month_avg=0.0))
        for k in ("F1", "F2", "F6", "F7"):
            self.assertFalse(f[k], k)

    def test_records(self):
        self.assertTrue(self.flags()["F3"])  # 11.0 is the highest quarter so far
        self.assertFalse(self.flags(fut=FUT)["F4"])  # 3.5 is below May's 4.0
        self.assertTrue(self.flags(fut={**FUT, "2026-06": 4.1})["F4"])

    def test_moving_away_from_clearing(self):
        falling = {"2026-03": 47.0, "2026-04": 46.5, "2026-05": 46.0, "2026-06": 45.5}
        self.assertTrue(self.flags(sp=falling)["F5"])
        self.assertFalse(self.flags(sp=SPONSORED)["F5"])  # June ticked up
        shrinking_hf = {**QUARTERLY, "2026-04": 9.0, "2026-05": 9.0, "2026-06": 9.0}
        self.assertFalse(self.flags(sp=falling, hf=shrinking_hf)["F5"])

    def test_reads_nothing_after_the_month(self):
        self.assertFalse(self.flags(fut={**FUT, "2026-07": 9.0})["F4"])


if __name__ == "__main__":
    unittest.main()


class ProspectiveCalendarTest(unittest.TestCase):
    def test_non_calendar_rule(self):
        import study_10_prospective as s10
        days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-13", "2026-11-18", "2026-11-19",
                "2026-11-25", "2026-11-27", "2026-11-30", "2026-12-01"]
        iorb = {d: 3.9 for d in days}
        for d in days[days.index("2026-11-19"):]:
            iorb[d] = 3.65  # a cut on the 19th: that day alone is excluded
        got = s10.non_calendar(days, iorb)
        # first two and last two business days of November out, the 13th out, the IORB change out;
        # December is the incomplete latest month, so none of it counts yet
        self.assertEqual(got, {"2026-11-04", "2026-11-05", "2026-11-18", "2026-11-25"})

    def test_offset(self):
        import study_10_prospective as s10
        days = ["a", "b", "c"]
        self.assertEqual(s10.offset(days, "b", 1), "c")
        self.assertIsNone(s10.offset(days, "c", 1))
