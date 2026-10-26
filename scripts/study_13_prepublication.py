"""Study 13: pre-publication checks on the article's claims (C1-C4; C5 is a literature search, written up by hand).

Design: docs/design-study-13-prepublication.md (committed before the checks were run).
Inputs: data/raw/watch/ (scripts/watch.py), data/raw/s11/ (fetch_study11.py); fetches FRED SOFR99 and IORB into
data/raw/s13/ with metadata/s13_manifest.json. Writes results/study-13/result.json.
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import statistics
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
import watch  # noqa: E402

RAW = ROOT / "data" / "raw" / "s13"
OUT = ROOT / "results" / "study-13"
DURATION = {"042601": 1.9, "044601": 4.2, "043602": 6.3, "043607": 8.5, "020601": 12.0, "020604": 18.0}
FACE = {"042601": 200_000, "044601": 100_000, "043602": 100_000, "043607": 100_000, "020601": 100_000,
        "020604": 100_000}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for s in ("SOFR99", "IORB"):
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
        with urllib.request.urlopen(url, timeout=120) as response:
            body = response.read()
        (RAW / f"{s}.csv").write_bytes(body)
        manifest[f"{s}.csv"] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                                "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s13_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def fred(path):
    out = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for d, v in reader:
            if v not in ("", "."):
                out[d] = float(v)
    return out


def qlabel(q):
    return f"{q[:4]}Q{(int(q[5:7]) - 1) // 3 + 1}"


def main():
    fetch()
    r = {"design": "docs/design-study-13-prepublication.md", "manifest": "metadata/s13_manifest.json"}

    # C1: hedge-fund clearing proxy, year on year
    sp_daily = watch.ofr("OFRHF_FICC-SPONSORED_REPO_VOL.json")
    sp = h.complete_months(sp_daily, "daily")
    hf = h.complete_months(watch.ofr("OFRHF_FPF-BORROW_REPO_SUM.json"), "quarterly")
    share = watch.cleared_share(sp, hf)
    q = {qlabel(k): round(v, 1) for k, v in sorted(share.items()) if k >= "2023-01"}
    yoy = {k: round(v - q[f"{int(k[:4]) - 1}{k[4:]}"], 1) for k, v in q.items() if f"{int(k[:4]) - 1}{k[4:]}" in q}
    dec = {y: round(sp[f"{y}-12"] / statistics.fmean(sp[f"{y}-{m}"] for m in ("10", "11")) * 100 - 100, 1)
           for y in ("2023", "2024", "2025") if all(f"{y}-{m}" in sp for m in ("10", "11", "12"))}
    survives = (yoy.get("2026Q2", 0) < 0) or (yoy.get("2026Q1", 0) < 0)
    r["C1_clearing_proxy"] = {"quarterly_pct": q, "change_vs_same_quarter_year_before_pp": yoy,
                              "december_volume_vs_oct_nov_mean_pct": dec, "slipped_claim_survives": survives}

    # C2: duration-weighted basis proxy (net short x face x duration), monthly
    raw = json.loads((ROOT / "data" / "raw" / "watch" / "CFTC_TFF_treasury.json").read_text())
    face, dur = {}, {}
    for row in raw:
        d, c = row["report_date_as_yyyy_mm_dd"][:10], row["cftc_contract_market_code"]
        net = float(row["lev_money_positions_short"]) - float(row["lev_money_positions_long"])
        face[d] = face.get(d, 0.0) + net * FACE[c] / 1e9
        dur[d] = dur.get(d, 0.0) + net * FACE[c] * DURATION[c] / 1e9
    fm, dm = h.complete_months(face, "daily"), h.complete_months(dur, "daily")
    def peak_and_latest(s):
        recent = {k: v for k, v in s.items() if k >= "2020-01"}
        p = max(recent, key=recent.get)
        last = max(s)
        return {"peak_month": p, "peak": round(s[p], 1), "latest_month": last, "latest": round(s[last], 1),
                "change_from_peak_pct": round((s[last] / s[p] - 1) * 100, 1)}
    c2 = {"face_value_bn": peak_and_latest(fm), "duration_weighted_bn_years": peak_and_latest(dm)}
    c2["avg_duration_years"] = {k: round(dm[k] / fm[k], 2) for k in ("2024-10", "2025-06", "2026-06", max(fm))}
    dw = c2["duration_weighted_bn_years"]
    c2["claim_survives"] = dw["change_from_peak_pct"] <= -15 and dw["peak_month"][:4] in ("2024", "2025")
    r["C2_basis_proxy_duration"] = c2

    # C3: futures cover of long Treasuries; derivative growth before and after Q3 2024
    s11 = lambda m: {k: v / 1e9 for k, v in json.loads((ROOT / "data" / "raw" / "s11" / f"{m}.json").read_text())}  # noqa
    lt, ird = s11("FPF-ASSETCLASS_LTREASURY_SUM"), s11("FPF-ASSETCLASS_IRD_GNE_SUM")
    fq = lambda d: fm[d[:7]]  # noqa: E731  futures short in the quarter-end month
    cover = {d: round(fq(d) / lt[d] * 100, 1) for d in ("2022-12-31", "2024-09-30", "2026-06-30")}
    g_before = ird["2024-09-30"] / ird["2022-12-31"] - 1
    g_after = ird["2026-06-30"] / ird["2024-09-30"] - 1
    r["C3_substitution"] = {
        "futures_short_pct_of_long_treasuries": cover,
        "ird_growth_pct": {"2022Q4_to_2024Q3": round(g_before * 100, 1), "2024Q3_to_2026Q2": round(g_after * 100, 1)},
        "ird_bn": {k: round(ird[k]) for k in ("2022-12-31", "2024-09-30", "2026-06-30")},
        "strengthened": cover["2026-06-30"] < cover["2024-09-30"] and g_after > g_before}

    # C4: SOFR 99th percentile in October 2026
    s99, iorb = fred(RAW / "SOFR99.csv"), fred(RAW / "IORB.csv")
    days = sorted(d for d in s99 if d.startswith("2026-10") and d in iorb)
    tail = {d: round((s99[d] - iorb[d]) * 100, 1) for d in days}
    r["C4_sofr_tail_october"] = {"days": tail, "max_bp": max(tail.values()), "data_to": days[-1],
                                 "claim_survives": max(tail.values()) <= 10}
    # C6, post hoc (added after reading Copeland and Kahn, Liberty Street Economics, 8 Oct 2025, which dates the surge
    # in sponsored membership to August 2022): which first break date fits the clearing series best?
    import study_03_chain as s3
    from study_04_amplification import ols
    from study_07_clearing import index
    m = h.complete_months
    tot, ficc = m(s3.ofr("OFR_MMF-MMF_RP_TOT-M.json"), "monthly"), m(s3.ofr("OFR_MMF-MMF_RP_wFICC-M.json"), "monthly")
    fed = m(s3.ofr("OFR_MMF-MMF_RP_wFR-M.json"), "monthly")
    priv = {k: tot[k] - fed[k] for k in tot if k in fed and tot[k] - fed[k] > 0}
    rev, dvp = m(s3.ofr("OFRHF_FICC-SPONSORED_REVREPO_VOL.json"), "daily"), m(s3.ofr("OFR_REPO-DVP_TV_TOT-P.json"), "daily")
    breaks = ["2022-06", "2022-09", "2023-03", "2023-06", "2023-09", "2023-12", "2024-03"]
    c6 = {}
    for name, series in (("ficc_share_mmf_repo", s3.ratio(ficc, tot)), ("ficc_share_mmf_private_repo", s3.ratio(ficc, priv)),
                         ("sponsored_revrepo_pct_dvp", s3.ratio(rev, dvp))):
        series = {k: v for k, v in series.items() if k >= "2020-03"}
        ms = sorted(series)
        fits = {}
        for b in breaks:
            x = [(index(k), max(0, index(k) - index(b)), max(0, index(k) - index("2025-02"))) for k in ms]
            y = [series[k] for k in ms]
            c = ols(x, y)
            sse = sum((a - (c[0] + sum(q * v for q, v in zip(c[1:], row)))) ** 2 for a, row in zip(y, x))
            fits[b] = {"sse": round(sse, 1), "slope_change_pp_per_year": round(c[2] * 12, 1),
                       "slope_change_at_2025_02_pp_per_year": round(c[3] * 12, 1)}
        c6[name] = {"fits_by_first_break": fits, "best_first_break": min(fits, key=lambda b: fits[b]["sse"]),
                    "values": {k: round(series[k], 1) for k in ("2022-06", "2022-09", "2022-12", "2023-06", "2023-11",
                                                                "2024-06", "2025-01", max(series)) if k in series}}
    r["C6_post_hoc_clearing_break_date"] = c6
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
