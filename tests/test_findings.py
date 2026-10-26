import json
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


class StudyPagesTest(unittest.TestCase):
    def test_study_links_go_to_site_pages(self):
        self.assertEqual(bf.target("../study-14/result.md", "results/study-15", "../"), "../studies/study-14.html")
        self.assertEqual(bf.target("results/study-16/result.md", "", ""), "studies/study-16.html")

    def test_other_links_go_to_github(self):
        self.assertEqual(bf.target("result.json", "results/study-16", "../"), bf.REPO + "results/study-16/result.json")
        self.assertEqual(bf.target("../../docs/x.md#y", "results/study-16", "../"), bf.REPO + "docs/x.md#y")

    def test_numbered_list(self):
        self.assertEqual(bf.render_list(["1. one", "2. two"], ordered=True), "<ol><li>one</li><li>two</li></ol>")

    def test_plain(self):
        self.assertEqual(bf.plain("did **not** move [x](y.md)"), "did not move x")


class RobustnessTest(unittest.TestCase):
    def test_escaped_pipe_stays_in_its_cell(self):
        html_ = bf.render_table(["| a | b |", "|---|---|", r"| x \| y | z |"])
        self.assertIn(">x | y</td>", html_)
        self.assertIn(">z</td>", html_)

    def test_uneven_table_raises(self):
        with self.assertRaises(ValueError):
            bf.render_table(["| a | b |", "|---|---|", "| x | y | z |"])

    def test_every_source_table_is_even(self):
        sources = [ROOT / "SYNTHESIS.md", *sorted((ROOT / "results").glob("*/result.md"))]
        for path in sources:
            for kind, lines in bf.blocks(path.read_text().splitlines()):
                if kind == "table":
                    bf.render_table(lines)  # raises on an uneven row

    def test_ordered_list_keeps_its_start(self):
        self.assertTrue(bf.render_list(["2. two"], ordered=True).startswith('<ol start="2">'))

    def test_ampersand_in_url_escaped_once(self):
        self.assertIn('href="https://x.org/a?b=1&amp;c=2"', bf.inline("[q](https://x.org/a?b=1&c=2)"))

    def test_external_and_missing_images(self):
        _, body = bf.render("![a](https://x.org/a.png)\n\n![b](nope.png)", base="results/study-16")
        self.assertIn('src="https://x.org/a.png"', body)
        self.assertNotIn("nope.png", body)

    def test_unnumbered_study_sorts_last(self):
        self.assertEqual(sorted(["dollar", "study-16", "study-02"], key=bf.study_number), ["study-02", "study-16", "dollar"])

    def test_study10_constant_matches_its_design(self):
        import study_10_prospective as s10
        self.assertEqual(bf.LEAD_MIN_SHOCKS, s10.LEAD_MIN_SHOCKS)

    def test_study10_page(self):
        status = json.loads((ROOT / "results" / "study-10" / "status.json").read_text())
        status["C_chain_under_stress"]["reference_april_2025"]["C1_max_noncal_spread_bp"] = None
        page = bf.study10_page(status, 10)
        self.assertIn("the test needs 10", page)
        self.assertIn("n/a bp", page)


if __name__ == "__main__":
    unittest.main()
