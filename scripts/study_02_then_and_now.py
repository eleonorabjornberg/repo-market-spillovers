"""Study 02: then and now. Where do today's repo and bond-market indicators stand against 2000 and 2007, and would
they have warned?

Design: docs/design-study-02-then-and-now.md (committed before the first run).
Inputs: data/raw/long/ (scripts/fetch_long.py). Writes results/study-02/result.json and chart.svg.
"""
import csv
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spillovers import history as h  # noqa: E402

RAW = ROOT / "data" / "raw" / "long"
OUT = ROOT / "results" / "study-02"
REFERENCE = {"2000-03": "Dot-com peak", "2007-07": "Before the 2007 repo run", "2008-08": "Before Lehman",
             "2019-08": "Before the 2019 repo spike", "2020-02": "Before COVID"}
ENDED = {"ted_bp"}  # series that stopped before today
# checks added after the first run's numbers were seen: reported apart, as post hoc
POST_HOC_CHECKS = {"baa_10y_bp": "low"}


def read_daily(source):
    """date -> float for one source."""
    if source.startswith("OFR:"):
        col = source.split(":", 1)[1]
        with open(RAW / "OFR_FSI.csv", newline="") as f:
            return {r["Date"]: float(r[col]) for r in csv.DictReader(f) if r[col]}
    if source.startswith("OFRHF:"):
        mnemonic = source.split(":", 1)[1]
        return {d: float(v) for d, v in json.loads((RAW / f"OFRHF_{mnemonic}.json").read_text()) if v is not None}
    out = {}
    with open(RAW / f"{source}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def complete_months(daily, quarterly):
    return h.complete_months(daily, "quarterly" if quarterly else "daily")


def check_manifest():
    manifest = json.loads((ROOT / "metadata" / "long_manifest.json").read_text())
    stale = [n for n, m in manifest.items() if hashlib.sha256((RAW / n).read_bytes()).hexdigest() != m["sha256"]]
    if stale:
        raise ValueError(f"data/raw/long differs from metadata/long_manifest.json for {stale}: re-run fetch_long.py")


def main():
    check_manifest()
    ids = {s for spec in h.INDICATORS.values() for s in (spec.get("num"), spec.get("den"), spec.get("minus")) if s}
    sources = {s: complete_months(read_daily(s), s in h.QUARTERLY) for s in ids}
    series = {name: h.build_indicator(spec, sources) for name, spec in h.INDICATORS.items()}

    today = min(max(s) for name, s in series.items() if name not in ENDED)
    nfci_weekly = read_daily("NFCI")
    onsets = h.stress_onsets(nfci_weekly)
    onset_months = sorted({d[:7] for d in onsets})
    last_nfci_month = max(complete_months(nfci_weekly, False))

    rows = []
    for name, spec in h.INDICATORS.items():
        s = series[name]
        row = {"indicator": name, "label": spec["label"], "group": spec["group"], "warn": spec["warn"],
               "from": min(s), "to": max(s)}
        for month, label in REFERENCE.items():
            v = s.get(month)
            row[month] = None if v is None else {"value": round(v, 3), "pct": round(h.percentile_of(s, v), 1)}
        v = s.get(today)
        row["today"] = None if v is None else {"month": today, "value": round(v, 3),
                                               "pct": round(h.percentile_of(s, v), 1)}
        latest = max(s)
        row["latest"] = {"month": latest, "value": round(s[latest], 3), "pct": round(h.percentile_of(s, s[latest]), 1),
                         "highest_since": max((m for m in s if m < latest and s[m] >= s[latest]), default=None),
                         "lowest_since": max((m for m in s if m < latest and s[m] <= s[latest]), default=None)}
        if spec["warn"] and v is not None:
            check = h.warning_check(s, v, spec["warn"], onset_months, last_month=last_nfci_month)
            row["check"] = {k: (round(x, 3) if isinstance(x, float) else x) for k, x in check.items()}
        if name in POST_HOC_CHECKS and v is not None:
            check = h.warning_check(s, v, POST_HOC_CHECKS[name], onset_months, last_month=last_nfci_month)
            row["post_hoc_check"] = {"direction": POST_HOC_CHECKS[name],
                                     **{k: (round(x, 3) if isinstance(x, float) else x) for k, x in check.items()}}
        rows.append(row)

    result = {"design": "docs/design-study-02-then-and-now.md", "manifest": "metadata/long_manifest.json",
              "today": today, "reference": REFERENCE, "stress_onsets": onsets,
              "check_window": {"from": "1990-01", "horizon_months": 24, "last_month_with_full_horizon":
                               h.month_add(last_nfci_month, -24)}, "indicators": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    (OUT / "chart.svg").write_text(chart(series, nfci_weekly, today))
    print("today:", today, "| stress onsets:", onsets)
    for r in rows:
        ref = "  ".join(f"{m}:{r[m]['pct']:5.1f}" if r[m] else f"{m}:   - " for m in REFERENCE)
        t = f"{r['today']['value']:8.2f} p{r['today']['pct']:5.1f}" if r["today"] else "      -        "
        lt = f"{r['latest']['month']} {r['latest']['value']:8.2f} p{r['latest']['pct']:5.1f}"
        c = r.get("check")
        cs = "" if not c else (f"warn n={c['warning_months']} followed={c['share_followed']} base={c['base_share']}")
        print(f"{r['indicator']:15} {ref} | today {t} | latest {lt} | {cs}")


def chart(series, nfci_weekly, today):
    """Small multiples, 1990 onwards: each indicator's monthly path, stress spells (NFCI > 0) shaded, reference
    months marked, and today's reading as a dot."""
    names = [n for n in h.INDICATORS if n != "nfci"] + ["nfci"]
    cols, pw, ph = 3, 330, 150
    rows_n = (len(names) + cols - 1) // cols
    w, top = cols * pw + 20, 64
    hgt = top + rows_n * (ph + 46) + 30
    start, end = "1990-01", max(max(s) for s in series.values())

    def mx(month, x0):
        y, m = int(month[:4]), int(month[5:7])
        y0, m0 = int(start[:4]), int(start[5:7])
        y1, m1 = int(end[:4]), int(end[5:7])
        span = (y1 - y0) * 12 + m1 - m0
        return x0 + 40 + ((y - y0) * 12 + m - m0) / span * (pw - 56)

    stress = sorted(m for m, v in h.to_monthly(nfci_weekly).items() if v > 0 and m >= start)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {hgt}" font-family="sans-serif" font-size="11">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<text x="10" y="22" font-size="15" font-weight="bold">Repo and bond-market indicators, 1990 to today</text>',
           '<text x="10" y="40" fill="#555">Grey bands: financial stress (Chicago Fed NFCI above 0). Dashed lines: March 2000, '
           'July 2007, August 2008, August 2019, February 2020. Red dot: latest reading.</text>']
    for i, name in enumerate(names):
        s = {m: v for m, v in series[name].items() if m >= start}
        if not s:
            continue
        x0 = 10 + (i % cols) * pw
        y0 = top + (i // cols) * (ph + 46)
        lo, hi = min(s.values()), max(s.values())
        pad = (hi - lo) * 0.08 or 1
        lo, hi = lo - pad, hi + pad
        y = lambda v: y0 + 22 + (hi - v) / (hi - lo) * (ph - 30)  # noqa: E731
        out.append(f'<text x="{x0 + 40}" y="{y0 + 12}" font-weight="bold">{h.INDICATORS[name]["label"]}</text>')
        for m in stress:
            out.append(f'<rect x="{mx(m, x0):.1f}" y="{y0 + 20}" width="{(pw - 56) / 440:.2f}" height="{ph - 26}" '
                       f'fill="#e5e7eb"/>')
        for m in REFERENCE:
            out.append(f'<line x1="{mx(m, x0):.1f}" x2="{mx(m, x0):.1f}" y1="{y0 + 20}" y2="{y0 + ph - 6}" '
                       f'stroke="#9ca3af" stroke-dasharray="2,2"/>')
        if lo < 0 < hi:
            out.append(f'<line x1="{x0 + 40}" x2="{x0 + pw - 16}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="#d1d5db"/>')
        months = sorted(s)
        pts = " ".join(f"{mx(m, x0):.1f},{y(s[m]):.1f}" for m in months)
        out.append(f'<polyline points="{pts}" fill="none" stroke="#1e3a8a" stroke-width="1.2"/>')
        last = months[-1]
        out.append(f'<circle cx="{mx(last, x0):.1f}" cy="{y(s[last]):.1f}" r="3.5" fill="#dc2626"/>')
        for v in (lo + pad, hi - pad):
            out.append(f'<text x="{x0 + 36}" y="{y(v) + 4:.1f}" text-anchor="end" fill="#555">{v:.1f}</text>')
        for yr in ("1990", "2000", "2010", "2020"):
            out.append(f'<text x="{mx(yr + "-01", x0):.1f}" y="{y0 + ph + 8}" text-anchor="middle" fill="#555">{yr}</text>')
    out.append("</svg>\n")
    return "\n".join(out)


if __name__ == "__main__":
    main()
