import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import study_11_what_repo_funds as s11  # noqa: E402

TABLE5 = ("Table 5: Major Foreign Holders of Treasury Securities\t\t\n\t\t\n"
          "Country\t2026-08\t2026-07\t\n"
          "Japan\t1068.3\t1103.9\t\n"
          "Cayman Islands\t463.0\t460.1\t\n")


class TicTest(unittest.TestCase):
    def test_cayman_row(self):
        with tempfile.TemporaryDirectory() as d:
            (pathlib.Path(d) / "TIC_slt_table5.txt").write_text(TABLE5)
            with mock.patch.object(s11, "RAW", pathlib.Path(d)):
                self.assertEqual(s11.tic_cayman(), {"2026-08": 463.0, "2026-07": 460.1})


if __name__ == "__main__":
    unittest.main()
