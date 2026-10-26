"""Study 03: map of the chain (H1). Who borrows in repo against Treasuries, who lends, through which channel, and
how that has changed.

Design: docs/design-study-03-chain.md (committed before the first run).
Inputs: data/raw/chain/ (scripts/fetch_chain.py) and data/panel.csv (scripts/build_panel.sh).
Writes results/study-03/result.json and chart.svg.
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
from fetch_chain import CFTC_CONTRACTS  # noqa: E402

RAW = ROOT / "data" / "raw" / "chain"
OUT = ROOT / "results" / "study-03"
SNAPSHOTS = ("2007-06", "2014-06", "2019-06", "2026-06")
BASE, NOW = "2019-06", "2026-06"
PRIVATE = ("ficc", "dfi", "ffi", "ocp")  # money-fund repo counterparties counted in C2


def check_manifest():
    manifest = json.loads((ROOT / "metadata" / "chain_manifest.json").read_text())
    stale = [n for n, m in manifest.items() if hashlib.sha256((RAW / n).read_bytes()).hexdigest() != m["sha256"]]
    if stale:
        raise ValueError(f"data/raw/chain differs from metadata/chain_manifest.json for {stale}: re-run fetch_chain.py")


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
    """date -> value from an OFR timeseries file (both APIs return [[date, value], ...])."""
    return {d: float(v) for d, v in json.loads((RAW / name).read_text()) if v is not None}


def mspd():
    """date -> marketable Treasury debt held by the public, $mn, summed over security classes."""
    out = {}
    for r in json.loads((RAW / "MSPD_marketable.json").read_text())["data"]:
        out[r["record_date"]] = out.get(r["record_date"], 0.0) + float(r["debt_held_public_mil_amt"])
    return out


def cftc_net_short():
    """report date -> leveraged funds' net short in Treasury futures, face value in $bn."""
    out = {}
    for r in json.loads((RAW / "CFTC_TFF_treasury.json").read_text()):
        date = r["report_date_as_yyyy_mm_dd"][:10]
        face = CFTC_CONTRACTS[r["cftc_contract_market_code"]]
        net = float(r["lev_money_positions_short"]) - float(r["lev_money_positions_long"])
        out[date] = out.get(date, 0.0) + net * face / 1e9
    return out


def panel_dealer():
    with open(ROOT / "data" / "panel.csv", newline="") as f:
        return {r["date"]: float(r["dealer_treasury_position"]) for r in csv.DictReader(f)
                if r["dealer_treasury_position"]}


def ratio(num, den, scale=100):
    return {m: v / den[m] * scale for m, v in num.items() if m in den and den[m]}


def herfindahl(parts):
    """month -> HHI (0-1) over the given component series, on months where all are present."""
    months = set.intersection(*(set(p) for p in parts))
    out = {}
    for m in months:
        total = sum(p[m] for p in parts)
        if total > 0:
            out[m] = sum((p[m] / total) ** 2 for p in parts)
    return out


def describe(s):
    peak = max(s, key=s.get)
    latest = max(s)
    return {"from": min(s), "latest": {"month": latest, "value": round(s[latest], 3)},
            "peak": {"month": peak, "value": round(s[peak], 3)},
            "snapshots": {m: (round(s[m], 3) if m in s else None) for m in SNAPSHOTS},
            "now_percentile": round(h.percentile_of(s, s[NOW]), 1) if NOW in s else None,
            "now_top_decile": (h.percentile_of(s, s[NOW]) >= 90) if NOW in s else None,
            "now_above_2019": (s[NOW] > s[BASE]) if NOW in s and BASE in s else None}


