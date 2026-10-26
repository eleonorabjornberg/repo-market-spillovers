"""Study 09: Treasuries in a panic — safe haven or source of stress? With household debt and mortgages.

Design: docs/design-study-09-debt-volatility.md (committed before the run).
Inputs: data/raw/s09/ (fetch_study09.py), data/panel.csv and data/fomc_calendar.json (build_panel.sh).
Writes results/study-09/result.json.
"""
import csv
import hashlib
import json
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import events as ev  # noqa: E402
from spillovers import history as h  # noqa: E402
from spillovers import stats  # noqa: E402
from study_04_amplification import ols  # noqa: E402

RAW = ROOT / "data" / "raw" / "s09"
OUT = ROOT / "results" / "study-09"
SEED, DRAWS = 20261029, 2000
PANIC_RISE = 0.15
ERAS = (("1990-01-01", "1999-12-31"), ("2000-01-01", "2007-12-31"), ("2008-01-01", "2019-12-31"),
        ("2020-01-01", "2026-12-31"))
SNAPSHOTS = ("2000-03", "2007-06", "2019-06")


def check_manifest():
    manifest = json.loads((ROOT / "metadata" / "s09_manifest.json").read_text())
    stale = [n for n, m in manifest.items() if hashlib.sha256((RAW / n).read_bytes()).hexdigest() != m["sha256"]]
    if stale:
        raise ValueError(f"data/raw/s09 differs from metadata/s09_manifest.json for {stale}")


