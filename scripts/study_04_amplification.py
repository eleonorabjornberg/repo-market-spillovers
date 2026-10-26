"""Study 04: do Treasury-market shocks spread into repo the next day (H2)?

Design: docs/design-study-04-amplification.md (committed before the run).
Inputs: data/panel.csv, data/fomc_calendar.json (build_panel.sh); data/raw/DGS10.csv (fetch_fred.py);
data/raw/long/OFR_FSI.csv (fetch_long.py); data/raw/chain/ (fetch_chain.py, for study 03's hedge-fund repo share).
Writes results/study-04/result.json.
"""
import csv
import hashlib
import json
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import events as ev  # noqa: E402
from spillovers import history as h  # noqa: E402
from spillovers import outcomes as oc  # noqa: E402
from spillovers import stats  # noqa: E402
import study_03_chain as s3  # noqa: E402

SEED, DRAWS, DOSE_DRAWS = 20261027, 5000, 2000
MAIN, REPLICATION = ("scarce_2025_26", "floor_2021_23"), ("scarce_2018_19", "floor_2021_23")
PLACEBO_SHIFT = 10
CASES = (("2020-03-12", "2020-03-18"), ("2025-04-03", "2025-04-11"))
OUT = ROOT / "results" / "study-04"


def check_inputs():
    manifest = json.loads((ROOT / "metadata" / "fred_manifest.json").read_text())
    if hashlib.sha256((ROOT / "data" / "raw" / "DGS10.csv").read_bytes()).hexdigest() != manifest["DGS10"]["sha256"]:
        raise ValueError("data/raw/DGS10.csv differs from metadata/fred_manifest.json")
    manifest = json.loads((ROOT / "metadata" / "long_manifest.json").read_text())
    if hashlib.sha256((ROOT / "data" / "raw" / "long" / "OFR_FSI.csv").read_bytes()).hexdigest() != \
            manifest["OFR_FSI.csv"]["sha256"]:
        raise ValueError("data/raw/long/OFR_FSI.csv differs from metadata/long_manifest.json")
    s3.check_manifest()


