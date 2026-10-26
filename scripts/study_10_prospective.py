"""Study 10: three prospective tests, frozen with docs/design-study-10-prospective.md on 26 October 2026.

Reads the watch's data (data/raw/watch/, results/watch/swap_daily.csv; run scripts/watch.py first) and writes
results/study-10/status.json. Each test reports "pending" until its data is complete, then its verdict by the design's
rules. Run monthly by .github/workflows/watch.yml.
"""
import csv
import datetime as dt
import json
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
from spillovers import stats  # noqa: E402
import fetch_chain  # noqa: E402

RAW = ROOT / "data" / "raw" / "watch"
OUT = ROOT / "results" / "study-10"
DEADLINES = {"D1_cash_clearing": ("2026-12-31", ("2024-12-31", "2025-12-31")),
             "D2_repo_clearing": ("2027-06-30", ("2025-06-30", "2026-06-30"))}
FORWARD_START = "2026-11-02"
FINAL_DATE = "2028-12-31"
LEAD_MIN_SHOCKS, LEAD_SEED, LEAD_DRAWS = 10, 20261101, 5000
REFERENCE_ONSET = "2025-03-10"


# --- data ---------------------------------------------------------------------------------------------------------
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
    return {d: float(v) for d, v in json.loads((RAW / name).read_text()) if v is not None}


def load():
    sofr, iorb = fred("SOFR"), fred("IORB")
    days = sorted(d for d in sofr if d in iorb)
    with open(RAW / "OFR_FSI.csv", newline="") as f:
        fsi = {r["Date"]: float(r["OFR FSI"]) for r in csv.DictReader(f) if r["OFR FSI"]}
    with open(ROOT / "results" / "watch" / "swap_daily.csv", newline="") as f:
        swap = {r["date"]: float(r["spread_10y_bp"]) for r in csv.DictReader(f) if r["spread_10y_bp"]}
    futures = {}
    for r in json.loads((RAW / "CFTC_TFF_treasury.json").read_text()):
        d = r["report_date_as_yyyy_mm_dd"][:10]
        face = fetch_chain.CFTC_CONTRACTS[r["cftc_contract_market_code"]]
        futures[d] = futures.get(d, 0.0) + (float(r["lev_money_positions_short"])
                                            - float(r["lev_money_positions_long"])) * face / 1e9
    return {"days": days, "spread": {d: (sofr[d] - iorb[d]) * 100 for d in days}, "iorb": iorb,
            "baa": {d: v * 100 for d, v in fred("BAA10Y").items()}, "fsi": fsi, "swap": swap, "futures": futures,
            "sponsored": ofr("OFRHF_FICC-SPONSORED_REVREPO_VOL.json"), "dvp": ofr("OFR_REPO-DVP_TV_TOT-P.json"),
            "hf_repo": ofr("OFRHF_FPF-BORROW_REPO_SUM.json")}


# --- calendar -----------------------------------------------------------------------------------------------------
def non_calendar(days, iorb):
    """Set of non-calendar days by the design's rule; days in a month not yet complete are left out."""
    by_month = {}
    for d in days:
        by_month.setdefault(d[:7], []).append(d)
    last_month = max(by_month)
    out = set()
    for month, ds in by_month.items():
        if month == last_month:
            continue
        for i, d in enumerate(ds):
            k = days.index(d)
            if i < 2 or i >= len(ds) - 2 or 13 <= int(d[8:10]) <= 17:
                continue
            if k > 0 and iorb.get(d) != iorb.get(days[k - 1]):
                continue
            out.add(d)
    return out


def offset(days, d, n):
    """The business day n days from d, or None beyond the data."""
    i = days.index(d) + n
    return days[i] if 0 <= i < len(days) else None


def on_or_before(series, d, max_gap=7):
    """series' value on d or the nearest earlier date within max_gap calendar days."""
    day = dt.date.fromisoformat(d)
    for k in range(max_gap + 1):
        key = (day - dt.timedelta(days=k)).isoformat()
        if key in series:
            return series[key]
    return None


