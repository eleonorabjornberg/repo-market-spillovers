import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_22_which_denominator as s22  # noqa: E402


class Study22Test(unittest.TestCase):
    def test_corr(self):
        self.assertAlmostEqual(s22.corr([1, 2, 3], [2, 4, 6]), 1.0)
        self.assertAlmostEqual(s22.corr([1, 2, 3], [3, 2, 1]), -1.0)
