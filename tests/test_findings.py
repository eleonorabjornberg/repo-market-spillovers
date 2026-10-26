import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_findings as bf  # noqa: E402


class RenderTest(unittest.TestCase):
    def test_inline(self):
        self.assertEqual(bf.inline("**a** and *b* and `c`"), "<b>a</b> and <i>b</i> and <code>c</code>")

    def test_repo_links_point_to_github_and_site_links_stay(self):
        self.assertIn(f'href="{bf.REPO}results/x.md"', bf.inline("[x](results/x.md)"))
        self.assertIn('href="index.html"', bf.inline("[w](index.html)"))
        self.assertIn('href="https://a.b/c"', bf.inline("[e](https://a.b/c)"))

    def test_table_and_list(self):
        _, body = bf.render("| A | B |\n|---|---:|\n| x | 1 |\n\n- one\n  continued\n- two\n  - sub")
        self.assertIn('<th style="text-align:right">B</th>', body)
        self.assertIn("<li>one continued</li>", body)
        self.assertIn("<ul><li>sub</li></ul>", body)

    def test_synthesis_renders_without_leftover_markdown(self):
        title, body = bf.render((ROOT / "SYNTHESIS.md").read_text())
        self.assertEqual(title, "Is the repo market signalling a crisis?")
        for leftover in ("**", "](", "`", "\n|"):
            self.assertNotIn(leftover, body)


if __name__ == "__main__":
    unittest.main()