# --- Part A -------------------------------------------------------------------------------------------------------
def day_measures(data, d, noncal):
    days, spread = data["days"], data["spread"]
    if d not in days or offset(days, d, 20) is None:
        return None
    prev = offset(days, d, -1)
    window = [x for x in days[days.index(d) - 10: days.index(d) + 11] if x in noncal]
    moves = [spread[x] - spread[offset(days, x, -1)] for x in window]
    s0, s1 = on_or_before(data["swap"], offset(days, d, -20)), on_or_before(data["swap"], offset(days, d, 20))
    return {"d_spread_bp": round(spread[d] - spread[prev], 2),
            "sd_noncal_d_spread_bp": round(statistics.pstdev(moves), 3) if len(moves) >= 5 else None,
            "n_noncal_days": len(moves),
            "swap_change_bp": None if s0 is None or s1 is None else round(s1 - s0, 2)}


def monthly_share(data, months):
    sp, dvp = h.complete_months(data["sponsored"], "daily"), h.complete_months(data["dvp"], "daily")
    vals = [sp[m] / dvp[m] * 100 for m in months if m in sp and m in dvp]
    return round(statistics.fmean(vals), 3) if len(vals) == len(months) else None


def part_a(data, noncal):
    out = {}
    for name, (deadline, comparators) in DEADLINES.items():
        d = day_measures(data, deadline, noncal)
        comps = {c: day_measures(data, c, noncal) for c in comparators}
        before = [h.month_add(deadline[:7], -k) for k in (2, 1, 0)]
        after = [h.month_add(deadline[:7], k) for k in (1, 2, 3)]
        share_before, share_after = monthly_share(data, before), monthly_share(data, after)
        a1 = None if share_before is None or share_after is None else round(share_after - share_before, 3)
        entry = {"deadline": deadline, "comparators": comps,
                 "A1_sponsored_share_change_pp": a1, "A1_migration_jump": None if a1 is None else a1 >= 3}
        if d is None or any(v is None for v in comps.values()) or d["sd_noncal_d_spread_bp"] is None:
            out[name] = {"status": "pending", **entry, "deadline_measures": d}
            continue
        c = list(comps.values())
        relief_day = all(d["d_spread_bp"] <= x["d_spread_bp"] - 2 for x in c)
        disruption = all(x["sd_noncal_d_spread_bp"] and d["sd_noncal_d_spread_bp"] >= 1.5 * x["sd_noncal_d_spread_bp"]
                         for x in c)
        relief_swaps = d["swap_change_bp"] is not None and all(
            x["swap_change_bp"] is not None and d["swap_change_bp"] > x["swap_change_bp"] for x in c)
        if relief_day and relief_swaps and not disruption:
            verdict = "relief"
        elif disruption and not relief_day:
            verdict = "mixed" if relief_swaps else "disruption"
        elif disruption:
            verdict = "mixed"
        else:
            verdict = "no visible effect"
        out[name] = {"status": "complete", **entry, "deadline_measures": d, "A2_relief_on_day": relief_day,
                     "A3_disruption": disruption, "A4_relief_in_swaps": relief_swaps, "verdict": verdict}
    # A5, descriptive: sponsored reverse repo / hedge-fund repo, quarterly
    sp = h.complete_months(data["sponsored"], "daily")
    hf = h.complete_months(data["hf_repo"], "quarterly")
    a5 = {}
    for q in ("2026-04", "2027-04", "2027-07"):
        months = [h.month_add(q, k) for k in range(3)]
        if all(m in sp for m in months) and q in hf:
            a5[q[:4] + "Q" + str((int(q[5:7]) - 1) // 3 + 1)] = round(statistics.fmean(sp[m] for m in months) / hf[q], 3)
    out["A5_sponsored_over_hf_repo"] = a5
    return out


# --- Part B -------------------------------------------------------------------------------------------------------
def part_b(data, noncal, today):
    days, spread, baa = data["days"], data["spread"], data["baa"]
    shocks, others = [], []
    for d in sorted(noncal):
        if d < FORWARD_START:
            continue
        prev, nxt = offset(days, d, -1), offset(days, d, 1)
        if nxt is None or prev not in baa or nxt not in baa:
            continue
        y = baa[nxt] - baa[prev]
        (shocks if spread[d] - spread[prev] >= 5 else others).append((d, round(y, 2)))
    out = {"from": FORWARD_START, "n_shock_days": len(shocks), "n_other_days": len(others), "shock_days": shocks}
    if len(shocks) < LEAD_MIN_SHOCKS and today < FINAL_DATE:
        return {"status": "pending", **out}
    if len(shocks) < 2 or len(others) < 30:
        return {"status": "complete", **out, "verdict": "too few days to test"}
    rng = random.Random(LEAD_SEED)
    hit, rest = [y for _, y in shocks], [y for _, y in others]
    draws = [a - b for a, b in zip(stats.boot_means(hit, LEAD_DRAWS, rng), stats.boot_means(rest, LEAD_DRAWS, rng))]
    lo, hi = stats.interval(draws)
    point = statistics.fmean(hit) - statistics.fmean(rest)
    return {"status": "complete", **out, "difference_bp": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)],
            "verdict": "confirmed" if lo > 0 else "not confirmed"}