def solve(a, b):
    """Gaussian elimination for a small dense system a x = b."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        if abs(m[c][c]) < 1e-12:
            raise ValueError("singular design matrix")
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def ols(xs, ys):
    """Coefficients of y on [1, x...]."""
    rows = [[1.0] + list(x) for x in xs]
    k = len(rows[0])
    xtx = [[sum(r[i] * r[j] for r in rows) for j in range(k)] for i in range(k)]
    xty = [sum(r[i] * y for r, y in zip(rows, ys)) for i in range(k)]
    return solve(xtx, xty)


def main():
    check_inputs()
    rng = random.Random(SEED)
    rows = ev.read_panel(ROOT / "data" / "panel.csv")
    labels, excluded = ev.classify(rows, ev.fomc_decision_dates(ROOT / "data" / "fomc_calendar.json"))
    dates = [r["date"] for r in rows]
    with open(ROOT / "data" / "panel.csv", newline="") as f:
        raw = {r["date"]: r for r in csv.DictReader(f)}
    spread = {d: (r["sofr"] - r["iorb"]) * 100 for d, r in zip(dates, rows) if r["sofr"] is not None}
    p75 = {d: (float(raw[d]["sofr_p75"]) - float(raw[d]["iorb"])) * 100 for d in dates if raw[d]["sofr_p75"]}
    d10 = oc.daily_changes(dates, oc.read_fred(ROOT / "data" / "raw" / "DGS10.csv"), "bp")
    with open(ROOT / "data" / "raw" / "long" / "OFR_FSI.csv", newline="") as f:
        vol = {r["Date"]: float(r["Volatility"]) for r in csv.DictReader(f) if r["Volatility"]}
    dvol = oc.daily_changes(dates, vol, "level")

    ok = lambda d: not labels[d] and d not in excluded  # noqa: E731
    eligible = [i for i in range(2, len(dates)) if ok(dates[i])]

    def y1(i):
        a, b = spread.get(dates[i - 1]), spread.get(dates[i])
        return None if a is None or b is None else b - a

    def y2(i):
        if i + 2 >= len(dates) or not (ok(dates[i + 1]) and ok(dates[i + 2])):
            return None
        a, b = spread.get(dates[i - 1]), spread.get(dates[i + 2])
        return None if a is None or b is None else b - a

    def y3(i):
        a, b = p75.get(dates[i - 1]), p75.get(dates[i])
        return None if a is None or b is None else b - a

    outcomes = {"Y1_next_day_bp": y1, "Y2_three_day_bp": y2, "Y3_p75_next_day_bp": y3}
    shock_value = {"S1_abs_d10y": lambda i: None if d10.get(dates[i - 1]) is None else abs(d10[dates[i - 1]]),
                   "S2_ofr_vol_rise": lambda i: dvol.get(dates[i - 1])}

    shocks = {}  # (shock, regime) -> set of t indices
    thresholds = {}
    for sname, fn in shock_value.items():
        for regime in ev.REGIMES:
            idx = [i for i in eligible if ev.regime_of(dates[i]) == regime and fn(i) is not None]
            vals = sorted(fn(i) for i in idx)
            q = vals[int(0.95 * len(vals))]
            thresholds[(sname, regime)] = q
            shocks[(sname, regime)] = {i for i in idx if fn(i) >= q}

    def effect(regime, shock_set, outcome):
        f = outcomes[outcome]
        idx = [i for i in eligible if ev.regime_of(dates[i]) == regime and f(i) is not None]
        hit = [f(i) for i in idx if i in shock_set]
        rest = [f(i) for i in idx if i not in shock_set]
        draws = [a - b for a, b in zip(stats.boot_means(hit, DRAWS, rng), stats.boot_means(rest, DRAWS, rng))]
        return statistics.fmean(hit) - statistics.fmean(rest), draws, len(hit)

    def summary(point, draws, **extra):
        lo, hi = stats.interval(draws)
        return {"estimate": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)],
                "excludes_zero": bool(lo > 0 or hi < 0), **extra}

    effects, table = {}, []
    for sname in shock_value:
        for regime in ev.REGIMES:
            for outcome in outcomes:
                point, draws, n = effect(regime, shocks[(sname, regime)], outcome)
                effects[(sname, regime, outcome)] = (point, draws)
                table.append({"shock": sname, "regime": regime, "outcome": outcome,
                              "threshold": round(thresholds[(sname, regime)], 3), **summary(point, draws, n_shock=n)})

    def did(sname, outcome, a, b, eff=effects):
        pa, da = eff[(sname, a, outcome)]
        pb, db = eff[(sname, b, outcome)]
        return summary(pa - pb, [x - y for x, y in zip(da, db)], contrast=f"{a} - {b}")

    contrasts = [{"shock": s, "outcome": o, **did(s, o, *c)} for s in shock_value for o in outcomes
                 for c in (MAIN, REPLICATION)]
    main_test = did("S1_abs_d10y", "Y1_next_day_bp", *MAIN)
    replication = did("S1_abs_d10y", "Y1_next_day_bp", *REPLICATION)

    placebo = {}
    for shift in (PLACEBO_SHIFT, -PLACEBO_SHIFT):
        eff = {}
        for regime in MAIN:
            moved = {i + shift for i in shocks[("S1_abs_d10y", regime)]}
            point, draws, n = effect(regime, moved, "Y1_next_day_bp")
            eff[("S1_abs_d10y", regime, "Y1_next_day_bp")] = (point, draws)
        placebo[f"shift_{shift:+d}"] = did("S1_abs_d10y", "Y1_next_day_bp", *MAIN, eff=eff)

    # dose-response: Y1 on |d10y(t-1)|, hedge-fund repo share (demeaned), and their product
    hf = s3.ratio({k: v / 1e9 for k, v in h.complete_months(s3.ofr("OFRHF_FPF-BORROW_REPO_SUM.json"),
                                                             "quarterly").items()},
                  {k: v / 1e3 - f / 1e3 for k, v in h.complete_months(s3.mspd(), "monthly").items()
                   for f in [h.complete_months(s3.fred("TREAST"), "daily").get(k)] if f is not None})
    obs = [(abs(d10[dates[i - 1]]), hf[dates[i][:7]], y1(i)) for i in eligible
           if ev.regime_of(dates[i]) != "covid_2020" and d10.get(dates[i - 1]) is not None
           and dates[i][:7] in hf and y1(i) is not None]
    hf_mean = statistics.fmean(o[1] for o in obs)
    design = [(x, z - hf_mean, x * (z - hf_mean)) for x, z, _ in obs]
    ys = [o[2] for o in obs]
    coef = ols(design, ys)
    boot = []
    for _ in range(DOSE_DRAWS):
        sample = [rng.randrange(len(obs)) for _ in obs]
        boot.append(ols([design[j] for j in sample], [ys[j] for j in sample])[3])
    lo, hi = stats.interval(boot)
    dose = {"n_days": len(obs), "hf_repo_pct_mean": round(hf_mean, 3),
            "coef_abs_d10y": round(coef[1], 4), "coef_hf_repo": round(coef[2], 4),
            "coef_product": round(coef[3], 5), "coef_product_ci95": [round(lo, 5), round(hi, 5)],
            "product_excludes_zero": bool(lo > 0 or hi < 0),
            "reading": "bp of next-day repo spread per bp of |d10y| per percentage point of hedge-fund repo share"}

    direction = {}
    regime = "scarce_2025_26"
    for sign, keep in (("selloff_d10y_up", lambda v: v > 0), ("rally_d10y_down", lambda v: v < 0)):
        subset = {i for i in shocks[("S1_abs_d10y", regime)] if keep(d10[dates[i - 1]])}
        point, draws, n = effect(regime, subset, "Y1_next_day_bp")
        direction[sign] = summary(point, draws, n_shock=n)

    cases = []
    for start, end in CASES:
        i0, i1 = dates.index(start), dates.index(end)
        for i in range(i0 - 3, i1 + 4):
            d = dates[i]
            cases.append({"date": d, "d10y_bp": None if d10.get(d) is None else round(d10[d], 1),
                          "ofr_vol_change": None if dvol.get(d) is None else round(dvol[d], 3),
                          "spread_bp": round(spread[d], 1), "d_spread_bp": None if y1(i) is None else round(y1(i), 1),
                          "p75_spread_bp": None if d not in p75 else round(p75[d], 1),
                          "calendar_or_excluded": sorted(labels[d]) + (["excluded"] if d in excluded else [])})

    placebo_ok = all(not p["excludes_zero"] or abs(p["estimate"]) < abs(main_test["estimate"]) / 2
                     for p in placebo.values())
    placebo_clean = all(not p["excludes_zero"] for p in placebo.values())
    main_pos = main_test["excludes_zero"] and main_test["estimate"] > 0
    same_sign = replication["estimate"] * main_test["estimate"] > 0
    dose_pos = dose["product_excludes_zero"] and dose["coef_product"] > 0
    if main_pos and placebo_clean and same_sign and dose_pos:
        verdict = "supported"
    elif main_pos and placebo_clean:
        verdict = "supported for 2025-26 only"
    else:
        verdict = "not supported"

    result = {"design": "docs/design-study-04-amplification.md",
              "panel_sha256": hashlib.sha256((ROOT / "data" / "panel.csv").read_bytes()).hexdigest(),
              "seed": SEED, "draws": DRAWS, "verdict": verdict,
              "verdict_inputs": {"main_positive": main_pos, "placebos_include_zero": placebo_clean,
                                 "placebos_small_relative_to_main": placebo_ok, "replication_same_sign": same_sign,
                                 "dose_product_positive": dose_pos},
              "main_test": main_test, "replication": replication, "placebo": placebo, "dose_response": dose,
              "direction_2025_26": direction, "contrasts": contrasts, "effects": table, "cases": cases}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("verdict", "verdict_inputs", "main_test", "replication", "placebo",
                                             "dose_response", "direction_2025_26")}, indent=1))


if __name__ == "__main__":
    main()
