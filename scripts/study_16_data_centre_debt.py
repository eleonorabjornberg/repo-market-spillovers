"""Study 16: data-centre debt, and whether it reaches the swap market.

Design: docs/design-study-16-data-centre-debt.md (committed before any data was fetched).
Run scripts/fetch_study16_dtcc.py first. This script fetches the SEC data into data/raw/s16/ (the contact the SEC
asks for is read from the SEC_USER_AGENT environment variable), records it in metadata/s16_manifest.json, and writes
results/study-16/result.json.
"""
import csv
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import random
import statistics
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spillovers import stats  # noqa: E402

RAW = ROOT / "data" / "raw" / "s16"
OUT = ROOT / "results" / "study-16"
COMPANIES = {"Alphabet": "0001652044", "Amazon": "0001018724", "Meta": "0001326801", "Microsoft": "0000789019",
             "Oracle": "0001341439", "CoreWeave": "0001769628"}
DEBT = (("LongTermDebt",), ("LongTermDebtNoncurrent", "LongTermDebtCurrent"), ("DebtInstrumentCarryingAmount",))
CAPEX = ("PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets")
LEASES = ("FinanceLeaseLiability",)
MATURITY = ("LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths",
            "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo",
            "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree",
            "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour",
            "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive",
            "LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive")
SEED, DRAWS = 20261027, 2000
FILINGS_FROM = "2024-10-01"