def main():
    check_manifest()
    m = h.complete_months
    # $bn throughout
    phmt_gross = {k: v / 1e3 for k, v in m(mspd(), "monthly").items()}
    fed_treasuries = {k: v / 1e3 for k, v in m(fred("TREAST"), "daily").items()}
    phmt = {k: phmt_gross[k] - fed_treasuries[k] for k in phmt_gross if k in fed_treasuries}
    repo_all = {k: v / 1e3 for k, v in m(fred("BOGZ1FL892150005Q"), "quarterly").items()}
    hf_repo = {k: v / 1e9 for k, v in m(ofr("OFRHF_FPF-BORROW_REPO_SUM.json"), "quarterly").items()}
    hf_long = {k: v / 1e9 for k, v in m(ofr("OFRHF_FPF-ASSETCLASS_LTREASURY_SUM.json"), "quarterly").items()}
    hf_short = {k: v / 1e9 for k, v in m(ofr("OFRHF_FPF-ASSETCLASS_STREASURY_SUM.json"), "quarterly").items()}
    futures_short = m(cftc_net_short(), "daily")
    mmf = {k: {key: v / 1e9 for key, v in m(ofr(f"OFR_MMF-MMF_RP_{code}-M.json"), "monthly").items()}
           for k, code in (("total", "TOT"), ("ficc", "wFICC"), ("fed", "wFR"), ("dfi", "wDFI"), ("ffi", "wFFI"),
                           ("ocp", "wOCP"))}
    mmf = {k: s for k, s in mmf.items()}
    sponsored_repo = {k: v / 1e9 for k, v in m(ofr("OFRHF_FICC-SPONSORED_REPO_VOL.json"), "daily").items()}
    sponsored_rev = {k: v / 1e9 for k, v in m(ofr("OFRHF_FICC-SPONSORED_REVREPO_VOL.json"), "daily").items()}
    dvp = {k: v / 1e9 for k, v in m(ofr("OFR_REPO-DVP_TV_TOT-P.json"), "daily").items()}
    dealer = m(panel_dealer(), "daily")

    measures = {
        "M1_repo_all_pct_phmt": ratio(repo_all, phmt),
        "M2_hf_repo_pct_phmt": ratio(hf_repo, phmt),
        "M3_hf_long_treasury_pct_phmt": ratio(hf_long, phmt),
        "M3_hf_short_treasury_pct_phmt": ratio(hf_short, phmt),
        "M4_levfund_futures_net_short_pct_phmt": ratio(futures_short, phmt),
        "M5_mmf_repo_pct_phmt": ratio(mmf["total"], phmt),
        "M6_sponsored_repo_pct_dvp": ratio(sponsored_repo, dvp),
        "M6_sponsored_revrepo_pct_dvp": ratio(sponsored_rev, dvp),
        "M7_dealer_treasury_pct_phmt": ratio(dealer, phmt),
        "C1_ficc_share_of_mmf_repo": ratio(mmf["ficc"], mmf["total"]),
        "C2_hhi_mmf_private_counterparties": herfindahl([mmf[k] for k in PRIVATE]),
    }
    levels = {"phmt_bn": phmt, "hf_repo_bn": hf_repo, "levfund_futures_net_short_bn": futures_short,
              "mmf_repo_bn": mmf["total"], "mmf_repo_ficc_bn": mmf["ficc"], "mmf_repo_fed_bn": mmf["fed"],
              "sponsored_repo_bn": sponsored_repo, "sponsored_revrepo_bn": sponsored_rev, "dvp_bn": dvp,
              "repo_all_bn": repo_all, "dealer_treasury_bn": dealer}
    mmf_split = {k: ratio(mmf[k], mmf["total"]) for k in ("ficc", "fed", "dfi", "ffi", "ocp")}

    d = {k: describe(s) for k, s in measures.items()}
    size = all(d[k]["now_top_decile"] and d[k]["now_above_2019"]
               for k in ("M2_hf_repo_pct_phmt", "M4_levfund_futures_net_short_pct_phmt"))
    concentration = all(d[k]["now_above_2019"] for k in ("C1_ficc_share_of_mmf_repo", "C2_hhi_mmf_private_counterparties"))
    verdict = ("supported" if size and concentration else "partly supported" if size or concentration
               else "not supported")

    result = {"design": "docs/design-study-03-chain.md", "manifest": "metadata/chain_manifest.json",
              "panel_sha256": hashlib.sha256((ROOT / "data" / "panel.csv").read_bytes()).hexdigest(),
              "snapshots": SNAPSHOTS, "criteria": {"a_size": size, "b_concentration": concentration},
              "verdict": verdict, "measures": d,
              "levels": {k: describe(s) for k, s in levels.items()},
              "mmf_split_pct": {k: describe(s) for k, s in mmf_split.items()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    (OUT / "chart.svg").write_text(chart(measures, mmf_split))
    print("verdict:", verdict, result["criteria"])
    for k, v in {**d, **{f"lvl:{k}": describe(s) for k, s in levels.items()},
                 **{f"mmf%:{k}": describe(s) for k, s in mmf_split.items()}}.items():
        snaps = " ".join(f"{x[:4]}:{'-' if y is None else round(y, 2)}" for x, y in v["snapshots"].items())
        print(f"{k:42} from {v['from']} | {snaps} | latest {v['latest']['month']} {v['latest']['value']:.2f} | "
              f"peak {v['peak']['month']} {v['peak']['value']:.2f} | pct {v['now_percentile']}")


def chart(measures, mmf_split):
    panels = [
        ("M2_hf_repo_pct_phmt", "Hedge-fund repo borrowing (% of private Treasuries)", measures),
        ("M4_levfund_futures_net_short_pct_phmt", "Leveraged funds' net short Treasury futures (%)", measures),
        ("M3_hf_short_treasury_pct_phmt", "Hedge funds' short Treasury exposure (%)", measures),
        ("M5_mmf_repo_pct_phmt", "Money-fund repo lending (% of private Treasuries)", measures),
        ("ficc", "Money-fund repo through FICC (% of their repo)", mmf_split),
        ("C2_hhi_mmf_private_counterparties", "Concentration of money-fund repo (HHI, private)", measures),
        ("M6_sponsored_revrepo_pct_dvp", "FICC sponsored reverse repo (% of DVP volume)", measures),
        ("M1_repo_all_pct_phmt", "Repo liabilities, all collateral (% of private Treasuries)", measures),
        ("M7_dealer_treasury_pct_phmt", "Dealer Treasury positions (% of private Treasuries)", measures),
    ]
    cols, pw, ph, top = 3, 330, 150, 64
    rows_n = (len(panels) + cols - 1) // cols
    w, hgt = cols * pw + 20, top + rows_n * (ph + 46) + 20
    start, end = "2006-01", "2026-12"

    def mx(month, x0):
        span = (int(end[:4]) - int(start[:4])) * 12 + 11
        k = (int(month[:4]) - int(start[:4])) * 12 + int(month[5:7]) - 1
        return x0 + 40 + k / span * (pw - 56)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {hgt}" font-family="sans-serif" font-size="11">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<text x="10" y="22" font-size="15" font-weight="bold">The repo chain behind the Treasury market, 2006 to today</text>',
           '<text x="10" y="40" fill="#555">Shares of privately held marketable Treasuries unless stated. Dashed lines: '
           'June 2007, 2014, 2019, 2026. Red dot: latest reading.</text>']
    for i, (key, title, src) in enumerate(panels):
        s = {k: v for k, v in src[key].items() if k >= start}
        x0, y0 = 10 + (i % cols) * pw, top + (i // cols) * (ph + 46)
        lo, hi = min(s.values()), max(s.values())
        lo = min(lo, 0)
        pad = (hi - lo) * 0.08 or 1
        lo, hi = lo - pad, hi + pad
        y = lambda v: y0 + 22 + (hi - v) / (hi - lo) * (ph - 30)  # noqa: E731
        out.append(f'<text x="{x0 + 40}" y="{y0 + 12}" font-weight="bold">{title}</text>')
        for snap in SNAPSHOTS:
            out.append(f'<line x1="{mx(snap, x0):.1f}" x2="{mx(snap, x0):.1f}" y1="{y0 + 20}" y2="{y0 + ph - 6}" '
                       f'stroke="#9ca3af" stroke-dasharray="2,2"/>')
        out.append(f'<line x1="{x0 + 40}" x2="{x0 + pw - 16}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="#d1d5db"/>')
        months = sorted(s)
        out.append('<polyline points="' + " ".join(f"{mx(k, x0):.1f},{y(s[k]):.1f}" for k in months)
                   + '" fill="none" stroke="#1e3a8a" stroke-width="1.3"/>')
        out.append(f'<circle cx="{mx(months[-1], x0):.1f}" cy="{y(s[months[-1]]):.1f}" r="3.5" fill="#dc2626"/>')
        for v in (lo + pad, hi - pad):
            out.append(f'<text x="{x0 + 36}" y="{y(v) + 4:.1f}" text-anchor="end" fill="#555">{v:.2f}</text>')
        for yr in ("2006", "2012", "2018", "2024"):
            out.append(f'<text x="{mx(yr + "-01", x0):.1f}" y="{y0 + ph + 8}" text-anchor="middle" fill="#555">{yr}</text>')
    out.append("</svg>\n")
    return "\n".join(out)


if __name__ == "__main__":
    main()
