"""Study 15: corporate bonds in repo, and in a stock-market panic.

Design: docs/design-study-15-corporate-bonds.md (committed before the data was fetched).
Fetches into data/raw/s15/ with metadata/s15_manifest.json and writes results/study-15/result.json.
"""
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
from spillovers import stats  # noqa: E402

RAW = ROOT / "data" / "raw" / "s15"
OUT = ROOT / "results" / "study-15"
OFR = {f"{leg}_{coll}": f"NYPD-PD_{leg.upper()}_{code}TOT-A" for leg in ("rp", "rrp")
       for coll, code in (("corporate", "CORD_"), ("treasury", "T_"))}  # 2015-2021 segment (design amendment)
NYFED = {"rp_corporate": ("PDSORA-CDTOT",), "rp_treasury": ("PDSORA-UTSETTOT", "PDSORA-UTSTTOT"),
         "rrp_corporate": ("PDSIRRA-CDTOT",), "rrp_treasury": ("PDSIRRA-UTSETTOT", "PDSIRRA-UTSTTOT")}  # 2nd amendment
FRED = ("DBAA", "DGS10", "VIXCLS")
PANIC_RISE = 0.15  # study 09's rule
ERAS = (("1990-01-01", "1999-12-31"), ("2000-01-01", "2007-12-31"), ("2008-01-01", "2019-12-31"),
        ("2020-01-01", "2026-12-31"))
