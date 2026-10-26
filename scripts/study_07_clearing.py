"""Study 07, part 1: is the growth of cleared repo a migration ahead of the SEC's clearing mandate?

Design: docs/design-study-07-watch.md (committed before the run).
Inputs: data/raw/chain/ (fetch_chain.py). Writes results/study-07/result.json.
"""
import json
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
from spillovers import stats  # noqa: E402
import study_03_chain as s3  # noqa: E402
from study_04_amplification import ols  # noqa: E402

BREAKS = ("2023-12", "2025-02")
SEED, DRAWS, BLOCK = 20261031, 2000, 6
OUT = ROOT / "results" / "study-07"


def index(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def design(months):
    t1, t2 = index(BREAKS[0]), index(BREAKS[1])
    return [(index(m), max(0, index(m) - t1), max(0, index(m) - t2)) for m in months]


def segmented(series, rng):
    months = sorted(series)
    x = design(months)
    y = [series[m] for m in months]
    coef = ols(x, y)
    fitted = [coef[0] + sum(c * v for c, v in zip(coef[1:], row)) for row in x]
    resid = [a - b for a, b in zip(y, fitted)]
    n = len(resid)
    boot = []
    for _ in range(DRAWS):
        res = []
        while len(res) < n:
            s = rng.randrange(n - BLOCK + 1)
            res.extend(resid[s:s + BLOCK])
        ystar = [f + r for f, r in zip(fitted, res[:n])]
        boot.append(ols(x, ystar))

    def summ(i, scale=12):
        point = coef[i] * scale
        lo, hi = stats.interval([b[i] * scale for b in boot])
        return {"estimate": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)], "excludes_zero": bool(lo > 0 or hi < 0)}

    slope_before = summ(1)
    change_at_adoption = summ(2)
    change_at_extension = summ(3)
    return {"from": months[0], "to": months[-1], "n_months": n,
            "units": "percentage points per year",
            "slope_before_2023_12": slope_before,
            "slope_2023_12_to_2025_01": round((coef[1] + coef[2]) * 12, 3),
            "slope_from_2025_02": round((coef[1] + coef[2] + coef[3]) * 12, 3),
            "change_at_adoption_2023_12": change_at_adoption,
            "change_at_extension_2025_02": change_at_extension,
            "values": {m: round(series[m], 2) for m in ("2019-06", "2023-11", "2025-01", months[-1]) if m in series}}


def main():
    s3.check_manifest()
    rng = random.Random(SEED)
    m = h.complete_months
    tot = m(s3.ofr("OFR_MMF-MMF_RP_TOT-M.json"), "monthly")
    ficc = m(s3.ofr("OFR_MMF-MMF_RP_wFICC-M.json"), "monthly")
    dvp = m(s3.ofr("OFR_REPO-DVP_TV_TOT-P.json"), "daily")
    rev = m(s3.ofr("OFRHF_FICC-SPONSORED_REVREPO_VOL.json"), "daily")
    rep = m(s3.ofr("OFRHF_FICC-SPONSORED_REPO_VOL.json"), "daily")
    series = {"C1_ficc_share_of_mmf_repo": s3.ratio(ficc, tot),
              "M6_sponsored_revrepo_pct_dvp": s3.ratio(rev, dvp),
              "M6_sponsored_repo_pct_dvp": s3.ratio(rep, dvp)}
    fits = {k: segmented(v, rng) for k, v in series.items()}
    # post hoc (added after the first run): the Fed's RRP drained in 2023-24, the same window as the adoption break,
    # which lifts FICC's share of *total* money-fund repo mechanically. Re-fit on private repo (total minus the Fed).
    fed = m(s3.ofr("OFR_MMF-MMF_RP_wFR-M.json"), "monthly")
    private = {k: tot[k] - fed[k] for k in tot if k in fed and tot[k] - fed[k] > 0}
    post_hoc = {"C1_ficc_share_of_mmf_private_repo": segmented(s3.ratio(ficc, private), rng)}
    decisive = ("C1_ficc_share_of_mmf_repo", "M6_sponsored_revrepo_pct_dvp")
    met = [k for k in decisive if fits[k]["change_at_adoption_2023_12"]["excludes_zero"]
           and fits[k]["change_at_adoption_2023_12"]["estimate"] > 0]
    verdict = "supported" if len(met) == 2 else "partly supported" if met else "not supported"
    result = {"design": "docs/design-study-07-watch.md", "manifest": "metadata/chain_manifest.json", "seed": SEED,
              "breaks": BREAKS, "verdict_migration": verdict, "series_meeting_rule": met, "fits": fits,
              "post_hoc": post_hoc}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