def fred(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def quarterly_ratio(num, den, scale):
    n, d = h.complete_months(fred(num), "quarterly"), h.complete_months(fred(den), "quarterly")
    return {m: n[m] / d[m] * scale for m in n if m in d}


def as_of(monthly, date, lag_months):
    """The value for the month `lag_months` before the date's month, or the latest earlier one available."""
    m = h.month_add(date[:7], -lag_months)
    earlier = [k for k in monthly if k <= m]
    return monthly[max(earlier)] if earlier else None


def block_boot(rows, fit, rng, draws=DRAWS):
    """Resample calendar years with replacement; rows carry their date first."""
    years = sorted({r[0][:4] for r in rows})
    by_year = {y: [r for r in rows if r[0][:4] == y] for y in years}
    out = []
    for _ in range(draws):
        sample = [r for y in rng.choices(years, k=len(years)) for r in by_year[y]]
        try:
            out.append(fit(sample))
        except ValueError:
            continue
    return out


def summary(point, draws):
    lo, hi = stats.interval(draws)
    return {"estimate": round(point, 4), "ci95": [round(lo, 4), round(hi, 4)], "excludes_zero": bool(lo > 0 or hi < 0)}


def main():
    check_manifest()
    rng = random.Random(SEED)
    vix, d10 = fred("VIXCLS"), fred("DGS10")
    cpi = h.complete_months(fred("CPIAUCSL"), "monthly")
    inflation = {m: (cpi[m] / cpi[h.month_add(m, -12)] - 1) * 100 for m in cpi if h.month_add(m, -12) in cpi}
    federal = quarterly_ratio("FYGFDPUN", "GDP", 100 / 1000)
    household = quarterly_ratio("CMDEBT", "GDP", 100 / 1000)

    vdates = sorted(vix)
    panic = []  # (date, d10y bp, federal debt %, inflation %)
    for prev, d in zip(vdates, vdates[1:]):
        if d < "1990-01-01" or vix[d] < vix[prev] * (1 + PANIC_RISE):
            continue
        if prev not in d10 or d not in d10:
            continue
        fd, inf = as_of(federal, d, 3), as_of(inflation, d, 1)
        if fd is None or inf is None:
            continue
        panic.append((d, (d10[d] - d10[prev]) * 100, fd, inf))

    # 1. haven, main: 1{d10y > 0} on federal debt/GDP and inflation, block bootstrap by year
    fit = lambda rows: ols([(r[2], r[3]) for r in rows], [1.0 if r[1] > 0 else 0.0 for r in rows])  # noqa: E731
    coef = fit(panic)
    boot = block_boot(panic, fit, rng)
    haven_main = {"n_panic_days": len(panic), "intercept": round(coef[0], 4),
                  "debt_per_pp": summary(coef[1], [b[1] for b in boot]),
                  "inflation_per_pp": summary(coef[2], [b[2] for b in boot])}
    haven_verdict = "supported" if haven_main["debt_per_pp"]["excludes_zero"] and coef[1] > 0 else "not supported"

    # 2. haven, by era
    eras = []
    for start, end in ERAS:
        rows = [r for r in panic if start <= r[0] <= end]
        fails = [1.0 if r[1] > 0 else 0.0 for r in rows]
        moves = [r[1] for r in rows]
        eras.append({"era": f"{start[:4]}-{end[:4]}", "n": len(rows),
                     "share_yield_up": summary(statistics.fmean(fails), stats.boot_means(fails, DRAWS, rng)),
                     "mean_d10y_bp": summary(statistics.fmean(moves), stats.boot_means(moves, DRAWS, rng)),
                     "federal_debt_pct_gdp_mean": round(statistics.fmean(r[2] for r in rows), 1)})

    # 3. repo, secondary: next panel day after a panic day
    prows = ev.read_panel(ROOT / "data" / "panel.csv")
    labels, excluded = ev.classify(prows, ev.fomc_decision_dates(ROOT / "data" / "fomc_calendar.json"))
    pdates = [r["date"] for r in prows]
    spread = {r["date"]: (r["sofr"] - r["iorb"]) * 100 for r in prows if r["sofr"] is not None}
    panic_by_date = {r[0]: r[1] for r in panic}
    after = {"yield_up": [], "yield_down": []}
    for prev, t in zip(pdates, pdates[1:]):
        if prev in panic_by_date and not labels[t] and t not in excluded and prev in spread and t in spread:
            key = "yield_up" if panic_by_date[prev] > 0 else "yield_down"
            after[key].append((t, spread[t] - spread[prev]))
    up, down = [x[1] for x in after["yield_up"]], [x[1] for x in after["yield_down"]]
    repo = {"n_yield_up": len(up), "n_yield_down": len(down),
            "dates_yield_up": [x[0] for x in after["yield_up"]], "dates_yield_down": [x[0] for x in after["yield_down"]]}
    if len(up) >= 2 and len(down) >= 2:
        repo["difference_bp"] = summary(statistics.fmean(up) - statistics.fmean(down),
                                        [a - b for a, b in zip(stats.boot_means(up, DRAWS, rng),
                                                               stats.boot_means(down, DRAWS, rng))])

    # 4. household debt: levels, and mortgage-Treasury spread in panic weeks
    levels = {"household_pct_gdp": {}, "federal_pct_gdp": {}}
    for name, s in (("household_pct_gdp", household), ("federal_pct_gdp", federal)):
        latest = max(s)
        peak = max(s, key=s.get)
        levels[name] = {**{m: round(s[m], 1) for m in SNAPSHOTS}, "latest": {"month": latest, "value": round(s[latest], 1)},
                        "peak": {"month": peak, "value": round(s[peak], 1)}}
    mort = fred("MORTGAGE30US")
    surveys = sorted(d for d in mort if d >= "1990-01-01" and d in d10)
    panic_days = sorted(panic_by_date)
    hh_mean_rows = []
    for prev, d in zip(surveys, surveys[1:]):
        hh = as_of(household, d, 3)
        if hh is None:
            continue
        sp_prev, sp = (mort[prev] - d10[prev]) * 100, (mort[d] - d10[d]) * 100
        is_panic = 1.0 if any(prev < p <= d for p in panic_days) else 0.0
        hh_mean_rows.append((d, sp - sp_prev, is_panic, hh))
    hh_mean = statistics.fmean(r[3] for r in hh_mean_rows)
    weekly = [(d, y, p, p * (hh - hh_mean)) for d, y, p, hh in hh_mean_rows]

    def mfit(rows):
        return ols([(r[2], r[3]) for r in rows], [r[1] for r in rows])

    mortgage = {}
    for label, rows in (("all_weeks", weekly),
                        ("without_2007_2009", [r for r in weekly if not "2007" <= r[0][:4] <= "2009"])):
        c = mfit(rows)
        b = block_boot(rows, mfit, rng)
        mortgage[label] = {"n_weeks": len(rows), "n_panic_weeks": int(sum(r[2] for r in rows)),
                           "panic_bp": summary(c[1], [x[1] for x in b]),
                           "panic_x_household_debt_bp_per_pp": summary(c[2], [x[2] for x in b])}
    mortgage["household_debt_mean_pct_gdp"] = round(hh_mean, 2)
    hh_verdict = ("supported" if mortgage["all_weeks"]["panic_x_household_debt_bp_per_pp"]["excludes_zero"]
                  and mortgage["all_weeks"]["panic_x_household_debt_bp_per_pp"]["estimate"] > 0 else "not supported")

    result = {"design": "docs/design-study-09-debt-volatility.md", "manifest": "metadata/s09_manifest.json",
              "panel_sha256": hashlib.sha256((ROOT / "data" / "panel.csv").read_bytes()).hexdigest(),
              "seed": SEED, "panic_rule": f"VIX close >= {1 + PANIC_RISE:.2f} x previous close, from 1990",
              "haven_verdict": haven_verdict, "haven_main": haven_main, "haven_by_era": eras,
              "repo_after_panic": repo, "debt_levels": levels, "household_mortgage_verdict": hh_verdict,
              "mortgage_spread_in_panic_weeks": mortgage,
              "panic_days_2020_on": [{"date": r[0], "d10y_bp": round(r[1], 1)} for r in panic if r[0] >= "2020"]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "panic_days_2020_on"}, indent=1))


if __name__ == "__main__":
    main()
