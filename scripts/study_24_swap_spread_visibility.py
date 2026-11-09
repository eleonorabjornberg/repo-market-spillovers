"""Study 24: can public data see the swap-spread trade?

Design: docs/design-study-24-swap-spread-visibility.md (committed before this study's data was fetched).
Reads data/raw/s24/ (written by scripts/fetch_study24.py, hashed in metadata/s24_manifest.json) and writes
results/study-24/result.json. Intervals are 90% percentile intervals, as the design states.
"""
import collections
import csv
import datetime as dt
import json
import math
import pathlib
import random
import statistics

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "s24"
OUT = ROOT / "results" / "study-24"
SEED, DRAWS = 20261109, 2000
Q1_QUARTERS = ["2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1", "2026Q2"]
Q1_THRESHOLD = 0.6


# ---------- small statistics ----------

def pct(sorted_xs, q):
    k = (len(sorted_xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(sorted_xs) - 1)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (k - lo)


def interval90(draws):
    s = sorted(d for d in draws if not math.isnan(d))
    return [pct(s, 0.05), pct(s, 0.95)] if s else [math.nan, math.nan]


def corr(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx, syy = sum((x - mx) ** 2 for x in xs), sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else math.nan


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(xs, ys):
    return corr(ranks(xs), ranks(ys))


def block_boot_corr(xs, ys, block, draws, rng):
    """Correlation with a 90% moving-block bootstrap interval (blocks of `block` consecutive pairs)."""
    n = len(xs)
    starts = list(range(n - block + 1))
    out = []
    for _ in range(draws):
        idx = []
        while len(idx) < n:
            s = rng.choice(starts)
            idx.extend(range(s, s + block))
        idx = idx[:n]
        out.append(corr([xs[i] for i in idx], [ys[i] for i in idx]))
    return corr(xs, ys), interval90(out)


# ---------- inputs ----------

def quarter(day):
    return f"{day[:4]}Q{(int(day[5:7]) - 1) // 3 + 1}"


def week(day):
    d = dt.date.fromisoformat(day)
    return (d - dt.timedelta(d.weekday())).isoformat()


def load_daily(path=None):
    """date -> category -> {"dv01", "capped_dv01", "trades"} summed over tenor buckets; and the by-bucket rows."""
    by = collections.defaultdict(lambda: collections.defaultdict(lambda: {"dv01": 0.0, "capped_dv01": 0.0, "trades": 0}))
    buckets = collections.defaultdict(float)
    with open(path or RAW / "daily.csv", newline="") as f:
        for r in csv.DictReader(f):
            t = by[r["date"]][r["category"]]
            t["dv01"] += float(r["dv01_musd"])
            t["capped_dv01"] += float(r["capped_dv01_musd"])
            t["trades"] += int(r["trades"])
            buckets[(r["date"][:7], r["category"], r["bucket"])] += float(r["dv01_musd"])
    return by, buckets


def ofr(mnemonic):
    return {d: v for d, v in json.loads((RAW / f"{mnemonic}.json").read_text()) if v is not None}


def dgs10():
    out = {}
    with open(RAW / "DGS10.csv", newline="") as f:
        for r in csv.DictReader(f):
            day = r.get("observation_date") or r.get("DATE")
            try:
                out[day] = float(r["DGS10"])
            except (ValueError, KeyError):
                continue
    return out


def rates10():
    with open(RAW / "daily_rates.csv", newline="") as f:
        return {r["date"]: float(r["median_fixed_rate"]) for r in csv.DictReader(f)}


# ---------- the questions ----------

def sums(by, key, cats=("single_spread",)):
    out = collections.defaultdict(float)
    for day, c in by.items():
        out[key(day)] += sum(c[k]["dv01"] for k in cats if k in c)
    return out


def total(c):
    return sum(v["dv01"] for v in c.values())


def q1(by, gne):
    flow = sums(by, quarter)
    q_end = {quarter(d): v for d, v in gne.items()}
    rows = []
    for q in Q1_QUARTERS:
        y, n = int(q[:4]), int(q[5])
        prev = f"{y}Q{n - 1}" if n > 1 else f"{y - 1}Q4"
        if q in flow and q in q_end and prev in q_end:
            rows.append({"quarter": q, "single_spread_dv01_musd": round(flow[q], 1),
                         "ird_gne_change_bn": round((q_end[q] - q_end[prev]) / 1e9, 1)})
    rho = spearman([r["single_spread_dv01_musd"] for r in rows], [r["ird_gne_change_bn"] for r in rows])
    return {"rows": rows, "spearman": round(rho, 3), "threshold": Q1_THRESHOLD, "quarters": len(rows),
            "tracks": bool(rho >= Q1_THRESHOLD)}


def weekly_shares(by, start, end):
    single, tot = collections.defaultdict(float), collections.defaultdict(float)
    for day, c in by.items():
        if start <= day <= end:
            single[week(day)] += c["single_spread"]["dv01"] if "single_spread" in c else 0.0
            tot[week(day)] += total(c)
    return {w: single[w] / tot[w] for w in sorted(tot) if tot[w]}


def q2(by, rng):
    base = weekly_shares(by, "2025-01-06", "2025-03-28")  # the whole weeks of January to March 2025
    april_days = [d for d in by if d.startswith("2025-04")]
    s = sum(by[d]["single_spread"]["dv01"] for d in april_days if "single_spread" in by[d])
    april = s / sum(total(by[d]) for d in april_days)
    april_weeks = weekly_shares(by, "2025-03-31", "2025-04-30")
    vals = list(base.values())
    boot = [statistics.fmean(rng.choices(vals, k=len(vals))) for _ in range(DRAWS)]
    ci = interval90(boot)
    return {"jan_mar_mean_weekly_share": round(statistics.fmean(vals), 4), "jan_mar_weeks": len(vals),
            "jan_mar_interval": [round(x, 4) for x in ci], "april_share": round(april, 4),
            "april_weekly_shares": {w: round(v, 4) for w, v in april_weeks.items()},
            "sees_unwind": bool(april > ci[1])}


def month_end_values(series):
    out = {}
    for d in sorted(series):
        out[d[:7]] = series[d]
    return out


def q3(by, tff, rng):
    flow = sums(by, lambda d: d[:7])
    me = month_end_values(tff)
    months = sorted(m for m in flow if m in me)
    pairs = []
    for a, b in zip(months, months[1:]):
        pairs.append((b, flow[b], (me[b] - me[a]) / 1e6))
    full = [p for p in pairs if p[0] < max(flow)]  # drop a final month the DTCC files do not cover in full
    r, ci = block_boot_corr([p[1] for p in full], [p[2] for p in full], 3, DRAWS, rng)
    return {"months": len(full), "corr": round(r, 3), "interval": [round(x, 3) for x in ci],
            "rows": [{"month": m, "single_spread_dv01_musd": round(f, 1), "lf_net_dv01_change_musd": round(c, 1)}
                     for m, f, c in full]}


def q4(by, rng):
    r10, y10 = rates10(), dgs10()
    spread = {d: (r10[d] * 100 - y10[d]) * 100 for d in r10 if d in y10}
    wk_spread = collections.defaultdict(list)
    for d, v in spread.items():
        wk_spread[week(d)].append(v)
    wk_mean = {w: statistics.fmean(v) for w, v in wk_spread.items()}
    flow = sums(by, week)
    weeks = sorted(w for w in wk_mean if w in flow)
    xs, ys = [], []
    for a, b in zip(weeks, weeks[1:]):
        xs.append(flow[b])
        ys.append(wk_mean[b] - wk_mean[a])
    r, ci = block_boot_corr(xs, ys, 4, DRAWS, rng)
    level = [round(wk_mean[w], 1) for w in weeks]
    return {"weeks": len(xs), "corr": round(r, 3), "interval": [round(x, 3) for x in ci],
            "spread_10y_bp_first": level[0], "spread_10y_bp_last": level[-1],
            "spread_10y_bp_min": min(level), "spread_10y_bp_max": max(level),
            "first_week": weeks[0], "last_week": weeks[-1]}


def q5(by):
    tot = sum(total(c) for c in by.values())
    capped = sum(v["capped_dv01"] for c in by.values() for v in c.values())
    single = sum(c["single_spread"]["dv01"] for c in by.values() if "single_spread" in c)
    single_capped = sum(c["single_spread"]["capped_dv01"] for c in by.values() if "single_spread" in c)
    pk = {k: sum(c[k]["trades"] for c in by.values() if k in c) for k in ("single_spread", "curve_spread", "package_no_spread")}
    return {"capped_share_of_dv01": round(capped / tot, 4),
            "single_spread_capped_share_of_dv01": round(single_capped / single, 4),
            "package_trades_without_spread_share": round(pk["package_no_spread"] / sum(pk.values()), 4),
            "single_spread_share_of_dv01": round(single / tot, 4)}


def describe(by, buckets, tff):
    months = sorted({d[:7] for d in by})
    full = months[1:-1] if len(months) > 2 else months  # first and last months may be partial
    flow = sums(by, lambda d: d[:7])
    share = {}
    for m in full:
        days = [d for d in by if d.startswith(m)]
        share[m] = sum(by[d]["single_spread"]["dv01"] for d in days if "single_spread" in by[d]) / \
            sum(total(by[d]) for d in days)
    first, last = full[:3], full[-3:]
    tb = {}
    for b in ("1.5-4y", "4-8y", "8-15y", "15-31y"):
        tb[b] = {"first3": round(sum(buckets.get((m, "single_spread", b), 0.0) for m in first), 1),
                 "last3": round(sum(buckets.get((m, "single_spread", b), 0.0) for m in last), 1)}
    me = month_end_values(tff)
    return {"first_months": first, "last_months": last,
            "single_spread_dv01_first3_musd": round(sum(flow[m] for m in first), 1),
            "single_spread_dv01_last3_musd": round(sum(flow[m] for m in last), 1),
            "single_spread_share_first3": round(statistics.fmean(share[m] for m in first), 4),
            "single_spread_share_last3": round(statistics.fmean(share[m] for m in last), 4),
            "by_tenor": tb,
            "lf_net_dv01_musd": {m: round(me[m] / 1e6, 1) for m in (first[0], last[-1]) if m in me},
            "monthly_single_spread_dv01_musd": {m: round(flow[m], 1) for m in full},
            "monthly_single_spread_share": {m: round(share[m], 4) for m in full}}


def main():
    rng = random.Random(SEED)
    by, buckets = load_daily()
    manifest = json.loads((ROOT / "metadata" / "s24_manifest.json").read_text())
    tff = ofr("TFF-LF_TREAS_NET_DV01")
    result = {
        "design": "docs/design-study-24-swap-spread-visibility.md",
        "dtcc_days": len(by), "first_day": min(by), "last_day": max(by),
        "dtcc_files_in_manifest": len(manifest["dtcc"]),
        "q1": q1(by, ofr("FPF-ASSETCLASS_IRD_GNE_SUM")),
        "q2": q2(by, rng),
        "q3": q3(by, tff, rng),
        "q4": q4(by, rng),
        "q5": q5(by),
        "describe": describe(by, buckets, tff),
    }
    result["verdict"] = ("public data tracks the trade" if result["q1"]["tracks"] and result["q2"]["sees_unwind"]
                         else "not tracked with this method" if not result["q1"]["tracks"] and not result["q2"]["sees_unwind"]
                         else "mixed")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("q1", "q2", "q5", "verdict")}, indent=1))


if __name__ == "__main__":
    main()
