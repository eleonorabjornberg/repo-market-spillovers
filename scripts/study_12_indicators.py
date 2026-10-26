"""Study 12: looking for better warning indicators, without fooling ourselves.

Design: docs/design-study-12-indicators.md (committed before any candidate was scored, with its amendment).
Inputs: data/raw/s12/ (fetch_study12.py); optionally data/raw/s12/ebp.csv (the Fed's excess bond premium, supplied by
hand, scored beside the main test). Writes results/study-12/result.json.
"""
import csv
import hashlib
import json
import math
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
from spillovers import stats  # noqa: E402
from study_06_warning import auroc  # noqa: E402

RAW = ROOT / "data" / "raw" / "s12"
OUT = ROOT / "results" / "study-12"
SEED, DRAWS = 20261102, 2000
EVENTS = ["1990-08-02", "1994-02-04", "1997-10-27", "1998-08-17", "2000-04-03", "2001-09-17", "2002-06-25",
          "2007-08-09", "2008-09-15", "2010-05-06", "2011-08-01", "2013-05-22", "2014-10-15", "2015-08-20",
          "2018-02-02", "2018-10-10", "2019-09-16", "2020-02-24", "2022-09-23", "2023-03-09", "2024-08-01",
          "2025-04-03"]
DEV, TEST = ("1991-01", "2012-12"), ("2013-01", "2025-09")
COMPOSITE = ("L1_vix_12m_mean", "L3_credit_gap", "L4_dealer_growth", "L5_stock_bond_corr")


def check_manifest():
    manifest = json.loads((ROOT / "metadata" / "s12_manifest.json").read_text())
    stale = [n for n, m in manifest.items() if hashlib.sha256((RAW / n).read_bytes()).hexdigest() != m["sha256"]]
    if stale:
        raise ValueError(f"data/raw/s12 differs from metadata/s12_manifest.json for {stale}")


