"""Render SYNTHESIS.md as site/findings.html, and every study's result as site/studies/<study>.html with an index at
site/studies.html, in the watch page's style.

A small converter for the Markdown subset these files use: headings, paragraphs, bullet lists (one nested level,
continuation lines), numbered lists, tables, images, bold, italics and links. Links to a study's result page go to its
page on the site; other links into the repository become GitHub links, since the site serves only site/.
"""
import html
import json
import pathlib
import posixpath
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEAD_MIN_SHOCKS = 10  # study 10's frozen design (scripts/study_10_prospective.py); a test checks they agree
REPO = "https://github.com/eleonorabjornberg/repo-market-spillovers/blob/main/"


STUDY_PAGE = re.compile(r"results/([\w-]+)/result\.md$")


def target(url, base, site_prefix):
    """Where a Markdown link points on the site: base is the source file's repository directory, site_prefix the
    path from the page being written back to site/."""
    if re.match(r"https?://|#|mailto:", url) or url in ("index.html", "findings.html", "studies.html"):
        return site_prefix + url if url.endswith(".html") and not url.startswith("http") else url
    path, _, anchor = url.partition("#")
    path = posixpath.normpath(posixpath.join(base, path))
    if path == "docs/design-study-10-prospective.md":
        return f"{site_prefix}studies/study-10.html"
    m = STUDY_PAGE.match(path)
    if m:
        return f"{site_prefix}studies/{m.group(1)}.html" + (f"#{anchor}" if anchor else "")
    return REPO + path + (f"#{anchor}" if anchor else "")


