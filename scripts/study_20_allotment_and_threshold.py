"""Study 20: full allotment or bill purchases? And why repo now gets tight with more reserves.

Design: docs/design-study-20-allotment-and-threshold.md (committed before its new data was fetched).
Reuses study 17's data and month-end measures (scripts/study_17_spikes_and_creep.py); fetches GDP and federal debt
held by the public into data/raw/s20/ with metadata/s20_manifest.json, and writes results/study-20/result.json.
"""
import bisect
import csv
import datetime as dt
import hashlib
import json
import pathlib
import random
import statistics
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import stats  # noqa: E402
from study_16_data_centre_debt import ols  # noqa: E402
import study_17_spikes_and_creep as s17  # noqa: E402

RAW = ROOT / "data" / "raw" / "s20"
OUT = ROOT / "results" / "study-20"
FRED = ("GDP", "FYGFDPUN")
SEED, DRAWS = 20261029, 2000
AFTER_FROM = "2025-12"  # the first month whose turn falls after full allotment (11 December 2025)


def fetch():
    s17.fetch()
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for s in FRED:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
        with urllib.request.urlopen(url, timeout=180) as response:
            body = response.read()
        (RAW / f"{s}.csv").write_bytes(body)
        manifest[f"{s}.csv"] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                                "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s20_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def read(path):
    out = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def all_month_jumps(days, s):
    """Month -> {J, B, qe, last}: study 17's measures, every month kept (as its post hoc check found safe)."""
    by = s17.months_of(days)
    keys = sorted(by)
    out = {}
    for i, m in enumerate(keys[:-1]):
        ds, nxt = by[m], by[keys[i + 1]]
        if len(ds) < 15:
            continue
        base = statistics.median(s[d] for d in ds[5:15])
        out[m] = {"J": (s[ds[-1]] + s[nxt[0]]) / 2 - base, "B": base, "qe": int(m[5:7]) % 3 == 0,
                  "last": ds[-1], "first": nxt[0]}
    return out


def interval(values):
    lo, hi = stats.interval(values)
    return [round(lo, 2), round(hi, 2)]


def part_a(jumps, s):
    reg = {m: v for m, v in jumps.items() if s17.regime(v["last"]) == "scarce_2025_26"}
    before = [v for m, v in reg.items() if m < AFTER_FROM]
    after = [v for m, v in reg.items() if m >= AFTER_FROM]
    rng = random.Random(SEED)
    a1_draws = [statistics.fmean(x["B"] for x in rng.choices(after, k=len(after)))
                - statistics.fmean(x["B"] for x in rng.choices(before, k=len(before))) for _ in range(DRAWS)]
    a1 = {"n_before": len(before), "n_after": len(after),
          "mean_B_before_bp": round(statistics.fmean(x["B"] for x in before), 2),
          "mean_B_after_bp": round(statistics.fmean(x["B"] for x in after), 2),
          "difference_bp": round(statistics.fmean(x["B"] for x in after) - statistics.fmean(x["B"] for x in before), 2),
          "ci95": interval(a1_draws),
          "mean_J_before_bp": round(statistics.fmean(x["J"] for x in before), 2),
          "mean_J_after_bp": round(statistics.fmean(x["J"] for x in after), 2)}

    def fit(b, a):
        rows = [(x["J"], [1.0, x["B"], 1.0 if x["qe"] else 0.0, 0.0]) for x in b] + \
               [(x["J"], [1.0, x["B"], 1.0 if x["qe"] else 0.0, 1.0]) for x in a]
        return ols(rows, 4)

    beta = fit(before, after)
    draws = [b[3] for b in (fit(rng.choices(before, k=len(before)), rng.choices(after, k=len(after)))
                            for _ in range(DRAWS)) if b]
    lo, hi = stats.interval(draws)
    a2 = {"d_after_bp": round(beta[3], 2), "ci95": [round(lo, 2), round(hi, 2)], "coef_B": round(beta[1], 3),
          "coef_quarter_end_bp": round(beta[2], 2),
          "verdict": ("smaller after full allotment" if hi < 0 else "larger" if lo > 0 else "no detectable difference")}
    turns = {lab: max((s[d], d) for x in grp for d in (x["last"], x["first"])) for lab, grp in (("before", before),
                                                                                               ("after", after))}
    a3 = {lab: {"max_turn_S_bp": round(v[0], 1), "date": v[1]} for lab, v in turns.items()}
    months = {"before": sorted(m for m in reg if m < AFTER_FROM), "after": sorted(m for m in reg if m >= AFTER_FROM)}
    return a1, a2, a3, months


