"""Study 05: does repo stress spread outward beyond calendar days (H3)?

Design: docs/design-study-05-spillback.md (committed before the run).
Part A: non-calendar repo shocks against wider markets. Part B: SOFR swap spreads from DTCC trades, 2024-11 onwards.
Inputs: data/panel.csv, data/fomc_calendar.json, data/raw/*.csv (fetch_fred.py), data/raw/long/OFR_FSI.csv
(fetch_long.py), data/raw/dtcc/sofr_ois_trades.csv (fetch_dtcc.py).
Writes results/study-05/result.json and swap_rates_daily.csv.
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
from spillovers import events as ev  # noqa: E402
from spillovers import outcomes as oc  # noqa: E402
from spillovers import stats  # noqa: E402

SEED, DRAWS, SLOPE_DRAWS = 20261028, 5000, 2000
SHOCK_BP = 5.0
PLACEBO_SHIFT = 10
MIN_TRADES = 5
OUT = ROOT / "results" / "study-05"
SECONDARY = {"DGS10": ("ust10y_bp", "bp"), "DGS2": ("ust2y_bp", "bp"), "VIXCLS": ("vix_pts", "level"),
             "SP500": ("spx_pct", "logpct"), "BAA10Y": ("baa_10y_bp", "bp"), "DTWEXBGS": ("usd_broad_pct", "logpct"),
             "RIFSPPFAAD01NB": ("cp_on_fin_iorb_bp", "bp_iorb"), "DTB4WK": ("bill4w_iorb_bp", "bp_iorb")}


def check_inputs():
    fred = json.loads((ROOT / "metadata" / "fred_manifest.json").read_text())
    for s in SECONDARY:
        if hashlib.sha256((ROOT / "data" / "raw" / f"{s}.csv").read_bytes()).hexdigest() != fred[s]["sha256"]:
            raise ValueError(f"data/raw/{s}.csv differs from metadata/fred_manifest.json")
    long = json.loads((ROOT / "metadata" / "long_manifest.json").read_text())
    if hashlib.sha256((ROOT / "data" / "raw" / "long" / "OFR_FSI.csv").read_bytes()).hexdigest() != \
            long["OFR_FSI.csv"]["sha256"]:
        raise ValueError("data/raw/long/OFR_FSI.csv differs from metadata/long_manifest.json")


def weighted_median(pairs):
    """Median of values weighted by weights: pairs of (value, weight)."""
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            return v
    raise ValueError("no trades")


def swap_rates():
    """date -> {"2y": rate %, "10y": rate %, "n2y": trades, "n10y": trades} from the filtered DTCC trades."""
    by = {}
    with open(ROOT / "data" / "raw" / "dtcc" / "sofr_ois_trades.csv", newline="") as f:
        for r in csv.DictReader(f):
            tenor = "2y" if float(r["tenor_years"]) < 5 else "10y"
            by.setdefault((r["execution"], tenor), []).append((float(r["fixed_rate"]) * 100, float(r["notional"])))
    out = {}
    for (date, tenor), trades in by.items():
        out.setdefault(date, {})[f"n{tenor}"] = len(trades)
        if len(trades) >= MIN_TRADES:
            out[date][tenor] = weighted_median(trades)
    return out


def main():
    check_inputs()
    rng = random.Random(SEED)
    rows = ev.read_panel(ROOT / "data" / "panel.csv")
    labels, excluded = ev.classify(rows, ev.fomc_decision_dates(ROOT / "data" / "fomc_calendar.json"))
    dates = [r["date"] for r in rows]
    iorb = {r["date"]: r["iorb"] for r in rows}
    spread = {r["date"]: (r["sofr"] - r["iorb"]) * 100 for r in rows if r["sofr"] is not None}
    dspread = oc.daily_changes(dates, {d: v / 100 for d, v in spread.items()}, "bp")
    ok = lambda d: not labels[d] and d not in excluded  # noqa: E731

    # two-day change, close of t-1 to close of t+1, for any level series on panel dates
    def two_day(level, kind):
        out = {}
        for i in range(1, len(dates) - 1):
            a, b = level.get(dates[i - 1]), level.get(dates[i + 1])
            if a is None or b is None:
                continue
            if kind == "bp":
                out[dates[i]] = (b - a) * 100
            elif kind == "level":
                out[dates[i]] = b - a
            elif kind == "logpct":
                out[dates[i]] = 100 * math.log(b / a)
            elif kind == "bp_iorb":
                out[dates[i]] = ((b - iorb[dates[i + 1]]) - (a - iorb[dates[i - 1]])) * 100
        return out

    with open(ROOT / "data" / "raw" / "long" / "OFR_FSI.csv", newline="") as f:
        fsi = {r["Date"]: float(r["OFR FSI"]) for r in csv.DictReader(f) if r["OFR FSI"]}
    outcome_series = {"ofr_fsi": two_day(fsi, "level")}
    for series, (name, kind) in SECONDARY.items():
        outcome_series[name] = two_day(oc.read_fred(ROOT / "data" / "raw" / f"{series}.csv"), kind)

    eligible = [i for i in range(1, len(dates) - 1) if ok(dates[i]) and dspread.get(dates[i]) is not None]
    shock = {i for i in eligible if dspread[dates[i]] >= SHOCK_BP}
    shock_days = {regime: sorted(dates[i] for i in shock if ev.regime_of(dates[i]) == regime) for regime in ev.REGIMES}

    def summary(point, draws, **extra):
        lo, hi = stats.interval(draws)
        return {"estimate": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)],
                "excludes_zero": bool(lo > 0 or hi < 0), **extra}

    def effect(regime, shock_set, name, f):
        y = outcome_series[name]
        idx = [i for i in eligible if ev.regime_of(dates[i]) == regime and dates[i] in y]
        hit = [f(y[dates[i]]) for i in idx if i in shock_set]
        rest = [f(y[dates[i]]) for i in idx if i not in shock_set]
        if len(hit) < 3:
            return None
        draws = [a - b for a, b in zip(stats.boot_means(hit, DRAWS, rng), stats.boot_means(rest, DRAWS, rng))]
        return summary(statistics.fmean(hit) - statistics.fmean(rest), draws, n_shock=len(hit), n_other=len(rest))

    part_a = []
    for regime in ev.REGIMES:
        for name in outcome_series:
            for measure, f in (("signed", lambda x: x), ("size", abs)):
                r = effect(regime, shock, name, f)
                if r:
                    part_a.append({"regime": regime, "outcome": name, "measure": measure, **r})
    get = lambda regime, name, measure: next((r for r in part_a if r["regime"] == regime and r["outcome"] == name  # noqa: E731
                                              and r["measure"] == measure), None)
    main_a = get("scarce_2025_26", "ofr_fsi", "signed")
    replication_a = get("scarce_2018_19", "ofr_fsi", "signed")
    moved = {i + PLACEBO_SHIFT for i in shock}
    placebo_a = effect("scarce_2025_26", moved, "ofr_fsi", lambda x: x)
    a_supports = bool(main_a and main_a["excludes_zero"] and main_a["estimate"] > 0
                      and replication_a and replication_a["estimate"] > 0
                      and placebo_a and not placebo_a["excludes_zero"])

    # Part B: swap spreads
    swaps = swap_rates()
    dgs = {t: oc.read_fred(ROOT / "data" / "raw" / f"DGS{t[:-1]}.csv") for t in ("2y", "10y")}
    spreads = {}
    for date, v in sorted(swaps.items()):
        for t in ("2y", "10y"):
            if t in v and date in dgs[t]:
                spreads.setdefault(t, {})[date] = (v[t] - dgs[t][date]) * 100
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "swap_rates_daily.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "sofr_swap_2y_pct", "trades_2y", "sofr_swap_10y_pct", "trades_10y",
                    "swap_spread_2y_bp", "swap_spread_10y_bp"])
        for date in sorted(swaps):
            v = swaps[date]
            w.writerow([date, round(v["2y"], 5) if "2y" in v else "", v.get("n2y", 0),
                        round(v["10y"], 5) if "10y" in v else "", v.get("n10y", 0),
                        round(spreads.get("2y", {}).get(date), 2) if date in spreads.get("2y", {}) else "",
                        round(spreads.get("10y", {}).get(date), 2) if date in spreads.get("10y", {}) else ""])

    part_b = {}
    for t in ("10y", "2y"):
        s = spreads[t]
        dsw = oc.daily_changes(dates, {d: v / 100 for d, v in s.items()}, "bp")
        pairs = [(dspread[d], dsw[d]) for d in dates if d >= "2025-01-01" and ok(d)
                 and dspread.get(d) is not None and dsw.get(d) is not None]
        slope, (lo, hi) = stats.slope_with_interval([p[0] for p in pairs], [p[1] for p in pairs], SLOPE_DRAWS, rng)
        two = two_day({d: v / 100 for d, v in s.items()}, "bp")
        me = [(dspread[dates[i]], two[dates[i]]) for i in range(1, len(dates) - 1)
              if dates[i] >= "2025-01-01" and "month_end" in labels[dates[i]] and dates[i] not in excluded
              and dspread.get(dates[i]) is not None and dates[i] in two]
        rank = lambda xs: [sorted(xs).index(x) for x in xs]  # noqa: E731
        rx, ry = rank([p[0] for p in me]), rank([p[1] for p in me])
        mx, my = statistics.fmean(rx), statistics.fmean(ry)
        rho = (sum((a - mx) * (b - my) for a, b in zip(rx, ry))
               / math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))) if len(me) > 2 else None
        part_b[t] = {"days_with_rate": len(s), "first": min(s), "last": max(s),
                     "level_bp": {"mean": round(statistics.fmean(s.values()), 2), "min": round(min(s.values()), 2),
                                  "max": round(max(s.values()), 2)},
                     "passthrough": {"n_days": len(pairs), "slope_bp_per_bp": round(slope, 4),
                                     "ci95": [round(lo, 4), round(hi, 4)], "excludes_zero": bool(lo > 0 or hi < 0)},
                     "month_end_rank_corr": {"n": len(me), "rho": None if rho is None else round(rho, 3)}}
    b10 = part_b["10y"]
    b_supports = bool(b10["passthrough"]["excludes_zero"] and b10["passthrough"]["slope_bp_per_bp"] < 0
                      and b10["month_end_rank_corr"]["rho"] is not None and b10["month_end_rank_corr"]["rho"] < 0)
    verdict = "supported" if a_supports and b_supports else "partly supported" if a_supports or b_supports \
        else "not supported"

    market = [r for r in part_a if r["regime"] in ev.COMPARED_REGIMES and r["outcome"] != "ofr_fsi"]
    result = {"design": "docs/design-study-05-spillback.md",
              "panel_sha256": hashlib.sha256((ROOT / "data" / "panel.csv").read_bytes()).hexdigest(),
              "dtcc_manifest": "metadata/dtcc_manifest.json", "seed": SEED, "verdict": verdict,
              "part_a": {"supports": a_supports, "shock_days": shock_days, "main": main_a,
                         "replication": replication_a, "placebo_plus10": placebo_a,
                         "multiplicity": {"intervals": len(market),
                                          "excluding_zero": sum(r["excludes_zero"] for r in market),
                                          "expected_by_chance": round(0.05 * len(market), 1)},
                         "effects": part_a},
              "part_b": {"supports": b_supports, **part_b}}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("part_a", "part_b")}, indent=1))
    print(json.dumps({k: result["part_a"][k] for k in ("supports", "shock_days", "main", "replication",
                                                       "placebo_plus10", "multiplicity")}, indent=1))
    print(json.dumps(result["part_b"], indent=1))


if __name__ == "__main__":
    main()
