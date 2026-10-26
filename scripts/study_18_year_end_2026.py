"""Study 18: year-end 2026, set down in advance.

Design: docs/design-study-18-year-end-2026.md, committed with this code, before the event; both are frozen.
Run weekly by .github/workflows/watch.yml. Fetches into data/raw/s18/ and writes results/study-18/status.json and
results/study-18/result.md ("pending" until the fifth business day of 2027 has data).
"""
import csv
import datetime as dt
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "s18"
OUT = ROOT / "results" / "study-18"
FRED = ("SOFR", "SOFR99", "IORB", "DFEDTARU")
TURNS = {"2025_26": ("2025", "2026"), "2026_27": ("2026", "2027")}
FORECASTS = {"T1": "held", "T2": "breached", "T3": "milder"}
RP_URL = ("https://markets.newyorkfed.org/api/rp/results/search.json?startDate={a}&endDate={b}"
          "&operationTypes=Repo")


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    for s in FRED:
        with urllib.request.urlopen(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}", timeout=180) as r:
            (RAW / f"{s}.csv").write_bytes(r.read())
    for key, (y0, y1) in TURNS.items():
        url = RP_URL.format(a=f"{y0}-12-20", b=f"{y1}-01-10")
        with urllib.request.urlopen(url, timeout=180) as r:
            (RAW / f"rp_{key}.json").write_bytes(r.read())


def fred(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def as_of(series, day):
    keys = [k for k in series if k <= day]
    return series[max(keys)] if keys else None


def turn_days(sofr_dates, y0, y1):
    """The last business day of y0 and the first of y1, by SOFR observations; None until both exist."""
    last = [d for d in sofr_dates if d.startswith(y0)]
    first = [d for d in sofr_dates if d.startswith(y1)]
    return (max(last), min(first)) if last and first and max(last) >= f"{y0}-12-24" else None


def gap_bp(rate, line):
    """How far a rate closed above the line, in bp; zero if at or below it."""
    return max(0.0, round((rate - line) * 100, 1))


def takeup(key, days):
    """Standing repo take-up ($bn) on each turn day, from the operation results."""
    path = RAW / f"rp_{key}.json"
    if not path.exists():
        return None
    ops = json.loads(path.read_text()).get("repo", {}).get("operations", [])
    out = {}
    for d in days:
        out[d] = round(sum(float(o.get("totalAmtAccepted", 0) or 0) for o in ops if o.get("operationDate") == d) / 1e9, 2)
    return out


def score(data, today):
    sofr, s99, iorb, top = data
    dates = sorted(sofr)
    out = {"design": "docs/design-study-18-year-end-2026.md", "run_date": today, "data_to": dates[-1],
           "forecasts": FORECASTS, "turns": {}}
    for key, (y0, y1) in TURNS.items():
        days = turn_days(dates, y0, y1)
        if days is None:
            out["turns"][key] = {"status": "pending"}
            continue
        rows = {}
        for d in days:
            line = as_of(top, d)
            rows[d] = {"line_pct": line, "iorb_plus_10_pct": round(as_of(iorb, d) + 0.10, 2),
                       "sofr_gap_bp": gap_bp(sofr[d], line),
                       "sofr99_gap_bp": gap_bp(s99[d], line) if d in s99 else None}
        out["turns"][key] = {"status": "measured", "days": rows, "takeup_bn": takeup(key, days),
                             "max_sofr_gap_bp": max(r["sofr_gap_bp"] for r in rows.values()),
                             "max_sofr99_gap_bp": max((r["sofr99_gap_bp"] or 0.0) for r in rows.values())}
    target = out["turns"]["2026_27"]
    settle = sorted(d for d in dates if d.startswith("2027"))
    if target["status"] != "measured" or len(settle) < 5 or any(r["sofr99_gap_bp"] is None for r in target["days"].values()):
        out["status"] = "pending"
        return out
    prev = out["turns"]["2025_26"]
    t1 = "breached" if target["max_sofr_gap_bp"] > 0 else "held"
    t2 = "breached" if target["max_sofr99_gap_bp"] > 0 else "held"
    diff = target["max_sofr_gap_bp"] - prev["max_sofr_gap_bp"]
    t3 = "milder" if diff <= -2 else "worse" if diff >= 2 else "similar"
    out.update({"status": "scored", "T1": t1, "T2": t2, "T3": t3, "T3_difference_bp": round(diff, 1),
                "forecasts_right": {k: out_v == FORECASTS[k] for k, out_v in (("T1", t1), ("T2", t2), ("T3", t3))}})
    return out


def page(status):
    head = ("# Study 18: year-end 2026, set down in advance\n\n"
            "Design: [`docs/design-study-18-year-end-2026.md`](../../docs/design-study-18-year-end-2026.md), "
            "committed with the scoring code on 26 October 2026, before the event. This page is rewritten by the "
            f"weekly watch. Status as of {status['run_date']}, data to {status['data_to']}.\n\n")
    forecasts = ("## Forecasts made on 26 October 2026\n\n"
                 "- **T1, the benchmark:** held (SOFR stays at or below the standing repo facility's rate on both turn days).\n"
                 "- **T2, the top of the market:** breached (SOFR's 99th percentile goes above it on at least one).\n"
                 "- **T3, against the 2025 turn:** milder.\n\n")
    if status["status"] != "scored":
        body = ("## In one line\n\nPending. The turn from 2026 to 2027 combines the first year-end with the facility at "
                "full allotment from the start, the deadline for clearing cash Treasury trades and the banks' "
                "year-end capital snapshot. It is scored once the fifth business day of 2027 has data.\n\n")
    else:
        right = status["forecasts_right"]
        body = (f"## In one line\n\nT1 **{status['T1']}**, T2 **{status['T2']}**, T3 **{status['T3']}** "
                f"({status['T3_difference_bp']:+.1f} bp against the 2025 turn). Forecasts right: "
                f"{sum(right.values())} of 3.\n\n")
    rows = ["| Turn | Day | Line (%) | SOFR above the line (bp) | 99th percentile above the line (bp) |",
            "|---|---|---:|---:|---:|"]
    for key, t in status["turns"].items():
        if t["status"] == "measured":
            for d, r in t["days"].items():
                p99 = "–" if r["sofr99_gap_bp"] is None else f"{r['sofr99_gap_bp']:.1f}"
                rows.append(f"| {key.replace('_', '/')} | {d} | {r['line_pct']:.2f} | {r['sofr_gap_bp']:.1f} | {p99} |")
    table = "## The turns\n\n" + "\n".join(rows) + "\n" if len(rows) > 2 else ""
    return head + body + forecasts + table


def run(today=None):
    data = tuple(fred(s) for s in FRED)
    status = score(data, today or dt.date.today().isoformat())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "status.json").write_text(json.dumps(status, indent=1) + "\n")
    (OUT / "result.md").write_text(page(status))
    return status


if __name__ == "__main__":
    if "--no-fetch" not in sys.argv:
        fetch()
    print(json.dumps(run(), indent=1))