# --- Part C -------------------------------------------------------------------------------------------------------
def stress_episode(data, noncal, onset):
    fsi_days = sorted(data["fsi"])
    i = fsi_days.index(onset)
    if i + 40 >= len(fsi_days):
        return None
    start, end = fsi_days[i - 5], fsi_days[i + 40]
    window = [d for d in data["days"] if start <= d <= end]
    c1 = max((data["spread"][d] for d in window if d in noncal), default=None)
    reports = sorted(data["futures"])
    before = [r for r in reports if r < onset]
    after = [r for r in reports if onset <= r <= (dt.date.fromisoformat(onset) + dt.timedelta(weeks=8)).isoformat()]
    c2 = None
    if before and after:
        base = data["futures"][before[-1]]
        c2 = round((min(data["futures"][r] for r in after) / base - 1) * 100, 2) if base > 0 else None
    swaps = [data["swap"][d] for d in window if d in data["swap"]]
    s0 = on_or_before(data["swap"], start)
    c3 = round(min(swaps) - s0, 2) if swaps and s0 is not None else None
    strained, unwind = c1 is not None and c1 >= 10, c2 is not None and c2 <= -10
    verdict = "the chain gave way" if strained and unwind else "strained" if strained or unwind else "held"
    return {"onset": onset, "window": [start, end], "C1_max_noncal_spread_bp": None if c1 is None else round(c1, 2),
            "C1_strained": strained, "C2_futures_short_change_pct": c2, "C2_unwind": unwind,
            "C3_swap_spread_change_bp": c3, "verdict": verdict}


def part_c(data, noncal, today):
    fsi_days = sorted(data["fsi"])
    onset = next((fsi_days[i] for i in range(20, len(fsi_days)) if fsi_days[i] >= FORWARD_START
                  and data["fsi"][fsi_days[i]] - data["fsi"][fsi_days[i - 20]] >= 1.0), None)
    reference = stress_episode(data, noncal, REFERENCE_ONSET) if REFERENCE_ONSET in data["fsi"] else None
    if onset is None:
        status = "complete" if today >= FINAL_DATE else "pending"
        return {"status": status, "onset": None, "verdict": "no stress event" if status == "complete" else None,
                "reference_april_2025": reference}
    episode = stress_episode(data, noncal, onset)
    if episode is None:
        return {"status": "pending", "onset": onset, "reference_april_2025": reference}
    return {"status": "complete", **episode, "reference_april_2025": reference}


def run(today=None):
    """Compute every test's status, write results/study-10/status.json, and return it."""
    today = today or dt.date.today().isoformat()
    data = load()
    noncal = non_calendar(data["days"], data["iorb"])
    status = {"design": "docs/design-study-10-prospective.md", "run_date": today, "data_to": data["days"][-1],
              "A_clearing_deadlines": part_a(data, noncal), "B_credit_lead": part_b(data, noncal, today),
              "C_chain_under_stress": part_c(data, noncal, today)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "status.json").write_text(json.dumps(status, indent=1) + "\n")
    return status


def main():
    print(json.dumps(run(), indent=1))


if __name__ == "__main__":
    main()