def fred(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def ofr(m):
    return {d: float(v) for d, v in json.loads((RAW / f"{m}.json").read_text()) if v is not None}


def lagged(monthly, months):
    """Shift a monthly series later by `months`: the value for month m is what was public then."""
    return {h.month_add(k, months): v for k, v in monthly.items()}


def candidates():
    """name -> (monthly series as public at each month, warning direction, group)."""
    m = h.complete_months
    vix = m(fred("VIXCLS"), "daily")
    keys = sorted(vix)
    l1 = {k: statistics.fmean(vix[x] for x in keys[i - 11:i + 1]) for i, k in enumerate(keys) if i >= 11}
    credit, gdp = m(fred("CRDQUSAPABIS"), "quarterly"), m(fred("GDP"), "quarterly")
    ratio = {k: credit[k] / gdp[k] * 100 for k in credit if k in gdp}
    rk = sorted(ratio)
    l3 = {k: ratio[k] - statistics.fmean(ratio[x] for x in rk[i - 120:i]) for i, k in enumerate(rk) if i >= 120}
    dealer = m(fred("BOGZ1FL664090005Q"), "quarterly")
    l4 = {k: (dealer[k] / dealer[h.month_add(k, -12)] - 1) * 100 for k in dealer if h.month_add(k, -12) in dealer}
    nasdaq, d10 = fred("NASDAQCOM"), fred("DGS10")
    days = sorted(d for d in nasdaq if d in d10)
    rets = [(days[i], math.log(nasdaq[days[i]] / nasdaq[days[i - 1]]), -(d10[days[i]] - d10[days[i - 1]]))
            for i in range(1, len(days))]
    l5 = {}
    for i in range(59, len(rets)):
        window = rets[i - 59:i + 1]
        xs, ys = [w[1] for w in window], [w[2] for w in window]
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        sxx, syy = sum((a - mx) ** 2 for a in xs), sum((b - my) ** 2 for b in ys)
        if sxx and syy:
            l5[rets[i][0][:7]] = sxy / math.sqrt(sxx * syy)  # month-end value: the last day of each month wins
    out = {"L1_vix_12m_mean": (l1, "low", "candidate"), "L3_credit_gap": (lagged(l3, 3), "high", "candidate"),
           "L4_dealer_growth": (lagged(l4, 3), "high", "candidate"), "L5_stock_bond_corr": (l5, "high", "candidate")}
    pf = lambda mn: lagged(m(ofr(mn), "quarterly"), 6)  # noqa: E731
    fin7 = {k: v + pf("FPF-ALLQHF_FINANCINGLIQUIDTYGT1LE7_PERCENT")[k]
            for k, v in pf("FPF-ALLQHF_FINANCINGLIQUIDTYLE1_PERCENT").items()}
    port7 = {k: v + pf("FPF-ALLQHF_PORTFOLIOLIQUIDITYGT1LE7_PERCENT")[k]
             for k, v in pf("FPF-ALLQHF_PORTFOLIOLIQUIDITYLE1_PERCENT").items()}
    out.update({
        "F1_top10_repo_share": (pf("FPF-BORROW_REPO_GAVN10_PERCENT"), "high", "form_pf"),
        "F2_top10_leverage": (pf("FPF-ALLQHF_GAVN10_LEVERAGERATIO_AVERAGE"), "high", "form_pf"),
        "F3_rv_leverage": (pf("FPF-STRATEGY_RV_LEVERAGERATIO_GAVWMEAN"), "high", "form_pf"),
        "F4_liquidity_mismatch": ({k: fin7[k] - port7[k] for k in fin7 if k in port7}, "high", "form_pf"),
        "B_curve_10y3m": (m(fred("T10Y3M"), "daily"), "low", "benchmark"),
        "B_baa_10y": (m(fred("BAA10Y"), "daily"), "high", "benchmark"),
        "B_nfci": (m(fred("NFCI"), "daily"), "high", "benchmark"),
    })
    ebp = RAW / "ebp.csv"
    if ebp.exists():
        with open(ebp, newline="") as f:
            out["L2_excess_bond_premium"] = (lagged({r["date"][:7]: float(r["ebp"]) for r in csv.DictReader(f)}, 1),
                                             "high", "supplied")
    return out


def expanding_score(series, direction, min_history):
    months = sorted(series)
    out = {}
    for i, mth in enumerate(months):
        if i + 1 < min_history:
            continue
        v = series[mth]
        hist = [series[k] for k in months[: i + 1]]
        out[mth] = (sum(x <= v for x in hist) if direction == "high" else sum(x >= v for x in hist)) / len(hist)
    return out


def labels(months, horizon):
    onsets = [e[:7] for e in EVENTS]
    return {mth: any(mth < o <= h.month_add(mth, horizon) for o in onsets) for mth in months}


def main():
    check_manifest()
    rng = random.Random(SEED)
    cands = candidates()
    scores = {}
    for name, (s, d, group) in cands.items():
        # Form PF is quarterly: 12 quarters of history = 36 months, the same rule
        scores[name] = expanding_score(s, d, 36)
    comp_months = set.intersection(*(set(scores[n]) for n in COMPOSITE))
    scores["composite"] = {mth: statistics.fmean(scores[n][mth] for n in COMPOSITE) for mth in comp_months}

    def period_months(period, names):
        return sorted(mth for mth in set.intersection(*(set(scores[n]) for n in names)) if period[0] <= mth <= period[1])

    def evaluate(names, period, horizon):
        months = period_months(period, names)
        lab = labels(months, horizon)
        out = {"months": [months[0], months[-1]] if months else None, "n_months": len(months),
               "n_positive": sum(lab.values())}
        if not months:
            return out
        years = sorted({mth[:4] for mth in months})
        by_year = {y: [mth for mth in months if mth[:4] == y] for y in years}
        boots = {n: [] for n in names}
        for _ in range(DRAWS):
            sample = [mth for y in rng.choices(years, k=len(years)) for mth in by_year[y]]
            for n in names:
                v = auroc([scores[n][mth] for mth in sample], [lab[mth] for mth in sample])
                if v is not None:
                    boots[n].append(v)
        for n in names:
            a = auroc([scores[n][mth] for mth in months], [lab[mth] for mth in months])
            lo, hi = stats.interval(boots[n])
            out[n] = {"auroc": round(a, 3), "ci95": [round(lo, 3), round(hi, 3)], "above_chance": lo > 0.5}
        return out

    long_names = ["composite", *COMPOSITE, "B_curve_10y3m", "B_baa_10y", "B_nfci"]
    if "L2_excess_bond_premium" in scores:
        long_names.append("L2_excess_bond_premium")
    results = {f"{p}_{hz}m": evaluate(long_names, period, hz) for p, period in (("development", DEV), ("test", TEST))
               for hz in (6, 12)}

    # main test: composite minus curve, test period, 6 months, paired block bootstrap
    months = period_months(TEST, ["composite", "B_curve_10y3m"])
    lab = labels(months, 6)
    years = sorted({mth[:4] for mth in months})
    by_year = {y: [mth for mth in months if mth[:4] == y] for y in years}
    diffs = []
    for _ in range(DRAWS):
        sample = [mth for y in rng.choices(years, k=len(years)) for mth in by_year[y]]
        a = auroc([scores["composite"][mth] for mth in sample], [lab[mth] for mth in sample])
        b = auroc([scores["B_curve_10y3m"][mth] for mth in sample], [lab[mth] for mth in sample])
        if a is not None and b is not None:
            diffs.append(a - b)
    point = (auroc([scores["composite"][mth] for mth in months], [lab[mth] for mth in months])
             - auroc([scores["B_curve_10y3m"][mth] for mth in months], [lab[mth] for mth in months]))
    lo, hi = stats.interval(diffs)
    main_test = {"estimate": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)]}

    form_pf = ["F1_top10_repo_share", "F2_top10_leverage", "F3_rv_leverage", "F4_liquidity_mismatch", "B_curve_10y3m"]
    results["form_pf_test_6m"] = evaluate(form_pf, ("2016-01", TEST[1]), 6)

    promising = sorted({n for key in ("test_6m", "test_12m") for n in long_names
                        if results[key].get(n, {}).get("above_chance") and not n.startswith("B_")}
                       | {n for n in form_pf[:-1] if results["form_pf_test_6m"].get(n, {}).get("above_chance")})
    verdict = ("a better indicator found" if lo > 0 else "promising" if promising else "nothing better")
    latest = {n: {"month": max(s), "score": round(s[max(s)], 3)} for n, s in scores.items() if s}
    result = {"design": "docs/design-study-12-indicators.md", "seed": SEED, "draws": DRAWS, "events": EVENTS,
              "verdict": verdict, "main_test_composite_minus_curve_test_6m": main_test, "promising": promising,
              "results": results, "latest_scores": latest}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("verdict", "main_test_composite_minus_curve_test_6m", "promising")},
                     indent=1))
    for key, r in results.items():
        print(f"\n{key}: {r['months']} n={r['n_months']} positive={r['n_positive']}")
        for n, v in r.items():
            if isinstance(v, dict):
                print(f"  {n:26} {v['auroc']:.3f} {v['ci95']} {'*' if v['above_chance'] else ''}")


if __name__ == "__main__":
    main()