def quarterly_as_of(series):
    """A lookup giving the latest quarterly value whose quarter starts on or before the day."""
    keys = sorted(series)
    return lambda d: series[keys[bisect.bisect_right(keys, d) - 1]] if bisect.bisect_right(keys, d) else None


def part_b(jumps, days):
    reserves = read(s17.RAW / "WRESBAL.csv")  # $ millions
    assets = s17.AsOf(read(s17.RAW / "TLAACBW027SBOG.csv"))  # $ billions
    gdp = quarterly_as_of(read(RAW / "GDP.csv"))  # $ billions, annual rate
    debt = quarterly_as_of(read(RAW / "FYGFDPUN.csv"))  # $ millions
    res = s17.AsOf(reserves)
    by = s17.months_of(days)
    ratios = {}
    for m, ds in by.items():
        vals = [(res(d), assets(d), gdp(d), debt(d)) for d in ds]
        vals = [v for v in vals if all(x is not None for x in v)]
        if not vals:
            continue
        r = statistics.fmean(v[0] for v in vals)
        ratios[m] = {"reserves_tn": r / 1e6, "debt_tn": statistics.fmean(v[3] for v in vals) / 1e6,
                     "bank_assets_pct": r / (statistics.fmean(v[1] for v in vals) * 1000) * 100,
                     "gdp_pct": r / (statistics.fmean(v[2] for v in vals) * 1000) * 100,
                     "debt_held_by_public_pct": r / statistics.fmean(v[3] for v in vals) * 100}
    old = {m: v for m, v in jumps.items() if s17.regime(v["last"]) == "scarce_2018_19" and m in ratios}
    new = {m: v for m, v in jumps.items() if s17.regime(v["last"]) == "scarce_2025_26" and m in ratios}
    lo = max(min(v["B"] for v in old.values()), min(v["B"] for v in new.values()))
    hi = min(max(v["B"] for v in old.values()), max(v["B"] for v in new.values()))
    co = [m for m, v in old.items() if lo <= v["B"] <= hi]
    cn = [m for m, v in new.items() if lo <= v["B"] <= hi]
    out = {"common_B_range_bp": [round(lo, 2), round(hi, 2)], "comparable_months": {"2018_19": len(co), "2025_26": len(cn)}}
    if min(len(co), len(cn)) < 5:
        out["verdict"] = "comparison not possible"
        return out
    out["levels_tn"] = {k: {"median_2018_19": round(statistics.median(ratios[m][k] for m in co), 2),
                            "median_2025_26": round(statistics.median(ratios[m][k] for m in cn), 2)}
                        for k in ("reserves_tn", "debt_tn")}
    qualifying = {}
    for k in ("bank_assets_pct", "gdp_pct", "debt_held_by_public_pct"):
        mo, mn = statistics.median(ratios[m][k] for m in co), statistics.median(ratios[m][k] for m in cn)
        rel = mn / mo * 100
        out[k] = {"median_2018_19": round(mo, 2), "median_2025_26": round(mn, 2), "2025_26_as_pct_of_2018_19": round(rel, 1),
                  "within_10pct": abs(rel - 100) <= 10}
        if abs(rel - 100) <= 10:
            qualifying[k] = abs(rel - 100)
    out["verdict"] = (f"the shift disappears under: {', '.join(sorted(qualifying, key=qualifying.get))}"
                      if qualifying else "the threshold has risen under every measure")
    out["closest"] = min(("bank_assets_pct", "gdp_pct", "debt_held_by_public_pct"),
                         key=lambda k: abs(out[k]["2025_26_as_pct_of_2018_19"] - 100))
    return out


def main():
    if "--no-fetch" not in sys.argv:
        fetch()
    days, s, s_ior, r, q, srf, top = s17.build()
    jumps = all_month_jumps(days, s)
    a1, a2, a3, months = part_a(jumps, s)
    result = {"design": "docs/design-study-20-allotment-and-threshold.md", "manifest": "metadata/s20_manifest.json",
              "inputs_also": "metadata/s17_manifest.json", "seed": SEED, "draws": DRAWS, "data_to": days[-1],
              "months": months, "A1_ordinary_days": a1, "A2_jumps_at_equal_tightness": a2, "A3_turn_days": a3,
              "B1_threshold": part_b(jumps, days)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
