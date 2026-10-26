"""Study 06: would the repo chain have warned of stress better than the standard signs (H4)?

Design: docs/design-study-06-warning.md (committed before the run).
Inputs: data/raw/chain/ (fetch_chain.py), data/raw/long/ (fetch_long.py).
Writes results/study-06/result.json.
"""
import csv
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
from spillovers import stats  # noqa: E402
import study_02_then_and_now as s2  # noqa: E402
import study_03_chain as s3  # noqa: E402

SEED, DRAWS = 20261030, 2000
HORIZON, MIN_HISTORY = 6, 36
EVENTS_END = "2026-03"
NAMED = {1: ("Flash crash and first euro-area crisis", "2010-05-06"),
         2: ("US downgrade and second euro-area crisis", "2011-08-01"),
         3: ("Taper tantrum", "2013-05-22"), 4: ("Treasury flash rally", "2014-10-15"),
         5: ("China devaluation sell-off", "2015-08-20"), 6: ("Volmageddon", "2018-02-02"),
         7: ("Q4 2018 sell-off", "2018-10-10"), 8: ("Repo spike", "2019-09-16"),
         9: ("COVID, Treasury dash for cash", "2020-02-24"), 10: ("UK gilt (LDI) crisis", "2022-09-23"),
         11: ("Regional banks (SVB)", "2023-03-09"), 12: ("Yen carry unwind", "2024-08-01"),
         13: ("Tariff shock and Treasury sell-off", "2025-04-03")}
OUT = ROOT / "results" / "study-06"


def indicators():
    """name -> (monthly series, warning direction, group)."""
    m = h.complete_months
    phmt = {k: v / 1e3 - f / 1e3 for k, v in m(s3.mspd(), "monthly").items()
            for f in [m(s3.fred("TREAST"), "daily").get(k)] if f is not None}
    hf = {k: v / 1e9 for k, v in m(s3.ofr("OFRHF_FPF-BORROW_REPO_SUM.json"), "quarterly").items()}
    fut = m(s3.cftc_net_short(), "daily")
    tot = m(s3.ofr("OFR_MMF-MMF_RP_TOT-M.json"), "monthly")
    ficc = m(s3.ofr("OFR_MMF-MMF_RP_wFICC-M.json"), "monthly")
    ids = {s for spec in h.INDICATORS.values() for s in (spec.get("num"), spec.get("den"), spec.get("minus")) if s}
    sources = {i: s2.complete_months(s2.read_daily(i), i in h.QUARTERLY) for i in ids}
    std = {n: h.build_indicator(h.INDICATORS[n], sources) for n in ("curve_10y3m_bp", "baa_10y_bp", "nfci_leverage")}
    std["nfci"] = s2.complete_months(s2.read_daily("NFCI"), False)
    return {"chain_hf_repo_pct_phmt": (s3.ratio(hf, phmt), "high", "chain"),
            "chain_levfund_futures_short_pct_phmt": (s3.ratio(fut, phmt), "high", "chain"),
            "chain_ficc_share_mmf_repo": (s3.ratio(ficc, tot), "high", "chain"),
            "std_curve_10y3m": (std["curve_10y3m_bp"], "low", "standard"),
            "std_baa_10y": (std["baa_10y_bp"], "high", "standard"),
            "std_nfci": (std["nfci"], "high", "standard"),
            "std_nfci_leverage": (std["nfci_leverage"], "high", "standard")}


def expanding_score(series, direction):
    """month -> share of the series' months up to and including it that are no more extreme (warning direction)."""
    months = sorted(series)
    out = {}
    for i, mth in enumerate(months):
        if i + 1 < MIN_HISTORY:
            continue
        hist = [series[k] for k in months[: i + 1]]
        v = series[mth]
        out[mth] = sum(x <= v for x in hist) / len(hist) if direction == "high" else \
            sum(x >= v for x in hist) / len(hist)
    return out