def fetch():
    agent = os.environ.get("SEC_USER_AGENT")
    if not agent:
        raise SystemExit("set SEC_USER_AGENT to a contact name and email, as the SEC asks")
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, cik in COMPANIES.items():
        for kind, url in (("facts", f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"),
                          ("submissions", f"https://data.sec.gov/submissions/CIK{cik}.json")):
            req = urllib.request.Request(url, headers={"User-Agent": agent})
            with urllib.request.urlopen(req, timeout=120) as response:
                body = response.read()
            (RAW / f"{name}_{kind}.json").write_bytes(body)
            manifest[f"{name}_{kind}.json"] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                                               "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        # the submissions file holds the latest 1,000 filings; older pages are fetched while they reach the window
        for page in json.loads((RAW / f"{name}_submissions.json").read_text())["filings"].get("files", []):
            if page["filingTo"] < FILINGS_FROM:
                continue
            url = f"https://data.sec.gov/submissions/{page['name']}"
            req = urllib.request.Request(url, headers={"User-Agent": agent})
            with urllib.request.urlopen(req, timeout=120) as response:
                body = response.read()
            fname = f"{name}_submissions-{page['name'].removesuffix('.json').split('-')[-1]}.json"
            (RAW / fname).write_bytes(body)
            manifest[fname] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                               "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s16_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def annual(facts, concept):
    """Fiscal year (the calendar year its period ends in) -> USD value, from 10-K filings; the latest filing wins.
    Flow values must cover a full year; balance-sheet values are at the fiscal year's end."""
    units = facts.get("facts", {}).get("us-gaap", {}).get(concept, {}).get("units", {}).get("USD", [])
    out, filed = {}, {}
    for u in units:
        if u.get("form") != "10-K":
            continue
        if "start" in u and (dt.date.fromisoformat(u["end"]) - dt.date.fromisoformat(u["start"])).days < 300:
            continue
        year = int(u["end"][:4])
        if year not in filed or u["filed"] >= filed[year]:
            out[year], filed[year] = u["val"], u["filed"]
    return out


def first_available(facts, options):
    """The first option whose concepts all have annual values; summed over its concepts, year by year."""
    for concepts in options:
        series = [annual(facts, c) for c in concepts]
        if all(series):
            years = set.intersection(*(set(s) for s in series))
            return "+".join(concepts), {y: sum(s[y] for s in series) for y in years}
    return None, {}


def size():
    out, totals = {}, {}
    for name in COMPANIES:
        facts = json.loads((RAW / f"{name}_facts.json").read_text())
        debt_c, debt = first_available(facts, DEBT)
        capex_c, capex = first_available(facts, [(c,) for c in CAPEX])
        _, leases = first_available(facts, [LEASES])
        mats = [annual(facts, c) for c in MATURITY]
        latest = max(debt) if debt else None
        mat_year = max(set.intersection(*(set(m) for m in mats))) if all(mats) else None
        out[name] = {"debt_concept": debt_c, "capex_concept": capex_c,
                     "debt_bn": {str(y): round(v / 1e9, 1) for y, v in sorted(debt.items()) if y >= 2019},
                     "capex_bn": {str(y): round(v / 1e9, 1) for y, v in sorted(capex.items()) if y >= 2019},
                     "finance_leases_bn": {str(y): round(v / 1e9, 1) for y, v in sorted(leases.items()) if y >= 2019},
                     "share_due_after_5y_pct": (round(mats[-1][mat_year] / sum(m[mat_year] for m in mats) * 100, 1)
                                                if mat_year else None),
                     "maturity_year": mat_year, "latest_fiscal_year": latest}
        for kind, s in (("debt", debt), ("capex", capex)):
            for y, v in s.items():
                totals.setdefault(kind, {}).setdefault(y, {})[name] = v
    together = {}
    for kind in ("debt", "capex"):
        full = {y: v for y, v in totals.get(kind, {}).items() if len(v) == len([n for n in COMPANIES if n != "CoreWeave"])
                or len(v) == len(COMPANIES)}
        together[kind] = {str(y): round(sum(v.values()) / 1e9, 1) for y, v in sorted(full.items()) if y >= 2019}
    return out, together


def business_days(start, end):
    d, out = start, []
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def shift(day, n):
    """The business day n business days from day (weekends only; holidays are not modelled)."""
    step = 1 if n > 0 else -1
    while n:
        day += dt.timedelta(days=step)
        if day.weekday() < 5:
            n -= step
    return day


def deal_days(filings):
    """filings: [(company, form, date)]. Pricing days per the design, merged across companies within 5 business days."""
    fwp = {}
    for c, form, d in filings:
        if form == "FWP":
            fwp.setdefault(c, []).append(d)
    days = [d for c, form, d in filings if form == "FWP"]
    for c, form, d in filings:
        if form == "424B2" and not any(shift(d, -3) <= x <= d for x in fwp.get(c, [])):
            days.append(shift(d, -1))
    merged = []
    for d in sorted(set(days)):
        if not merged or d > shift(merged[-1], 5):
            merged.append(d)
    return merged


def ols(rows, k):
    """Least squares by the normal equations; rows are (y, x list of length k)."""
    a = [[0.0] * k for _ in range(k)]
    b = [0.0] * k
    for y, x in rows:
        for i in range(k):
            b[i] += x[i] * y
            for j in range(k):
                a[i][j] += x[i] * x[j]
    for i in range(k):  # Gaussian elimination with partial pivoting
        p = max(range(i, k), key=lambda r: abs(a[r][i]))
        a[i], a[p], b[i], b[p] = a[p], a[i], b[p], b[i]
        if abs(a[i][i]) < 1e-12:
            return None
        for r in range(i + 1, k):
            f = a[r][i] / a[i][i]
            b[r] -= f * b[i]
            for c in range(i, k):
                a[r][c] -= f * a[i][c]
    beta = [0.0] * k
    for i in reversed(range(k)):
        beta[i] = (b[i] - sum(a[i][j] * beta[j] for j in range(i + 1, k))) / a[i][i]
    return beta


def event_coefficient(obs):
    """Coefficient on the event indicator in log(value) ~ event + block dummies + weekday dummies.
    obs: (block, weekday, value, is_event); a block is a calendar month (or a drawn month in the bootstrap)."""
    blocks = sorted({o[0] for o in obs})
    rows = [(math.log(v), [1.0 if e else 0.0] + [1.0 if blk == m else 0.0 for m in blocks]
             + [1.0 if wd == w else 0.0 for w in range(1, 5)]) for blk, wd, v, e in obs]
    beta = ols(rows, 1 + len(blocks) + 4)
    return beta[0] if beta else None


def swap_test(filings):
    with open(RAW / "dtcc_daily.csv", newline="") as f:
        daily = {r["date"]: r for r in csv.DictReader(f)}
    series = {"long": {d: float(r["long_notional"]) for d, r in daily.items()},
              "ten": {d: float(r["ten_notional"]) for d, r in daily.items()},
              "long_trades": {d: float(r["long_trades"]) for d, r in daily.items()}}
    days = sorted(d for d in daily if all(series[k][d] > 0 for k in series))
    deals = deal_days(filings)
    events = {x.isoformat() for d in deals for x in (d, shift(d, 1))} & set(days)
    in_window = [d for d in deals if d.isoformat() in days or shift(d, 1).isoformat() in days]

    def obs(k, labelled):
        return [(blk, dt.date.fromisoformat(d).weekday(), series[k][d], d in events) for blk, d in labelled]

    labelled = [(d[:7], d) for d in days]
    point = {k: event_coefficient(obs(k, labelled)) for k in series}
    point["long_minus_ten"] = point["long"] - point["ten"]
    rng = random.Random(SEED)
    by_month = {}
    for d in days:
        by_month.setdefault(d[:7], []).append(d)
    months = sorted(by_month)
    draws = {k: [] for k in point}
    for _ in range(DRAWS):
        sample = [(i, d) for i, m in enumerate(rng.choices(months, k=len(months))) for d in by_month[m]]
        if not any(d in events for _, d in sample):
            continue
        got = {k: event_coefficient(obs(k, sample)) for k in series}
        if any(v is None for v in got.values()):
            continue
        for k, v in got.items():
            draws[k].append(v)
        draws["long_minus_ten"].append(got["long"] - got["ten"])
    out = {"n_days": len(days), "days": [days[0], days[-1]], "n_deals": len(deals),
           "n_deals_in_window": len(in_window), "n_event_days": len(events), "n_draws_used": len(draws["long"]),
           "deal_days": [d.isoformat() for d in deals]}
    for k, v in point.items():
        lo, hi = stats.interval(draws[k])
        out[k] = {"coef_log": round(v, 4), "pct": round((math.exp(v) - 1) * 100, 1),
                  "ci95_pct": [round((math.exp(lo) - 1) * 100, 1), round((math.exp(hi) - 1) * 100, 1)],
                  "lower_above_zero": lo > 0}
    out["heavier_around_deals"] = out["long"]["lower_above_zero"]
    out["specific_to_long_tenors"] = out["long_minus_ten"]["lower_above_zero"]
    return out


def filings():
    out = set()
    for name in COMPANIES:
        pages = [json.loads((RAW / f"{name}_submissions.json").read_text())["filings"]["recent"]]
        pages += [json.loads(f.read_text()) for f in sorted(RAW.glob(f"{name}_submissions-*.json"))]
        for page in pages:
            for form, date in zip(page["form"], page["filingDate"]):
                if form in ("FWP", "424B2") and date >= FILINGS_FROM:
                    out.add((name, form, dt.date.fromisoformat(date)))
    return sorted(out)


def main():
    if "--no-fetch" not in sys.argv:
        fetch()
    companies, together = size()
    deals = filings()
    result = {"design": "docs/design-study-16-data-centre-debt.md", "manifest": "metadata/s16_manifest.json",
              "seed": SEED, "draws": DRAWS, "Q1_size": {"companies": companies, "together_bn": together},
              "Q2_swaps": swap_test(deals),
              "Q3_share_due_after_5y_pct": {n: c["share_due_after_5y_pct"] for n, c in companies.items()},
              "filings_by_company": {n: sum(1 for c, _, _ in deals if c == n) for n in COMPANIES}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
