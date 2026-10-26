"""Study 11: what is hedge-fund repo funding now that the basis trade has shrunk? Descriptive.

Design: docs/design-study-11-what-repo-funds.md (committed before the data was fetched).
Inputs: data/raw/s11/ (fetch_study11.py), data/raw/dtcc/packages_daily.csv (fetch_dtcc_packages.py),
data/raw/chain/CFTC_TFF_treasury.json (fetch_chain.py). Writes results/study-11/result.json and
dtcc_packages_monthly.csv.
"""
import csv
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
import study_03_chain as s3  # noqa: E402
from fetch_study11 import STRATEGIES  # noqa: E402

RAW = ROOT / "data" / "raw" / "s11"
OUT = ROOT / "results" / "study-11"
BASE = "2024-09-30"
PACKAGE_RISE_PP, IRD_GROWTH, E4_GAP_PP = 5.0, 0.10, 5.0


def check_manifest():
    manifest = json.loads((ROOT / "metadata" / "s11_manifest.json").read_text())
    stale = [n for n, m in manifest.items() if hashlib.sha256((RAW / n).read_bytes()).hexdigest() != m["sha256"]]
    if stale:
        raise ValueError(f"data/raw/s11 differs from metadata/s11_manifest.json for {stale}")


def ofr(mnemonic):
    return {d: v / 1e9 for d, v in json.loads((RAW / f"{mnemonic}.json").read_text()) if v is not None}


def growth(s, latest):
    return s[latest] / s[BASE] - 1


def packages():
    """month -> {bucket: {"package": notional, "single": notional}} and overall package share by month."""
    monthly = {}
    with open(ROOT / "data" / "raw" / "dtcc" / "packages_daily.csv", newline="") as f:
        for r in csv.DictReader(f):
            if not r["bucket"]:
                continue
            m = monthly.setdefault(r["date"][:7], {})
            b = m.setdefault(r["bucket"], {"package": 0.0, "single": 0.0, "trades": 0})
            b["package" if r["package"] == "1" else "single"] += float(r["notional"]) / 1e9
            b["trades"] += int(r["trades"])
    months = sorted(monthly)[:-1]  # the latest month may be partial
    share = {}
    for m in months:
        pkg = sum(b["package"] for b in monthly[m].values())
        tot = pkg + sum(b["single"] for b in monthly[m].values())
        share[m] = pkg / tot * 100
    return {m: monthly[m] for m in months}, share


def tic_cayman():
    lines = (RAW / "TIC_slt_table5.txt").read_text().splitlines()
    header = next(l for l in lines if l.startswith("Country\t")).split("\t")
    row = next(l for l in lines if l.startswith("Cayman Islands\t")).split("\t")
    return {m: float(v) for m, v in zip(header[1:], row[1:]) if m.strip() and v.strip()}


def main():
    check_manifest()
    s3.check_manifest()
    repo, lt, st = ofr("FPF-BORROW_REPO_SUM"), ofr("FPF-ASSETCLASS_LTREASURY_SUM"), ofr("FPF-ASSETCLASS_STREASURY_SUM")
    ird, ird_l, ird_s = (ofr("FPF-ASSETCLASS_IRD_GNE_SUM"), ofr("FPF-ASSETCLASS_IRD_LGNE_SUM"),
                         ofr("FPF-ASSETCLASS_IRD_SGNE_SUM"))
    latest = max(repo)
    fut = h.complete_months(s3.cftc_net_short(), "daily")
    fut_base, fut_latest = fut[BASE[:7]], fut[latest[:7]]

    monthly, share = packages()
    months = sorted(share)
    first, last = months[:3], months[-3:]
    share_first = sum(share[m] for m in first) / 3
    share_last = sum(share[m] for m in last) / 3
    e1a = share_last - share_first >= PACKAGE_RISE_PP
    e1b = growth(ird, latest) >= IRD_GROWTH and fut_latest < fut_base

    borrow = {s: ofr(f"FPF-STRATEGY_{s}_BORROWING_SUM") for s in STRATEGIES}
    gne = {s: ofr(f"FPF-STRATEGY_{s}_GNE_SUM") for s in STRATEGIES}
    d_borrow = {s: borrow[s][latest] - borrow[s][BASE] for s in STRATEGIES}
    total_change = sum(d_borrow.values())
    shares = {s: d_borrow[s] / total_change * 100 for s in STRATEGIES}
    e2, e3 = shares["MACRO"] > shares["RV"], shares["RV"] > shares["MACRO"]
    e4_gap = (growth(repo, latest) - growth(lt, latest)) * 100
    e4 = e4_gap >= E4_GAP_PP

    cayman = tic_cayman()
    c_first, c_last = min(cayman), max(cayman)

    r1 = lambda v: round(v, 1)  # noqa: E731
    result = {
        "design": "docs/design-study-11-what-repo-funds.md", "manifest": "metadata/s11_manifest.json",
        "base_quarter": BASE, "latest_quarter": latest,
        "levels_bn": {k: {"base": r1(s[BASE]), "latest": r1(s[latest]), "growth_pct": r1(growth(s, latest) * 100)}
                      for k, s in (("hf_repo_borrowing", repo), ("hf_long_treasury", lt), ("hf_short_treasury", st),
                                   ("hf_ird_gross_notional", ird), ("hf_ird_long", ird_l), ("hf_ird_short", ird_s))},
        "levfund_futures_net_short_bn": {"base_month": BASE[:7], "base": r1(fut_base), "latest_month": latest[:7],
                                         "latest": r1(fut_latest),
                                         "growth_pct": r1((fut_latest / fut_base - 1) * 100)},
        "E1_swap_spread_trades": {
            "a_package_share_pct": {"first_months": first, "first": r1(share_first), "last_months": last,
                                    "last": r1(share_last), "change_pp": r1(share_last - share_first),
                                    "points_to_E1a": e1a},
            "b_ird_grew_while_futures_fell": e1b, "points_to_E1": e1a and e1b},
        "E2_E3_strategy_share_of_borrowing_change_pct": {s: r1(v) for s, v in shares.items()},
        "borrowing_by_strategy_bn": {s: {"base": r1(borrow[s][BASE]), "latest": r1(borrow[s][latest])} for s in STRATEGIES},
        "gne_by_strategy_bn": {s: {"base": r1(gne[s][BASE]), "latest": r1(gne[s][latest])} for s in STRATEGIES},
        "total_borrowing_change_bn": r1(total_change),
        "points_to_E2_macro": e2, "points_to_E3_relative_value": e3,
        "E4_repo_minus_long_treasury_growth_pp": r1(e4_gap), "points_to_E4_non_treasury": e4,
        "tic_cayman_bn": {"coverage": [c_first, c_last], "first": cayman[c_first], "last": cayman[c_last],
                          "growth_pct": r1((cayman[c_last] / cayman[c_first] - 1) * 100),
                          "levfund_futures_short_growth_same_months_pct":
                              r1((fut[c_last] / fut[c_first] - 1) * 100) if c_first in fut and c_last in fut else None,
                          "decides_nothing": True},
        "package_share_by_month_pct": {m: r1(share[m]) for m in months},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    with open(OUT / "dtcc_packages_monthly.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "bucket", "package_notional_bn", "single_notional_bn", "trades"])
        for m in months:
            for b, v in sorted(monthly[m].items()):
                w.writerow([m, b, round(v["package"], 1), round(v["single"], 1), v["trades"]])
    print(json.dumps({k: v for k, v in result.items() if k != "package_share_by_month_pct"}, indent=1))


if __name__ == "__main__":
    main()
