import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_17_spikes_and_creep as s17  # noqa: E402


def month(prefix, n):
    return [f"{prefix}-{d:02d}" for d in range(1, n + 1)]


class Study17Test(unittest.TestCase):
    def test_as_of(self):
        f = s17.AsOf({"2025-01-01": 1.0, "2025-01-08": 2.0})
        self.assertIsNone(f("2024-12-31"))
        self.assertEqual(f("2025-01-07"), 1.0)
        self.assertEqual(f("2025-01-08"), 2.0)

    def test_month_jump(self):
        days = month("2025-03", 20) + month("2025-04", 3)
        s = {d: -5.0 for d in days}
        s["2025-03-20"], s["2025-04-01"] = 3.0, 1.0  # last business day of March and first of April
        top = s17.AsOf({"2025-01-01": 4.5})
        j = s17.month_jumps(days, s, top)["2025-03"]
        self.assertEqual(j["J"], 7.0)  # mean(3, 1) - median(-5)
        self.assertEqual(j["B"], -5.0)
        self.assertTrue(j["qe"])

    def test_month_with_a_rate_change_is_dropped(self):
        days = month("2025-03", 20) + month("2025-04", 3)
        s = {d: 0.0 for d in days}
        top = s17.AsOf({"2025-01-01": 4.5, "2025-03-19": 4.25})
        self.assertNotIn("2025-03", s17.month_jumps(days, s, top))

    def test_regime(self):
        self.assertEqual(s17.regime("2019-06-03"), "scarce_2018_19")
        self.assertEqual(s17.regime("2020-06-03"), None)
        self.assertEqual(s17.regime("2026-06-03"), "scarce_2025_26")
