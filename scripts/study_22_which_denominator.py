"""Study 22: what should reserves be measured against?

Design: docs/design-study-22-which-denominator.md (committed before this study's new data was fetched).
Uses study 17's and study 20's data and fetches GFDEBTN, WTREGEN and SOFR volume into data/raw/s22/, with
metadata/s22_manifest.json; writes results/study-22/result.json.
"""
import datetime as dt
import hashlib
import json
import math
import pathlib
import random
import statistics
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import stats  # noqa: E402
import study_17_spikes_and_creep as s17  # noqa: E402
import study_20_allotment_and_threshold as s20  # noqa: E402

RAW = ROOT / "data" / "raw" / "s22"
OUT = ROOT / "results" / "study-22"
SEED, DRAWS = 20261030, 2000
NAMES = ("debt_held_by_public", "total_public_debt", "sofr_volume", "gdp", "bank_assets",
         "reserves_plus_tga_over_debt_held_by_public")


def fetch():
    s20.fetch()  # also refreshes study 17's inputs
    RAW.mkdir(parents=True, exist_ok=True)
    urls = {f"{s}.csv": f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}" for s in ("GFDEBTN", "WTREGEN")}
    urls["sofr.json"] = (f"https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2018-04-02"
                         f"&endDate={dt.date.today().isoformat()}")
    manifest = {}
    for name, url in urls.items():
        with urllib.request.urlopen(url, timeout=180) as response:
            body = response.read()
        (RAW / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s22_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def sofr_volume():
    """date -> SOFR volume, $ billions."""
    out = {}
    for r in json.loads((RAW / "sofr.json").read_text())["refRates"]:
        try:
            out[r["effectiveDate"]] = float(r["volumeInBillions"])
        except (KeyError, TypeError, ValueError):
            continue
    return out


def monthly_ratios(days):
    res = s17.AsOf(s20.read(s17.RAW / "WRESBAL.csv"))  # $ mn
    tga = s17.AsOf(s20.read(RAW / "WTREGEN.csv"))  # $ mn
    assets = s17.AsOf(s20.read(s17.RAW / "TLAACBW027SBOG.csv"))  # $ bn
    held = s20.quarterly_as_of(s20.read(s20.RAW / "FYGFDPUN.csv"))  # $ mn
    total = s20.quarterly_as_of(s20.read(RAW / "GFDEBTN.csv"))  # $ mn
    gdp = s20.quarterly_as_of(s20.read(s20.RAW / "GDP.csv"))  # $ bn
    vol = sofr_volume()  # $ bn
    out = {}
    for m, ds in s17.months_of(days).items():
        rows = []
        for d in ds:
            v = (res(d), tga(d), assets(d), held(d), total(d), gdp(d), vol.get(d))
            if all(x is not None for x in v):
                rows.append(v)
        if not rows:
            continue
        mean = [statistics.fmean(r[i] for r in rows) for i in range(7)]
        r_mn, t_mn, a_bn, h_mn, tot_mn, g_bn, v_bn = mean
        out[m] = {"debt_held_by_public": r_mn / h_mn * 100, "total_public_debt": r_mn / tot_mn * 100,
                  "sofr_volume": r_mn / (v_bn * 1000) * 100, "gdp": r_mn / (g_bn * 1000) * 100,
                  "bank_assets": r_mn / (a_bn * 1000) * 100,
                  "reserves_plus_tga_over_debt_held_by_public": (r_mn + t_mn) / h_mn * 100}
    return out


def corr(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx, syy = sum((x - mx) ** 2 for x in xs), sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else float("nan")


def main():
    if "--no-fetch" not in sys.argv:
        fetch()
    days, s, s_ior, r, q, srf, top = s17.build()
    jumps = s20.all_month_jumps(days, s)
    ratios = monthly_ratios(days)
    monthly_s = {m: statistics.fmean(s[d] for d in ds) for m, ds in s17.months_of(days).items()}
    months = sorted(m for m in ratios if m in monthly_s and not ("2020-03" <= m <= "2020-12"))
    # T1: comparable months, as in study 20
    old = {m: v for m, v in jumps.items() if s17.regime(v["last"]) == "scarce_2018_19" and m in ratios}
    new = {m: v for m, v in jumps.items() if s17.regime(v["last"]) == "scarce_2025_26" and m in ratios}
    lo = max(min(v["B"] for v in old.values()), min(v["B"] for v in new.values()))
    hi = min(max(v["B"] for v in old.values()), max(v["B"] for v in new.values()))
    co = [m for m, v in old.items() if lo <= v["B"] <= hi]
    cn = [m for m, v in new.items() if lo <= v["B"] <= hi]
    rng = random.Random(SEED)
    years = sorted({m[:4] for m in months})
    by_year = {y: [m for m in months if m[:4] == y] for y in years}
    results = {}
    for k in NAMES:
        mo, mn = statistics.median(ratios[m][k] for m in co), statistics.median(ratios[m][k] for m in cn)
        point = corr([ratios[m][k] for m in months], [monthly_s[m] for m in months])
        draws = []
        for _ in range(DRAWS):
            sample = [m for y in rng.choices(years, k=len(years)) for m in by_year[y]]
            c = corr([ratios[m][k] for m in sample], [monthly_s[m] for m in sample])
            if not math.isnan(c):
                draws.append(c)
        clo, chi = stats.interval(draws)
        rel = mn / mo * 100
        results[k] = {"T1_median_2018_19": round(mo, 3), "T1_median_2025_26": round(mn, 3),
                      "T1_2025_26_as_pct_of_2018_19": round(rel, 1), "T1_matches": abs(rel - 100) <= 10,
                      "T2_corr_with_spread": round(point, 3), "T2_ci95": [round(clo, 3), round(chi, 3)]}
    matching = [k for k in NAMES if results[k]["T1_matches"]]
    best = min(matching, key=lambda k: results[k]["T2_corr_with_spread"]) if matching else None
    if best is None:
        verdict = "debt held by the public is not beaten (no ratio matches)"
    elif best == "debt_held_by_public":
        verdict = "debt held by the public is the best denominator"
    else:
        b_hi = results[best]["T2_ci95"][1]
        d_lo = results["debt_held_by_public"]["T2_ci95"][0]
        verdict = (f"{best} is the best denominator" if b_hi < d_lo
                   else f"debt held by the public is not beaten ({best} fits as well within the intervals)")
    result = {"design": "docs/design-study-22-which-denominator.md", "manifest": "metadata/s22_manifest.json",
              "inputs_also": ["metadata/s17_manifest.json", "metadata/s20_manifest.json"], "seed": SEED, "draws": DRAWS,
              "months": [months[0], months[-1]], "n_months": len(months), "comparable_months": {"2018_19": len(co), "2025_26": len(cn)},
              "denominators": results, "matching": matching, "best": best, "verdict": verdict,
              "n_tried": len(NAMES)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
