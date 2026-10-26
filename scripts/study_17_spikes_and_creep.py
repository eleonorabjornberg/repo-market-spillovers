"""Study 17: why 2025-26 month-ends are milder than 2018-19's, and what drove the slow creep.

Design: docs/design-study-17-milder-spikes-and-creep.md (committed before any data was fetched).
Fetches into data/raw/s17/ with metadata/s17_manifest.json and writes results/study-17/result.json.
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

RAW = ROOT / "data" / "raw" / "s17"
OUT = ROOT / "results" / "study-17"
FRED = ("SOFR", "DFEDTARU", "IOER", "IORB", "WRESBAL", "TLAACBW027SBOG", "RRPONTSYD", "RPONTSYD", "SOFR99")
OFR = {"FICC-SPONSORED_REPO_VOL": "hf", "FICC-SPONSORED_REVREPO_VOL": "hf", "REPO-DVP_TV_TOT-P": "stfm"}
REGIMES = {"scarce_2018_19": ("2018-04-03", "2019-12-31"), "floor_2021_23": ("2021-01-01", "2023-12-31"),
           "scarce_2025_26": ("2025-01-01", "9999-12-31")}
SEED, DRAWS = 20261028, 2000


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    urls = {f"{s}.csv": f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}" for s in FRED}
    for m, kind in OFR.items():
        base = "https://data.financialresearch.gov/hf/v1" if kind == "hf" else "https://data.financialresearch.gov/v1"
        urls[f"{m}.json"] = f"{base}/series/timeseries?mnemonic={m}"
    manifest = {}
    for name, url in urls.items():
        with urllib.request.urlopen(url, timeout=180) as response:
            body = response.read()
        (RAW / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s17_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def fred(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def ofr(name):
    return {d: float(v) for d, v in json.loads((RAW / f"{name}.json").read_text()) if v is not None}


class AsOf:
    """Fast as-of lookups on a sorted series."""
    def __init__(self, series):
        self.keys = sorted(series)
        self.series = series

    def __call__(self, day):
        i = bisect.bisect_right(self.keys, day)
        return self.series[self.keys[i - 1]] if i else None


def regime(day):
    for name, (a, b) in REGIMES.items():
        if a <= day <= b:
            return name
    return None


def build():
    sofr, top = fred("SOFR"), AsOf(fred("DFEDTARU"))
    ior = AsOf({**fred("IOER"), **fred("IORB")})
    reserves, assets = AsOf(fred("WRESBAL")), AsOf(fred("TLAACBW027SBOG"))
    rrp, srf = fred("RRPONTSYD"), fred("RPONTSYD")
    days = sorted(d for d in sofr if top(d) is not None)
    s = {d: (sofr[d] - top(d)) * 100 for d in days}
    s_ior = {d: (sofr[d] - ior(d)) * 100 for d in days if ior(d) is not None}
    r = {d: reserves(d) / (assets(d) * 1000) * 100 for d in days if reserves(d) and assets(d)}  # WRESBAL $mn, assets $bn
    q = {d: rrp.get(d, 0.0) / assets(d) * 100 for d in days if assets(d)}  # RRPONTSYD $bn
    return days, s, s_ior, r, q, srf, top


def months_of(days):
    by = {}
    for d in days:
        by.setdefault(d[:7], []).append(d)
    return by


def month_jumps(days, s, top):
    """Month -> (J, B, quarter_end, last day, first day of next month), per the design."""
    by = months_of(days)
    keys = sorted(by)
    out = {}
    for i, m in enumerate(keys[:-1]):
        ds, nxt = by[m], by[keys[i + 1]]
        if len(ds) < 15:
            continue
        last, first = ds[-1], nxt[0]
        if top(ds[5]) != top(first):
            continue  # the target range changed inside the window
        base = statistics.median(s[d] for d in ds[5:15])
        out[m] = {"J": (s[last] + s[first]) / 2 - base, "B": base, "qe": int(m[5:7]) % 3 == 0,
                  "last": last, "first": first}
    return out


def boot_interval(values):
    lo, hi = stats.interval(values)
    return [round(lo, 2), round(hi, 2)]


def part_a(jumps, r, srf, days, s):
    rng = random.Random(SEED)
    sc = {k: {m: v for m, v in jumps.items() if regime(v["last"]) == k} for k in REGIMES}
    a1 = {k: {"n": len(v), "mean_J_bp": round(statistics.fmean(x["J"] for x in v.values()), 2)} for k, v in sc.items() if v}
    old, new = list(sc["scarce_2018_19"].values()), list(sc["scarce_2025_26"].values())
    diffs = []
    for _ in range(DRAWS):
        a, b = rng.choices(old, k=len(old)), rng.choices(new, k=len(new))
        diffs.append(statistics.fmean(x["J"] for x in b) - statistics.fmean(x["J"] for x in a))
    a1["difference_2025_26_minus_2018_19_bp"] = {
        "estimate": round(a1["scarce_2025_26"]["mean_J_bp"] - a1["scarce_2018_19"]["mean_J_bp"], 2),
        "ci95": boot_interval(diffs)}

    def fit(rows, xkey):
        return ols([(x["J"], [1.0, x[xkey], 1.0 if x["qe"] else 0.0, 1.0 if x["new"] else 0.0]) for x in rows], 4)

    for x in old:
        x["new"] = False
        x["R"] = r.get(x["last"])
    for x in new:
        x["new"] = True
        x["R"] = r.get(x["last"])

    def model(xkey):
        lo_o, hi_o = min(x[xkey] for x in old), max(x[xkey] for x in old)
        lo_n, hi_n = min(x[xkey] for x in new), max(x[xkey] for x in new)
        lo, hi = max(lo_o, lo_n), min(hi_o, hi_n)
        overlap = {"2018_19": sum(lo <= x[xkey] <= hi for x in old), "2025_26": sum(lo <= x[xkey] <= hi for x in new)}
        out = {"range_2018_19": [round(lo_o, 2), round(hi_o, 2)], "range_2025_26": [round(lo_n, 2), round(hi_n, 2)],
               "months_in_common_range": overlap}
        if min(overlap.values()) < 5:
            out["verdict"] = "cannot separate" if xkey == "B" else "no overlap"
            return out
        beta = fit(old + new, xkey)
        draws = []
        for _ in range(DRAWS):
            b = fit(rng.choices(old, k=len(old)) + rng.choices(new, k=len(new)), xkey)
            if b:
                draws.append(b)
        lo_d, hi_d = stats.interval([b[3] for b in draws])
        out.update({"coef_tightness_or_reserves": round(beta[1], 3),
                    "coef_tightness_or_reserves_ci95": boot_interval([b[1] for b in draws]),
                    "coef_quarter_end_bp": round(beta[2], 2), "d_2025_26_bp": round(beta[3], 2),
                    "d_ci95": [round(lo_d, 2), round(hi_d, 2)]})
        if xkey == "B":
            out["verdict"] = ("scarcity accounts for it" if lo_d <= 0 <= hi_d else
                              "something beyond scarcity damps the spikes" if hi_d < 0 else
                              "2025-26 spikes are larger at equal tightness")
        return out

    a2 = {"by_tightness_B": model("B"), "by_reserves_R": model("R")}
    # A3: the ceiling
    no_d = ols([(x["J"], [1.0, x["B"], 1.0 if x["qe"] else 0.0]) for x in old + new], 3)
    resid = {k: sorted(x["J"] - (no_d[0] + no_d[1] * x["B"] + no_d[2] * (1.0 if x["qe"] else 0.0)) for x in rows)
             for k, rows in (("2018_19", old), ("2025_26", new))}

    def pct(v, p):
        return round(v[min(len(v) - 1, int(p * len(v)))], 2)

    turn = {k: [d for x in rows for d in (x["last"], x["first"])] for k, rows in (("2018_19", old), ("2025_26", new))}
    a3 = {k: {"share_turn_days_above_top_pct": round(sum(s[d] > 0 for d in turn[k]) / len(turn[k]) * 100, 1),
              "max_turn_spread_bp": round(max(s[d] for d in turn[k]), 1),
              "residual_p50_bp": pct(resid[k], 0.5), "residual_p90_bp": pct(resid[k], 0.9)} for k in turn}
    with_srf = [x["J"] for x in new if max(srf.get(x["last"], 0.0), srf.get(x["first"], 0.0)) >= 1.0]
    without = [x["J"] for x in new if max(srf.get(x["last"], 0.0), srf.get(x["first"], 0.0)) < 1.0]
    a3["2025_26_srf"] = {"n_with_takeup": len(with_srf), "mean_J_with_bp": round(statistics.fmean(with_srf), 2) if with_srf else None,
                         "n_without": len(without), "mean_J_without_bp": round(statistics.fmean(without), 2) if without else None}
    return a1, a2, a3, new


def part_a4(new):
    spons_r, spons_rr, dvp = ofr("FICC-SPONSORED_REPO_VOL"), ofr("FICC-SPONSORED_REVREPO_VOL"), ofr("REPO-DVP_TV_TOT-P")
    rows = []
    for x in new:
        m = x["last"][:7]
        ds = [d for d in dvp if d[:7] == m and d in spons_r and d in spons_rr and dvp[d]]
        if ds:
            share = statistics.fmean((spons_r[d] + spons_rr[d]) / dvp[d] * 100 for d in ds)
            rows.append((x["J"], [1.0, x["B"], share]))
    if len(rows) < 8:
        return {"n_months": len(rows), "note": "too few months with clearing data"}
    beta = ols(rows, 3)
    rng = random.Random(SEED + 1)
    draws = [b[2] for b in (ols(rng.choices(rows, k=len(rows)), 3) for _ in range(DRAWS)) if b]
    return {"n_months": len(rows), "coef_sponsored_share_bp_per_pp": round(beta[2], 3), "ci95": boot_interval(draws)}


def part_b(days, s, s_ior, r, q):
    by = months_of(days)
    monthly = {}
    for m, ds in by.items():
        rr = [r[d] for d in ds if d in r]
        qq = [q[d] for d in ds if d in q]
        if rr and qq:
            monthly[m] = {"S": statistics.fmean(s[d] for d in ds), "R": statistics.fmean(rr), "Q": statistics.fmean(qq),
                          "S_ior": statistics.fmean(s_ior[d] for d in ds if d in s_ior) if any(d in s_ior for d in ds) else None}
    yearly = {y: {k: round(statistics.fmean(v[k] for m, v in monthly.items() if m[:4] == y and v[k] is not None), 2)
                  for k in ("S", "S_ior", "R", "Q")} for y in sorted({m[:4] for m in monthly})}
    # B1
    rows = [(v["S"], [1.0, v["R"], v["Q"]]) for m, v in monthly.items() if m >= "2021-01"]
    beta = ols(rows, 3)
    d = {k: yearly["2025"][k] - yearly["2022"][k] for k in ("S", "R", "Q")}
    fitted = beta[1] * d["R"] + beta[2] * d["Q"]
    b1 = {"coef_R": round(beta[1], 3), "coef_Q": round(beta[2], 3), "actual_change_2022_2025_bp": round(d["S"], 2),
          "from_reserves_bp": round(beta[1] * d["R"], 2), "from_on_rrp_bp": round(beta[2] * d["Q"], 2),
          "fitted_change_bp": round(fitted, 2), "fitted_share_pct": round(fitted / d["S"] * 100, 1),
          "verdict": "the two drains account for the creep" if fitted >= 0.75 * d["S"] else "something else contributed"}
    # B2
    old = [v for m, v in monthly.items() if "2018-04" <= m <= "2019-12"]
    new = [v for m, v in monthly.items() if m >= "2025-01"]
    fit = ols([(v["S"], [1.0, v["R"]]) for v in old], 2)
    lo, hi = min(v["R"] for v in old), max(v["R"] for v in old)
    inside = [v for v in new if lo <= v["R"] <= hi]
    b2 = {"fit_2018_19": {"a": round(fit[0], 2), "b_per_pp_R": round(fit[1], 2)},
          "R_range_2018_19": [round(lo, 2), round(hi, 2)],
          "R_range_2025_26": [round(min(v["R"] for v in new), 2), round(max(v["R"] for v in new), 2)],
          "n_2025_26_months_in_range": len(inside),
          "mean_actual_2025_26_bp": round(statistics.fmean(v["S"] for v in new), 2),
          "mean_predicted_by_2018_19_fit_bp": round(statistics.fmean(fit[0] + fit[1] * v["R"] for v in new), 2),
          "R_at_which_2018_19_fit_gives_2025_26_mean_spread": round(
              (statistics.fmean(v["S"] for v in new) - fit[0]) / fit[1], 2) if fit[1] else None}
    if len(inside) < 5:
        b2["verdict"] = "cannot tell"
    else:
        rng = random.Random(SEED + 2)
        draws = []
        for _ in range(DRAWS):
            f = ols([(v["S"], [1.0, v["R"]]) for v in rng.choices(old, k=len(old))], 2)
            if f:
                pick = rng.choices(inside, k=len(inside))
                draws.append(statistics.fmean(v["S"] - (f[0] + f[1] * v["R"]) for v in pick))
        mean_res = statistics.fmean(v["S"] - (fit[0] + fit[1] * v["R"]) for v in inside)
        lo_r, hi_r = stats.interval(draws)
        b2.update({"mean_residual_bp": round(mean_res, 2), "ci95": [round(lo_r, 2), round(hi_r, 2)],
                   "verdict": ("repo was tighter than reserves predict" if lo_r > 0 else
                               "repo was looser than reserves predict" if hi_r < 0 else "as predicted")})
    return yearly, b1, b2


def post_hoc(days, s, srf, top):
    """Checks added after the first results (labelled post hoc in the result): all months kept, including those with a
    rate change, split into quarter-ends and other month-ends; and the largest turn-day spread above the top of the
    range in each scarce regime."""
    by = months_of(days)
    keys = sorted(by)
    rows = []
    for i, m in enumerate(keys[:-1]):
        ds, nxt = by[m], by[keys[i + 1]]
        reg = regime(ds[-1])
        if len(ds) < 15 or reg not in ("scarce_2018_19", "scarce_2025_26"):
            continue
        base = statistics.median(s[d] for d in ds[5:15])
        rows.append({"month": m, "regime": reg, "qe": int(m[5:7]) % 3 == 0, "last": ds[-1], "first": nxt[0],
                     "J": (s[ds[-1]] + s[nxt[0]]) / 2 - base,
                     "fed_repo_bn": max(srf.get(ds[-1], 0.0), srf.get(nxt[0], 0.0))})
    rng = random.Random(SEED + 3)
    out = {}
    for label, keep in (("all_month_ends", lambda r: True), ("quarter_ends", lambda r: r["qe"]),
                        ("other_month_ends", lambda r: not r["qe"])):
        old = [r["J"] for r in rows if r["regime"] == "scarce_2018_19" and keep(r)]
        new = [r["J"] for r in rows if r["regime"] == "scarce_2025_26" and keep(r)]
        diffs = [statistics.fmean(rng.choices(new, k=len(new))) - statistics.fmean(rng.choices(old, k=len(old)))
                 for _ in range(DRAWS)]
        out[label] = {"n_2018_19": len(old), "n_2025_26": len(new),
                      "mean_2018_19_bp": round(statistics.fmean(old), 2), "mean_2025_26_bp": round(statistics.fmean(new), 2),
                      "median_2018_19_bp": round(statistics.median(old), 2),
                      "median_2025_26_bp": round(statistics.median(new), 2),
                      "difference_bp": round(statistics.fmean(new) - statistics.fmean(old), 2), "ci95": boot_interval(diffs)}
    out["quarter_end_months"] = [{"month": r["month"], "regime": r["regime"], "J_bp": round(r["J"], 1),
                                  "fed_repo_bn": round(r["fed_repo_bn"], 1)} for r in rows if r["qe"]]
    for reg in ("scarce_2018_19", "scarce_2025_26"):
        turns = [(s[d], d) for r in rows if r["regime"] == reg for d in (r["last"], r["first"])]
        out[f"max_turn_spread_above_top_{reg}"] = {"bp": round(max(turns)[0], 1), "date": max(turns)[1]}
    return out


LINE_PERIODS = (("before full allotment", "2021-07-29", "2025-12-10"),
                ("year-end 2025, just after full allotment", "2025-12-11", "2025-12-31"),
                ("2026 to 3 September", "2026-01-02", "2026-09-03"),
                ("2026 to the latest data", "2026-01-02", "9999-12-31"))


def facility_line():
    """Addendum (post hoc, 26 October 2026): Eleonora brought counts from another analysis of the standing repo
    facility's line, IORB + 10 bp, around the move to full allotment on 11 December 2025. This reproduces them from
    FRED: days on which SOFR, and SOFR's 99th percentile, closed above the line."""
    sofr, s99, iorb = fred("SOFR"), fred("SOFR99"), fred("IORB")
    out = {}
    for label, a, b in LINE_PERIODS:
        rows = {}
        for name, series in (("SOFR", sofr), ("SOFR99", s99)):
            days = [d for d in series if a <= d <= b and d in iorb]
            above = [round((series[d] - iorb[d]) * 100 - 10, 1) for d in days if series[d] - iorb[d] > 0.10 + 1e-9]
            at = sum(abs((series[d] - iorb[d]) * 100 - 10) < 0.5 for d in days)
            rows[name] = {"days": len(days), "above_line": len(above),
                          "share_pct": round(len(above) / len(days) * 100, 1) if days else None,
                          "max_bp_above": max(above) if above else None, "days_at_line": at}
        out[label] = {"from": a, "to": b, **rows}
    return out


def main():
    if "--no-fetch" not in sys.argv:
        fetch()
    days, s, s_ior, r, q, srf, top = build()
    jumps = month_jumps(days, s, top)
    a1, a2, a3, new = part_a(jumps, r, srf, days, s)
    a4 = part_a4(new)
    yearly, b1, b2 = part_b(days, s, s_ior, r, q)
    extra = post_hoc(days, s, srf, top)
    line = facility_line()
    result = {"design": "docs/design-study-17-milder-spikes-and-creep.md", "manifest": "metadata/s17_manifest.json",
              "seed": SEED, "draws": DRAWS, "data_to": days[-1],
              "A1_gap": a1, "A2_equal_tightness": a2, "A3_ceiling": a3, "A4_clearing": a4,
              "B_yearly": yearly, "B1_drains": b1, "B2_2018_19_relationship": b2, "post_hoc": extra, "addendum_facility_line": line,
              "month_jumps": {m: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in x.items()}
                              for m, x in sorted(jumps.items())}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "month_jumps"}, indent=1))


if __name__ == "__main__":
    main()
