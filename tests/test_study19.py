import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import study_19_who_pays_above_the_line as s19  # noqa: E402


def day(sofr99, tgcr99, bgcr99):
    return {"SOFR": {"rate": 3.6, "p99": sofr99}, "TGCR": {"rate": 3.6, "p99": tgcr99},
            "BGCR": {"rate": 3.6, "p99": bgcr99}}


class Study19Test(unittest.TestCase):
    def test_breach_in_dvp_only_with_no_takeup(self):
        rt = {"a": day(3.80, 3.70, 3.72), "b": day(3.77, 3.74, 3.74), "c": day(3.70, 3.65, 3.66)}
        tk = {"c": {"total": 10.0, "by_close_time": {"13:45": 10.0}}}
        q1, q2, breach = s19.period_measures(sorted(rt), rt, lambda d: 3.75, tk)
        self.assertEqual(breach, ["a", "b"])
        self.assertEqual(q1["TGCR_p99_also_above"], 0)
        self.assertEqual(q1["verdict"], "outside tri-party (in DVP)")
        self.assertEqual(q2["median_takeup_breach_days_bn"], 0.0)
        self.assertEqual(q2["verdict"], "largely unused when the top of the market paid more")

    def test_at_the_line_is_not_above(self):
        self.assertFalse(s19.above(3.75, 3.75))
        self.assertTrue(s19.above(3.76, 3.75))