def inline(text, base="", site_prefix=""):
    links = []

    def stash(m):  # links are resolved from the raw URL, so an & in it is escaped once
        links.append((m.group(1), target(m.group(2), base, site_prefix)))
        return f"\x00{len(links) - 1}\x00"

    text = html.escape(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash, text), quote=False)
    text = re.sub(r"\x00(\d+)\x00",
                  lambda m: f'<a href="{html.escape(links[int(m.group(1))][1])}">'
                            f'{html.escape(links[int(m.group(1))][0], quote=False)}</a>', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<i>\1</i>", text)
    return text


def blocks(lines):
    """Group lines into (kind, lines) blocks: heading, table, list, paragraph."""
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("#"):
            out.append(("heading", [line]))
            i += 1
        elif line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            out.append(("table", lines[i:j]))
            i = j
        elif line.startswith("!["):
            out.append(("image", [line]))
            i += 1
        elif line.startswith("- ") or re.match(r"\d+\. ", line):
            ordered = not line.startswith("- ")
            j = i
            while j < len(lines) and lines[j].strip() and (
                    lines[j].startswith(("- ", "  ")) if not ordered else (re.match(r"\d+\. ", lines[j])
                                                                          or lines[j].startswith("  "))):
                j += 1
            out.append(("olist" if ordered else "list", lines[i:j]))
            i = j
        else:
            j = i
            while j < len(lines) and lines[j].strip() and not (lines[j].startswith(("#", "|", "- ", "!["))
                                                               or re.match(r"\d+\. ", lines[j])):
                j += 1
            out.append(("paragraph", lines[i:j]))
            i = j
    return out


def render_list(lines, ordered=False, **kw):
    items = []  # [text, [subitems]]
    for line in lines:
        m = re.match(r"\d+\. ", line)
        if line.startswith("- ") or m:
            items.append([line[m.end() if m else 2:], []])
        elif re.match(r" {2,4}- ", line):
            items[-1][1].append(line.strip()[2:])
        elif line.startswith("    ") and items[-1][1]:
            items[-1][1][-1] += " " + line.strip()
        else:
            items[-1][0] += " " + line.strip()
    parts = []
    for text, sub in items:
        nested = "<ul>" + "".join(f"<li>{inline(s, **kw)}</li>" for s in sub) + "</ul>" if sub else ""
        parts.append(f"<li>{inline(text, **kw)}{nested}</li>")
    if not ordered:
        return "<ul>" + "".join(parts) + "</ul>"
    start = int(re.match(r"(\d+)\. ", lines[0]).group(1))
    return (f'<ol start="{start}">' if start != 1 else "<ol>") + "".join(parts) + "</ol>"


def cells(line):
    """A Markdown table row's cells; an escaped pipe (\\|) stays inside its cell."""
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def render_table(lines, **kw):
    rows = [cells(line) for line in lines]
    if any(len(r) != len(rows[0]) for r in rows):
        raise ValueError(f"table rows have different numbers of cells: {lines[0]!r}")
    head, body = rows[0], [r for r in rows[2:]]
    aligns = ["right" if c.endswith(":") else "left" for c in rows[1]]
    th = "".join(f'<th style="text-align:{a}">{inline(c, **kw)}</th>' for c, a in zip(head, aligns))
    trs = "".join("<tr>" + "".join(f'<td style="text-align:{a}">{inline(c, **kw)}</td>' for c, a in zip(r, aligns))
                  + "</tr>" for r in body)
    return f'<div class="table"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def render(md, base="", site_prefix="", images=None, image_prefix=""):
    """images: a list that collects (repository path, alt) for each image, which the caller copies into site/."""
    kw = {"base": base, "site_prefix": site_prefix}
    parts, title = [], "Findings"
    for kind, lines in blocks(md.splitlines()):
        if kind == "heading":
            level = len(lines[0]) - len(lines[0].lstrip("#"))
            text = lines[0][level:].strip()
            if level == 1:
                title = text
            parts.append(f"<h{level}>{inline(text, **kw)}</h{level}>")
        elif kind == "table":
            parts.append(render_table(lines, **kw))
        elif kind in ("list", "olist"):
            parts.append(render_list(lines, ordered=kind == "olist", **kw))
        elif kind == "image":
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", lines[0])
            if re.match(r"https?://", m.group(2)):
                src = m.group(2)
            else:
                path = posixpath.normpath(posixpath.join(base, m.group(2)))
                if not (ROOT / path).exists():
                    print(f"warning: image {path} not found; left out")
                    continue
                if images is not None:
                    images.append(path)
                src = image_prefix + posixpath.basename(path)
            parts.append(f'<figure><a href="{html.escape(src)}"><img src="{html.escape(src)}" '
                         f'alt="{html.escape(m.group(1))}"></a></figure>')
        else:
            parts.append(f"<p>{inline(' '.join(l.strip() for l in lines), **kw)}</p>")
    return title, "\n".join(parts)


def one_line(md):
    """The paragraph under a study's "In one line" heading, or None."""
    m = re.search(r"^## In one line\s*\n+((?:[^#\n|].*\n?)+)", md, re.M)
    return " ".join(l.strip() for l in m.group(1).splitlines()) if m else None


STYLE = """
:root{--bg:#fafaf9;--fg:#1c1917;--muted:#57534e;--line:#e7e5e4;--card:#fff;--accent:#1e3a8a}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0c0a09;--fg:#f5f5f4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#93c5fd}}
:root[data-theme="dark"]{--bg:#0c0a09;--fg:#f5f5f4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#93c5fd}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 16px 72px}h1{font-size:clamp(30px,6vw,44px);line-height:1.15;margin:0 0 12px;letter-spacing:-.02em}
h2{font-size:24px;margin:44px 0 12px;letter-spacing:-.01em}h3{font-size:19px;margin:32px 0 8px}
p,li{max-width:70ch}a{color:var(--accent)}ul,ol{padding-left:22px}li{margin:4px 0}
h1+p{color:var(--muted)}nav{font-size:15px;margin-bottom:28px}
.table{overflow-x:auto;margin:16px 0}table{border-collapse:collapse;width:100%;font-size:15px;background:var(--card)}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{font-weight:600}
figure{margin:16px 0}img{max-width:100%;height:auto;background:#fff;border-radius:6px}
.study{border-bottom:1px solid var(--line);padding:14px 0}.study h3{margin:0 0 4px}.study p{margin:0;color:var(--muted)}
code{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--card);border:1px solid var(--line);border-radius:4px;padding:1px 4px}
"""


def page(title, description, nav, body):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<style>{STYLE}</style></head><body><main>
<nav>{nav}</nav>
{body}
</main></body></html>
"""


def nav(prefix, here):
    links = [("index.html", "Repo Market Watch"), ("findings.html", "Findings"), ("studies.html", "All studies")]
    return " · ".join(html.escape(label) if label == here else f'<a href="{prefix}{url}">{label}</a>'
                      for url, label in links)


def signed(value, fmt="+.0f"):
    return "n/a" if value is None else format(value, fmt).replace("-", "−")


def study10_page(status, min_shocks):
    """Study 10 scores events as they happen, so its page is its current status, from status.json."""
    a, b, c = status["A_clearing_deadlines"], status["B_credit_lead"], status["C_chain_under_stress"]
    rows = []
    for key, label in (("D1_cash_clearing", "Cash Treasury clearing"), ("D2_repo_clearing", "Repo clearing")):
        d = a[key]
        comps = "; ".join(f"{day}: SOFR − IORB change {signed(v.get('d_spread_bp'))} bp"
                          for day, v in d["comparators"].items())
        where = (f"Scored against the same days in earlier years ({comps})." if d.get("verdict")
                 else f"Scored after the deadline's window closes. Comparators: {comps}.")
        rows.append((f"{label}, deadline {d['deadline']}", d.get("verdict") or "pending", where))
    rows.append(("Credit after repo shocks", b.get("verdict") or "pending",
                 f"New repo shocks since {b['from']}: {b['n_shock_days']} (the test needs {min_shocks})."))
    ref = c.get("reference_april_2025") or {}
    now = (f"Stress event from {c['onset']}." if c.get("onset") else "No stress event since the test was set.")
    ref_text = (f" For reference, April 2025 scored the same way: {ref['verdict']} (repo peaked at "
                f"{signed(ref.get('C1_max_noncal_spread_bp'), '.0f')} bp on ordinary days; the 10-year swap spread "
                f"moved {signed(ref.get('C3_swap_spread_change_bp'))} bp).") if ref.get("verdict") else ""
    rows.append(("The chain under the next stress", c.get("verdict") or "pending", now + ref_text))
    trs = "".join(f"<tr><td>{html.escape(t)}</td><td><b>{html.escape(v)}</b></td><td>{html.escape(n)}</td></tr>"
                  for t, v, n in rows)
    pending = sum(v == "pending" for _, v, _ in rows)
    state = ("None has a verdict yet: each waits for its event." if pending == len(rows)
             else f"{len(rows) - pending} of {len(rows)} have a verdict; the rest wait for their events.")
    body = (f"<h1>Study 10: three prospective tests</h1><p>Status as of {status['run_date']}, data to "
            f"{status['data_to']}. Updated every week by the watch.</p>"
            "<p>These tests were written down, with the code that scores them, before the events they test: the "
            "clearing deadlines of 31 December 2026 and 30 June 2027, the next repo shocks, and the next stress "
            f"event. {state} Each verdict appears here when it is scored, whatever it says.</p>"
            '<div class="table"><table><thead><tr><th>Test</th><th>Verdict</th><th>Where it stands</th></tr></thead>'
            f"<tbody>{trs}</tbody></table></div>"
            f'<p><a href="{REPO}docs/design-study-10-prospective.md">The design</a> sets what each test measures and '
            f'what would count. <a href="{REPO}results/study-10/status.json">The full status</a>, with every '
            "measure, is on GitHub.</p>")
    return page("Study 10: three prospective tests", "Pre-registered tests of the clearing deadlines and the next "
                "stress, with their current status.", nav("../", ""), body)


def readme_results():
    """Study directory -> the one-line result from README.md's results table."""
    out = {}
    for line in (ROOT / "README.md").read_text().splitlines():
        m = re.match(r"\| \[[^\]]+\]\(results/([\w-]+)/result\.md\) \|[^|]*\| (.*) \|$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def plain(text):
    """Markdown inline text as plain text, for a page's description."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\*\*|`|(?<![*\w])\*(?!\s)|(?<!\s)\*(?![*\w])", "", text)


def study_number(name):
    """Sort key: the first number in a study's directory name, then the name; unnumbered studies go last."""
    m = re.search(r"(\d+)", name)
    return (int(m.group(1)) if m else 9999, name)


def main():
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    title, body = render((ROOT / "SYNTHESIS.md").read_text())
    (site / "findings.html").write_text(page("Repo Market Findings", f"{title} What public data shows about the US "
                                             "repo market and warning signs, 2018-2026.", nav("", "Findings"), body))
    studies = site / "studies"
    if studies.exists():
        shutil.rmtree(studies)
    studies.mkdir()
    summaries = readme_results()
    entries = []
    for path in sorted((ROOT / "results").glob("*/result.md"), key=lambda p: study_number(p.parent.name)):
        name = path.parent.name
        md = path.read_text()
        images = []
        title, body = render(md, base=f"results/{name}", site_prefix="../", images=images, image_prefix=f"{name}-")
        for img in images:
            shutil.copy(ROOT / img, studies / f"{name}-{posixpath.basename(img)}")
        source = f'<p><a href="{REPO}results/{name}/result.md">Source on GitHub</a>, with its design, code and data.</p>'
        summary = summaries.get(name) or one_line(md)
        (studies / f"{name}.html").write_text(page(title.removesuffix(" — result").removesuffix(": result"),
                                                   plain(summary or title), nav("../", ""), body + source))
        entries.append((name, title.removesuffix(" — result").removesuffix(": result"), f"studies/{name}.html", summary))
    status_path = ROOT / "results" / "study-10" / "status.json"
    if status_path.exists():
        (studies / "study-10.html").write_text(study10_page(json.loads(status_path.read_text()), LEAD_MIN_SHOCKS))
        entries.append(("study-10", "Study 10: three prospective tests", "studies/study-10.html",
                        "Tests set on 26 October 2026, with the code that scores them, before their data exists: the "
                        "clearing deadlines, the credit lead, and the chain under the next stress. No result yet, by "
                        "design; this page shows where each stands."))
    entries.sort(key=lambda e: study_number(e[0]))
    items = "".join(f'<div class="study"><h3><a href="{html.escape(url)}">{inline(t)}</a></h3>'
                    + (f"<p>{inline(line)}</p>" if line else "") + "</div>" for _, t, url, line in entries)
    body = ("<h1>All studies</h1><p>Every study in the project, each designed and committed before its data was "
            "examined. Start with <a href=\"findings.html\">the findings</a> for the overall picture.</p>" + items)
    (site / "studies.html").write_text(page("Repo Market Studies", "Every study of the repo-market-spillovers project, "
                                            "with its result.", nav("", "All studies"), body))
    print(f"wrote site/findings.html, site/studies.html and {len(entries)} study pages")


if __name__ == "__main__":
    main()