SEED, DRAWS = 20261026, 2000
OLD_COLL = {"corporate": "C", "mortgage": "MB", "agency": "FA", "treasury": "UST"}  # 2008 extension, SBP2013 format
OLD_SIDES = {"out": "PDFSO", "in": "PDFSI"}
OLD_WINDOWS = {"baseline_end": "2007-08-01", "W1_bear_start": "2008-03-17", "W2_lehman_start": "2008-09-15"}
WINDOWS = {"march_2020": ("2020-02-26", "2020-03-18"), "april_2025": ("2025-04-02", "2025-04-09")}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {}
    urls = {f"{k}.json": f"https://data.financialresearch.gov/v1/series/timeseries?mnemonic={m}" for k, m in OFR.items()}
    urls.update({f"{s}.csv": f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}" for s in FRED})
    urls.update({f"nyfed/{k}.json": f"https://markets.newyorkfed.org/api/pd/get/{k}.json" for k in nyfed_keys()})
    urls.update({f"sbp2013/{k}.json": f"https://markets.newyorkfed.org/api/pd/get/SBP2013/timeseries/{k}.json"
                 for k in old_keys()})
    (RAW / "sbp2013").mkdir(exist_ok=True)
    (RAW / "nyfed").mkdir(exist_ok=True)
    for name, url in urls.items():
        with urllib.request.urlopen(url, timeout=180) as response:
            body = response.read()
        (RAW / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s15_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def old_keys():
    return [f"{side}{c}{t}" for side in OLD_SIDES.values() for c in OLD_COLL.values() for t in ("T", "OC", "TA")]


def old(key):
    rows = json.loads((RAW / "sbp2013" / f"{key}.json").read_text())["pd"]["timeseries"]
    return {r["asofdate"]: float(r["value"]) for r in rows if r["value"] not in ("*", "")}


def total_check(t, oc, ta):
    """Share of weeks in which T is within 1% of OC + TA (the extension's check on reading the names)."""
    common = [w for w in t if w in oc and w in ta and t[w]]
    ok = sum(abs((oc[w] + ta[w]) / t[w] - 1) <= 0.01 for w in common)
    return round(ok / len(common) * 100, 1) if common else None


def window_mean(series, start=None, end=None):
    """Mean of the 13 weeks from start, or of the 13 weeks up to and including end."""
    keys = sorted(series)
    ws = [k for k in keys if k >= start][:13] if start else [k for k in keys if k <= end][-13:]
    return (statistics.fmean(series[k] for k in ws), [ws[0], ws[-1]]) if len(ws) == 13 else (None, None)


def q4_2008():
    out = {"checks_T_equals_OC_plus_TA_pct": {}}
    series = {}
    for side, sp in OLD_SIDES.items():
        for coll, c in OLD_COLL.items():
            t, oc, ta = (old(f"{sp}{c}{x}") for x in ("T", "OC", "TA"))
            share = total_check(t, oc, ta)
            out["checks_T_equals_OC_plus_TA_pct"][f"{sp}{c}"] = share
            if share is None or share < 95:
                raise ValueError(f"{sp}{c}: T does not equal OC + TA ({share}%); the design says stop")
            series[(side, coll)] = t
    for side in OLD_SIDES:
        rows = {}
        for coll in OLD_COLL:
            s = series[(side, coll)]
            base, bw = window_mean(s, end=OLD_WINDOWS["baseline_end"])
            w1, w1w = window_mean(s, start=OLD_WINDOWS["W1_bear_start"])
            w2, w2w = window_mean(s, start=OLD_WINDOWS["W2_lehman_start"])
            rows[coll] = {"baseline_bn": round(base / 1000, 1), "W1_bn": round(w1 / 1000, 1), "W2_bn": round(w2 / 1000, 1),
                          "W1_change_pct": pct(base, w1), "W2_change_pct": pct(base, w2)}
            out["windows"] = {"baseline": bw, "W1": w1w, "W2": w2w}
        out[f"securities_{side}"] = rows
    so = out["securities_out"]
    out["run_on_private_collateral_visible"] = (so["corporate"]["W2_change_pct"] <= -20 and
                                                so["corporate"]["W2_change_pct"] <= so["treasury"]["W2_change_pct"] - 20)
    return out


def nyfed_keys():
    return [k for keys in NYFED.values() for k in keys]


def nyfed(name):
    """Week -> dollars, the sum of the New York Fed's continuous totals; a week with any '*' is left out."""
    parts = []
    for key in NYFED[name]:
        rows = json.loads((RAW / "nyfed" / f"{key}.json").read_text())["pd"]["timeseries"]
        parts.append({r["asofdate"]: float(r["value"]) * 1e6 for r in rows if r["value"] != "*"})  # $ millions
    return {w: sum(p[w] for p in parts) for w in set.intersection(*(set(p) for p in parts))}


def agreement(total, ofr_series):
    """Share of overlapping weeks in which the two agree within 1% (second amendment's check)."""
    common = [w for w in ofr_series if w in total and ofr_series[w]]
    ok = sum(abs(total[w] / ofr_series[w] - 1) <= 0.01 for w in common)
    return {"n_weeks": len(common), "share_within_1pct": round(ok / len(common) * 100, 1) if common else None}


def ofr(key):
    return {d: float(v) for d, v in json.loads((RAW / f"{key}.json").read_text()) if v is not None}


def fred(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def pct(a, b):
    return round((b / a - 1) * 100, 2)


def window_change(series, a_end, b_start):
    """Percent change from the mean of the four observations up to a_end to the mean of the four from b_start."""
    keys = sorted(series)
    a = [series[k] for k in keys if k <= a_end][-4:]
    b = [series[k] for k in keys if k >= b_start][:4]
    if len(a) < 4 or len(b) < 4:
        return None
    return pct(statistics.fmean(a), statistics.fmean(b))


def panic_days(vix, d10, baa):
    """(date, ΔT bp, ΔBaa bp) on study 09's panic days, with both yields observed on both days."""
    days = sorted(vix)
    out = []
    for prev, d in zip(days, days[1:]):
        if d < "1990-01-01" or vix[d] < vix[prev] * (1 + PANIC_RISE):
            continue
        if all(x in s for x in (prev, d) for s in (d10, baa)):
            out.append((d, round((d10[d] - d10[prev]) * 100, 1), round((baa[d] - baa[prev]) * 100, 1)))
    return out


def share_up(rows):
    return sum(r[2] > 0 for r in rows) / len(rows) * 100 if rows else None


def boot_share(rows, rng):
    years = sorted({r[0][:4] for r in rows})
    by_year = {y: [r for r in rows if r[0][:4] == y] for y in years}
    draws = []
    for _ in range(DRAWS):
        sample = [r for y in rng.choices(years, k=len(years)) for r in by_year[y]]
        if sample:
            draws.append(share_up(sample))
    return stats.interval(draws)


def size(s, weeks, leg):
    """Q1 for one leg: corporate over corporate plus Treasury, on the first and last 13 complete weeks."""
    first, last = weeks[:13], weeks[-13:]
    mean = lambda key, ws: statistics.fmean(s[key][w] for w in ws)  # noqa: E731
    share = lambda ws: mean(f"{leg}_corporate", ws) / (mean(f"{leg}_corporate", ws) + mean(f"{leg}_treasury", ws))  # noqa: E731
    return {"weeks": [weeks[0], weeks[-1]], "n_weeks": len(weeks), "first_window": [first[0], first[-1]],
            "last_window": [last[0], last[-1]],
            "corporate_share_first_pct": round(share(first) * 100, 2),
            "corporate_share_last_pct": round(share(last) * 100, 2),
            **{f"{c}_bn_{p}": round(mean(f"{leg}_{c}", ws) / 1e9, 1) for c in ("corporate", "treasury")
               for p, ws in (("first", first), ("last", last))},
            "corporate_growth_pct": pct(mean(f"{leg}_corporate", first), mean(f"{leg}_corporate", last)),
            "treasury_growth_pct": pct(mean(f"{leg}_treasury", first), mean(f"{leg}_treasury", last))}


def measures():
    old = {k: ofr(k) for k in OFR}
    new = {k: nyfed(k) for k in NYFED}
    checks = {k: agreement(new[k], old[k]) for k in ("rp_corporate", "rrp_corporate")}
    for k, c in checks.items():
        if c["share_within_1pct"] is None or c["share_within_1pct"] < 95:
            raise ValueError(f"{k}: the New York Fed total does not match the OFR series ({c}); the design says stop")
    q1 = {"check_against_ofr_2015_2021": checks}
    for leg in ("rp", "rrp"):
        weeks = sorted(set(new[f"{leg}_corporate"]) & set(new[f"{leg}_treasury"]))
        q1[leg] = size(new, weeks, leg)
    q1["small"] = q1["rp"]["corporate_share_last_pct"] < 10
    q1["grew_faster_than_treasury"] = q1["rp"]["corporate_growth_pct"] > q1["rp"]["treasury_growth_pct"]
    q2 = {"march_2020_ofr": {}, "march_2020_totals": {}, "april_2025_totals": {}}
    for leg in ("rp", "rrp"):
        for c in ("corporate", "treasury"):
            key = f"{leg}_{c}"
            q2["march_2020_ofr"][f"{key}_pct"] = window_change(old[key], *WINDOWS["march_2020"])
            q2["march_2020_totals"][f"{key}_pct"] = window_change(new[key], *WINDOWS["march_2020"])
            q2["april_2025_totals"][f"{key}_pct"] = window_change(new[key], *WINDOWS["april_2025"])
    m = q2["march_2020_ofr"]
    q2["march_2020_pulled_back_from_corporate"] = (m["rp_corporate_pct"] < 0
                                                    and m["rp_corporate_pct"] <= m["rp_treasury_pct"] - 10)
    rows = panic_days(fred("VIXCLS"), fred("DGS10"), fred("DBAA"))
    fail, haven = [r for r in rows if r[1] > 0], [r for r in rows if r[1] <= 0]
    rng = random.Random(SEED)
    lo, hi = boot_share(fail, rng)
    q3 = {"n_panic_days": len(rows), "n_haven_failure": len(fail), "n_haven": len(haven),
          "baa_up_on_haven_failure_pct": round(share_up(fail), 1), "ci95": [round(lo, 1), round(hi, 1)],
          "no_offset": lo > 50,
          "mean_on_haven_failure_bp": {"dT": round(statistics.fmean(r[1] for r in fail), 1),
                                       "dBaa": round(statistics.fmean(r[2] for r in fail), 1)},
          "mean_on_haven_days_bp": {"dT": round(statistics.fmean(r[1] for r in haven), 1),
                                    "dBaa": round(statistics.fmean(r[2] for r in haven), 1)},
          "by_era": [{"era": f"{a[:4]}-{b[:4]}", "n": len(e := [r for r in rows if a <= r[0] <= b]),
                      "baa_up_pct": round(share_up(e), 1) if e else None,
                      "treasury_up_pct": round(sum(r[1] > 0 for r in e) / len(e) * 100, 1) if e else None}
                     for a, b in ERAS],
          "panic_days_2020_on": [{"date": r[0], "dT_bp": r[1], "dBaa_bp": r[2]} for r in rows if r[0] >= "2020"]}
    return {"Q1_size": q1, "Q2_stress_windows": q2, "Q3_panic_days": q3, "Q4_2008": q4_2008()}


def main():
    fetch()
    result = {"design": "docs/design-study-15-corporate-bonds.md", "manifest": "metadata/s15_manifest.json",
              "seed": SEED, "draws": DRAWS, **measures()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "Q3_panic_days"}, indent=1))
    print(json.dumps({k: v for k, v in result["Q3_panic_days"].items() if k != "panic_days_2020_on"}, indent=1))


if __name__ == "__main__":
    main()