def auroc(scores, labels):
    """Mann-Whitney AUROC; ties count half. None without both classes."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def mechanical_onsets():
    """First days the OFR FSI rose >= 1.0 over 20 business days, at least 60 business days apart."""
    with open(ROOT / "data" / "raw" / "long" / "OFR_FSI.csv", newline="") as f:
        fsi = [(r["Date"], float(r["OFR FSI"])) for r in csv.DictReader(f) if r["OFR FSI"]]
    onsets, last = [], -10 ** 9
    for i in range(20, len(fsi)):
        if fsi[i][1] - fsi[i - 20][1] >= 1.0 and i - last >= 60 and fsi[i][0] >= "2010-01-01":
            onsets.append(fsi[i][0])
            last = i
    return onsets


def main():
    s3.check_manifest()
    s2.check_manifest()
    rng = random.Random(SEED)
    ind = indicators()
    scores = {n: expanding_score(s, d) for n, (s, d, _) in ind.items()}
    start = max(min(s) for s in scores.values())
    end = h.month_add(EVENTS_END, -HORIZON)
    months = [mth for mth in sorted(set.intersection(*(set(s) for s in scores.values()))) if start <= mth <= end]

    def labels_for(onset_dates):
        onset_months = [d[:7] for d in onset_dates if d[:7] <= EVENTS_END]
        return {mth: any(mth < o <= h.month_add(mth, HORIZON) for o in onset_months) for mth in months}

    named_labels = labels_for([d for _, d in NAMED.values()])
    mech = mechanical_onsets()
    mech_labels = labels_for(mech)

    def all_aurocs(label_map, month_list):
        return {n: auroc([scores[n][mth] for mth in month_list], [label_map[mth] for mth in month_list]) for n in ind}

    full = all_aurocs(named_labels, months)
    chain = [n for n in ind if ind[n][2] == "chain"]
    standard = [n for n in ind if ind[n][2] == "standard"]
    best_chain = max(chain, key=lambda n: full[n])
    best_std = max(standard, key=lambda n: full[n])

    years = sorted({mth[:4] for mth in months})
    by_year = {y: [mth for mth in months if mth[:4] == y] for y in years}
    diffs = {"named": [], "mechanical": []}
    per_indicator = {n: [] for n in ind}
    for _ in range(DRAWS):
        sample = [mth for y in rng.choices(years, k=len(years)) for mth in by_year[y]]
        for key, lab in (("named", named_labels), ("mechanical", mech_labels)):
            a = auroc([scores[best_chain][mth] for mth in sample], [lab[mth] for mth in sample])
            b = auroc([scores[best_std][mth] for mth in sample], [lab[mth] for mth in sample])
            if a is not None and b is not None:
                diffs[key].append(a - b)
        for n in ind:
            v = auroc([scores[n][mth] for mth in sample], [named_labels[mth] for mth in sample])
            if v is not None:
                per_indicator[n].append(v)

    def summ(point, draws):
        lo, hi = stats.interval(draws)
        return {"estimate": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)], "excludes_zero": bool(lo > 0 or hi < 0)}

    mech_full = all_aurocs(mech_labels, months)
    main_diff = summ(full[best_chain] - full[best_std], diffs["named"])
    mech_diff = summ(mech_full[best_chain] - mech_full[best_std], diffs["mechanical"])
    if main_diff["excludes_zero"] and main_diff["estimate"] > 0 and mech_diff["estimate"] > 0:
        verdict = "supported"
    elif main_diff["excludes_zero"] and main_diff["estimate"] < 0:
        verdict = "not supported"
    else:
        verdict = "cannot tell"

    latest = {n: {"month": max(scores[n]), "score": round(scores[n][max(scores[n])], 3)} for n in ind}
    result = {"design": "docs/design-study-06-warning.md", "seed": SEED, "draws": DRAWS,
              "period": [months[0], months[-1]], "n_months": len(months),
              "n_positive_months_named": sum(named_labels.values()),
              "named_events_in_period": [f"{k}: {v[0]} ({v[1]})" for k, v in NAMED.items()
                                         if months[0] < v[1][:7] <= h.month_add(months[-1], HORIZON)],
              "mechanical_onsets": mech, "n_positive_months_mechanical": sum(mech_labels.values()),
              "auroc_named": {n: {"auroc": round(full[n], 3), **dict(zip(("ci95",), [[round(x, 3) for x in stats.interval(per_indicator[n])]]))}
                              for n in ind},
              "auroc_mechanical": {n: round(v, 3) if v is not None else None for n, v in mech_full.items()},
              "best_chain": best_chain, "best_standard": best_std,
              "main_difference": main_diff, "mechanical_difference": mech_diff, "verdict": verdict,
              "latest_scores": latest}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
