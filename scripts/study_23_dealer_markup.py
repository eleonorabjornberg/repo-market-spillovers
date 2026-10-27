"""Study 23: the dealer markup as a daily series.

Design: docs/design-study-23-dealer-markup.md (committed before this study's new data was fetched).
Fetches the New York Fed's secured reference rates from April 2018 into data/raw/s23/ (metadata/s23_manifest.json);
uses study 17's FRED and OFR inputs; writes results/study-23/result.json.
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
import study_10_prospective as s10  # noqa: E402
import study_17_spikes_and_creep as s17  # noqa: E402
from study_22_which_denominator import corr  # noqa: E402

RAW = ROOT / "data" / "raw" / "s23"
OUT = ROOT / "results" / "study-23"
SEED, DRAWS = 20261031, 2000
FULL_ALLOTMENT = "2025-12-11"


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    url = (f"https://markets.newyorkfed.org/api/rates/secured/all/search.json?startDate=2018-04-02"
           f"&endDate={dt.date.today().isoformat()}")
    with urllib.request.urlopen(url, timeout=180) as response:
        body = response.read()
    (RAW / "secured.json").write_bytes(body)
    manifest = {"secured.json": {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                                 "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}}
    for f in sorted(s17.RAW.glob("*")):  # study 17's inputs as used here
        manifest[f"s17/{f.name}"] = {"sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    (ROOT / "metadata" / "s23_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def markups():
    """date -> {"p99": SOFR99 - TGCR99, "p75": SOFR75 - TGCR75}, in bp."""
    by = {}
    for r in json.loads((RAW / "secured.json").read_text())["refRates"]:
        if r["type"] not in ("SOFR", "TGCR"):
            continue
        try:
            by.setdefault(r["effectiveDate"], {})[r["type"]] = (float(r["percentPercentile99"]), float(r["percentPercentile75"]))
        except (KeyError, TypeError, ValueError):
            continue
    return {d: {"p99": round((v["SOFR"][0] - v["TGCR"][0]) * 100, 1), "p75": round((v["SOFR"][1] - v["TGCR"][1]) * 100, 1)}
            for d, v in by.items() if len(v) == 2}


def quarter_end_turns(days):
    """The last business day of each quarter-end month and the next business day; and the year-end subset."""
    by = {}
    for d in days:
        by.setdefault(d[:7], []).append(d)
    keys = sorted(by)
    qe, ye = set(), set()
    for i, m in enumerate(keys[:-1]):
        if int(m[5:7]) % 3 == 0:
            pair = {by[m][-1], by[keys[i + 1]][0]}
            qe |= pair
            if m[5:7] == "12":
                ye |= pair
    return qe, ye


def boot_diff(a_days, b_days, values, rng):
    """Mean(values on a_days) - mean(on b_days), resampling days within each year."""
    years = sorted({d[:4] for d in a_days + b_days})
    ay = {y: [d for d in a_days if d[:4] == y] for y in years}
    by_ = {y: [d for d in b_days if d[:4] == y] for y in years}
    draws = []
    for _ in range(DRAWS):
        a = [d for y in years for d in rng.choices(ay[y], k=len(ay[y]))] if a_days else []
        b = [d for y in years for d in rng.choices(by_[y], k=len(by_[y]))] if b_days else []
        if a and b:
            draws.append(statistics.fmean(values[d] for d in a) - statistics.fmean(values[d] for d in b))
    lo, hi = stats.interval(draws)
    return (round(statistics.fmean(values[d] for d in a_days) - statistics.fmean(values[d] for d in b_days), 2),
            [round(lo, 2), round(hi, 2)])


def main():
    if "--no-fetch" not in sys.argv:
        fetch()
    mk = markups()
    days = sorted(mk)
    ior = {**s17.fred("IOER"), **s17.fred("IORB")}
    noncal = s10.non_calendar(days, ior)
    rng = random.Random(SEED)
    p99 = {d: mk[d]["p99"] for d in days}
    p75 = {d: mk[d]["p75"] for d in days}
    qe, ye = quarter_end_turns(days)
    others = [d for d in days if d not in qe]
    q1 = {}
    for label, series in (("p99", p99), ("p75", p75)):
        est, ci = boot_diff(sorted(qe), others, series, rng)
        q1[label] = {"quarter_end_minus_other_bp": est, "ci95": ci, "n_quarter_end_days": len(qe),
                     "mean_quarter_end_bp": round(statistics.fmean(series[d] for d in qe), 2),
                     "mean_other_bp": round(statistics.fmean(series[d] for d in others), 2),
                     "mean_year_end_bp": round(statistics.fmean(series[d] for d in ye), 2)}
    q1["verdict"] = "widens at quarter-ends" if q1["p99"]["ci95"][0] > 0 else "no detectable widening at quarter-ends"
    before = [d for d in days if "2025-01-01" <= d < FULL_ALLOTMENT and d in noncal]
    after = [d for d in days if d >= FULL_ALLOTMENT and d in noncal]
    est, ci = boot_diff(after, before, p99, rng)
    q2 = {"n_before": len(before), "n_after": len(after), "mean_before_bp": round(statistics.fmean(p99[d] for d in before), 2),
          "mean_after_bp": round(statistics.fmean(p99[d] for d in after), 2), "after_minus_before_bp": est, "ci95": ci}
    # Q3: monthly non-calendar markup against the sponsored share of cleared repo
    sr, srr, dvp = (s17.ofr(n) for n in ("FICC-SPONSORED_REPO_VOL", "FICC-SPONSORED_REVREPO_VOL", "REPO-DVP_TV_TOT-P"))
    months = {}
    for d in days:
        if d in noncal:
            months.setdefault(d[:7], {"mk": [], "sh": []})["mk"].append(p99[d])
    for d in dvp:
        if d in sr and d in srr and dvp[d] and d[:7] in months:
            months[d[:7]]["sh"].append((sr[d] + srr[d]) / dvp[d] * 100)
    rows = {m: (statistics.fmean(v["mk"]), statistics.fmean(v["sh"])) for m, v in months.items() if v["mk"] and v["sh"]}
    ms = sorted(rows)
    point = corr([rows[m][1] for m in ms], [rows[m][0] for m in ms])
    years = sorted({m[:4] for m in ms})
    by_year = {y: [m for m in ms if m[:4] == y] for y in years}
    draws = []
    for _ in range(DRAWS):
        sample = [m for y in rng.choices(years, k=len(years)) for m in by_year[y]]
        c = corr([rows[m][1] for m in sample], [rows[m][0] for m in sample])
        if not math.isnan(c):
            draws.append(c)
    lo, hi = stats.interval(draws)
    q3 = {"months": [ms[0], ms[-1]], "n_months": len(ms), "corr_sponsored_share_vs_markup": round(point, 3),
          "ci95": [round(lo, 3), round(hi, 3)],
          "verdict": "narrows as sponsored clearing grows" if hi < 0 else "no detectable narrowing with sponsored clearing"}
    yearly = {y: {"p99_all_days_bp": round(statistics.fmean(p99[d] for d in days if d[:4] == y), 2),
                  "p99_noncal_days_bp": round(statistics.fmean(p99[d] for d in days if d[:4] == y and d in noncal), 2)
                  if any(d[:4] == y and d in noncal for d in days) else None,
                  "sponsored_share_pct": round(statistics.fmean(rows[m][1] for m in ms if m[:4] == y), 1)
                  if any(m[:4] == y for m in ms) else None}
              for y in sorted({d[:4] for d in days})}
    result = {"design": "docs/design-study-23-dealer-markup.md", "manifest": "metadata/s23_manifest.json", "seed": SEED,
              "draws": DRAWS, "days": [days[0], days[-1]], "n_days": len(days), "Q1_quarter_ends": q1,
              "Q2_full_allotment": q2, "Q3_sponsored_clearing": q3, "yearly": yearly,
              "latest": {"date": days[-1], "p99_markup_bp": p99[days[-1]]}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
