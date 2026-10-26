"""Render SYNTHESIS.md as site/findings.html, in the watch page's style.

A small converter for the Markdown subset SYNTHESIS.md uses: headings, paragraphs, bullet lists (one nested level,
continuation lines), tables, bold, italics and links. Links into the repository become GitHub links, since the site
serves only site/.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = "https://github.com/eleonorabjornberg/repo-market-spillovers/blob/main/"


def inline(text):
    text = html.escape(text, quote=False)

    def link(m):
        label, url = m.group(1), m.group(2)
        if not re.match(r"https?://|index\.html$|#", url):
            url = REPO + url
        return f'<a href="{html.escape(url)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
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
        elif line.startswith("- "):
            j = i
            while j < len(lines) and lines[j].strip() and (lines[j].startswith("- ") or lines[j].startswith("  ")):
                j += 1
            out.append(("list", lines[i:j]))
            i = j
        else:
            j = i
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(("#", "|", "- ")):
                j += 1
            out.append(("paragraph", lines[i:j]))
            i = j
    return out


def render_list(lines):
    items = []  # [text, [subitems]]
    for line in lines:
        if line.startswith("- "):
            items.append([line[2:], []])
        elif line.startswith("  - "):
            items[-1][1].append(line[4:])
        elif line.startswith("    ") and items[-1][1]:
            items[-1][1][-1] += " " + line.strip()
        else:
            items[-1][0] += " " + line.strip()
    parts = []
    for text, sub in items:
        nested = "<ul>" + "".join(f"<li>{inline(s)}</li>" for s in sub) + "</ul>" if sub else ""
        parts.append(f"<li>{inline(text)}{nested}</li>")
    return "<ul>" + "".join(parts) + "</ul>"


def render_table(lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    head, body = rows[0], [r for r in rows[2:]]
    aligns = ["right" if c.strip().endswith(":") else "left" for c in lines[1].strip().strip("|").split("|")]
    th = "".join(f'<th style="text-align:{a}">{inline(c)}</th>' for c, a in zip(head, aligns))
    trs = "".join("<tr>" + "".join(f'<td style="text-align:{a}">{inline(c)}</td>' for c, a in zip(r, aligns))
                  + "</tr>" for r in body)
    return f'<div class="table"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def render(md):
    parts, title = [], "Findings"
    for kind, lines in blocks(md.splitlines()):
        if kind == "heading":
            level = len(lines[0]) - len(lines[0].lstrip("#"))
            text = lines[0][level:].strip()
            if level == 1:
                title = text
            parts.append(f"<h{level}>{inline(text)}</h{level}>")
        elif kind == "table":
            parts.append(render_table(lines))
        elif kind == "list":
            parts.append(render_list(lines))
        else:
            parts.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return title, "\n".join(parts)


STYLE = """
:root{--bg:#fafaf9;--fg:#1c1917;--muted:#57534e;--line:#e7e5e4;--card:#fff;--accent:#1e3a8a}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0c0a09;--fg:#f5f5f4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#93c5fd}}
:root[data-theme="dark"]{--bg:#0c0a09;--fg:#f5f5f4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#93c5fd}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 16px 72px}h1{font-size:clamp(30px,6vw,44px);line-height:1.15;margin:0 0 12px;letter-spacing:-.02em}
h2{font-size:24px;margin:44px 0 12px;letter-spacing:-.01em}h3{font-size:19px;margin:32px 0 8px}
p,li{max-width:70ch}a{color:var(--accent)}ul{padding-left:22px}li{margin:4px 0}
h1+p{color:var(--muted)}nav{font-size:15px;margin-bottom:28px}
.table{overflow-x:auto;margin:16px 0}table{border-collapse:collapse;width:100%;font-size:15px;background:var(--card)}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{font-weight:600}
code{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--card);border:1px solid var(--line);border-radius:4px;padding:1px 4px}
"""


def main():
    title, body = render((ROOT / "SYNTHESIS.md").read_text())
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Repo Market Findings</title>
<meta name="description" content="{html.escape(title)} What public data shows about the US repo market and warning signs, 2018-2026.">
<style>{STYLE}</style></head><body><main>
<nav><a href="index.html">Repo Market Watch</a> · Findings</nav>
{body}
</main></body></html>
"""
    (ROOT / "site").mkdir(exist_ok=True)
    (ROOT / "site" / "findings.html").write_text(page)
    print("wrote site/findings.html")


if __name__ == "__main__":
    main()
