"""Study 21: the reserves-to-debt gauge, tested on months that have not happened yet.

Design: docs/design-study-21-reserves-to-debt-gauge.md, committed with this code on 27 October 2026; both are frozen.
Run weekly by .github/workflows/watch.yml (before watch.py, which shows the gauge). Fetches into data/raw/s21/ and
writes results/study-21/status.json and results/study-21/result.md.
"""
import bisect
import csv
import datetime as dt
import json
import pathlib
import statistics
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "s21"
OUT = ROOT / "results" / "study-21"
FRED = ("WRESBAL", "FYGFDPUN", "SOFR", "DFEDTARU")
SCARCE_BELOW, AMPLE_FROM = 10.0, 11.0
B_LINE, J_LINE = -15.0, 3.0
FIRST_MONTH, LAST_MONTH = "2026-11", "2027-12"
PUBLICATION_LAG_MONTHS = 5  # a quarter's debt figure is treated as public five months after the quarter starts


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    for s in FRED:
        with urllib.request.urlopen(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}", timeout=180) as r:
            (RAW / f"{s}.csv").write_bytes(r.read())


def read(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def month_add(month, n):
    y, m = int(month[:4]), int(month[5:7]) + n
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


def public_debt(debt):
    """Date -> the latest quarterly debt figure public by then (quarter start + PUBLICATION_LAG_MONTHS)."""
    avail = sorted((month_add(q[:7], PUBLICATION_LAG_MONTHS) + "-01", v) for q, v in debt.items())
    keys = [a for a, _ in avail]
    return lambda d: avail[bisect.bisect_right(keys, d) - 1][1] if bisect.bisect_right(keys, d) else None


def gauge(reserves, debt):
    """Week -> reserves over debt held by the public, in %."""
    pub = public_debt(debt)
    return {w: r / pub(w) * 100 for w, r in reserves.items() if pub(w)}


def zone(ratio):
    return "scarce" if ratio < SCARCE_BELOW else "ample" if ratio >= AMPLE_FROM else "no call"


def month_measures(sofr, top):
    """Month -> (B, J), study 17's measures with every month kept; needs the next month's first business day."""
    days = sorted(d for d in sofr if top(d) is not None)
    s = {d: (sofr[d] - top(d)) * 100 for d in days}
    by = {}
    for d in days:
        by.setdefault(d[:7], []).append(d)
    keys = sorted(by)
    out = {}
    for i, m in enumerate(keys[:-1]):
        ds, nxt = by[m], by[keys[i + 1]]
        if len(ds) < 15:
            continue
        base = statistics.median(s[d] for d in ds[5:15])
        out[m] = (round(base, 2), round((s[ds[-1]] + s[nxt[0]]) / 2 - base, 2))
    return out


def score(weekly, measures, today):
    monthly = {}
    for w, v in weekly.items():
        monthly.setdefault(w[:7], []).append(v)
    monthly = {m: round(statistics.fmean(v), 2) for m, v in monthly.items()}
    rows = []
    m = FIRST_MONTH
    while m <= LAST_MONTH:
        if m in monthly and m in measures:
            z = zone(monthly[m])
            b, j = measures[m]
            match = None
            if z == "scarce":
                match = b > B_LINE and j > J_LINE
            elif z == "ample":
                match = b <= B_LINE and j <= J_LINE
            rows.append({"month": m, "gauge_pct": monthly[m], "zone": z, "B_bp": b, "J_bp": j, "match": match})
        m = month_add(m, 1)
    zoned = [r for r in rows if r["zone"] != "no call"]
    share = round(sum(r["match"] for r in zoned) / len(zoned) * 100, 1) if zoned else None
    final = today >= "2028-01-15"
    if len(zoned) < 6:
        verdict = "inconclusive" if final else "pending"
    else:
        verdict = "the gauge holds" if share >= 75 else "the gauge fails" if share <= 50 else "inconclusive"
        if not final:
            verdict += " (interim)"
    latest = max(weekly)
    return {"design": "docs/design-study-21-reserves-to-debt-gauge.md", "run_date": today,
            "latest_week": latest, "latest_gauge_pct": round(weekly[latest], 2), "latest_zone": zone(weekly[latest]),
            "recent_months": {k: monthly[k] for k in sorted(monthly)[-6:]},
            "scored_months": rows, "zone_months": len(zoned),
            "zones": {z: sum(r["zone"] == z for r in rows) for z in ("scarce", "ample", "no call")},
            "match_share_pct": share, "verdict": verdict}


def page(st):
    lines = ["# Study 21: the reserves-to-debt gauge", "",
             "Design: [`docs/design-study-21-reserves-to-debt-gauge.md`](../../docs/design-study-21-reserves-to-debt-gauge.md), "
             "committed with the scoring code on 27 October 2026. This page is rewritten by the weekly watch. "
             f"Status as of {st['run_date']}.", "",
             "## In one line", "",
             f"Reserves were **{st['latest_gauge_pct']:.1f}%** of federal debt held by the public in the week of "
             f"{st['latest_week']}: the **{st['latest_zone']}** zone (below 10% scarce, 11% or more ample). Verdict so far: "
             f"**{st['verdict']}** ({st['zone_months']} zone months scored from November 2026).", "",
             "## What is being tested", "",
             "Study 20 found that repo got tight when reserves fell to about a tenth of the debt, in 2018–19 and in "
             "2025–26. This tests it on months that had not happened when the design was written. In a scarce month, "
             "ordinary-day repo should trade above −15 bp against the top of the Fed's range and month-ends should jump "
             "more than 3 bp. In an ample month, neither. The gauge holds if at least 75% of zone months match.", ""]
    if st["scored_months"]:
        lines += ["| Month | Gauge | Zone | Ordinary days (bp) | Month-end jump (bp) | Match |", "|---|---:|---|---:|---:|---|"]
        for r in st["scored_months"]:
            lines.append(f"| {r['month']} | {r['gauge_pct']:.2f}% | {r['zone']} | {r['B_bp']:.1f} | {r['J_bp']:.1f} | "
                         f"{'–' if r['match'] is None else 'yes' if r['match'] else 'no'} |")
    else:
        lines += ["No month has been scored yet: November 2026 is scored once December's first business day has data."]
    return "\n".join(lines) + "\n"


def run(today=None):
    reserves, debt, sofr, top_raw = (read(s) for s in FRED)
    keys = sorted(top_raw)
    top = lambda d: top_raw[keys[bisect.bisect_right(keys, d) - 1]] if bisect.bisect_right(keys, d) else None  # noqa: E731
    st = score(gauge(reserves, debt), month_measures(sofr, top), today or dt.date.today().isoformat())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "status.json").write_text(json.dumps(st, indent=1) + "\n")
    (OUT / "result.md").write_text(page(st))
    return st


if __name__ == "__main__":
    if "--no-fetch" not in sys.argv:
        fetch()
    print(json.dumps({k: v for k, v in run().items() if k != "scored_months"}, indent=1))
