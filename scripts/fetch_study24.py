"""Study 24: aggregate DTCC's public SOFR swap reports by package structure, and fetch the OFR and FRED series.

For each weekday from 1 November 2024, downloads DTCC's CFTC cumulative rates file, keeps new spot-starting USD SOFR
OIS trades of 1.5 to 31 years' tenor, classifies each (`classify_day`), and appends one row per day, category and tenor
bucket to data/raw/s24/daily.csv. The median fixed rate of outright 9.5-10.5 year trades goes to daily_rates.csv. Only
aggregates are kept; each zip's SHA-256 is recorded in metadata/s24_manifest.json and the zip is discarded. Days already
in the manifest are skipped, so the script can be re-run to extend the series. The design is
docs/design-study-24-swap-spread-visibility.md.
"""
import collections
import concurrent.futures
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import statistics
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "s24"
MANIFEST = ROOT / "metadata" / "s24_manifest.json"
START = dt.date(2024, 11, 1)
DTCC = "https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_{d:%Y_%m_%d}.zip"
OFR = ("FPF-ASSETCLASS_IRD_GNE_SUM", "FPF-ASSETCLASS_IRD_LGNE_SUM", "FPF-ASSETCLASS_IRD_SGNE_SUM",
       "TFF-LF_TREAS_NET_DV01")
OFR_URL = "https://data.financialresearch.gov/hf/v1/series/timeseries?mnemonic={m}"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=2024-10-01"
BUCKETS = ((1.5, 4.0, "1.5-4y"), (4.0, 8.0, "4-8y"), (8.0, 15.0, "8-15y"), (15.0, 31.0, "15-31y"))
CATEGORIES = ("single_spread", "curve_spread", "package_no_spread", "outright")
DAILY_FIELDS = ["date", "category", "bucket", "trades", "notional_musd", "dv01_musd", "capped_trades", "capped_dv01_musd"]
RATE_FIELDS = ["date", "trades", "median_fixed_rate"]
DEFAULT_RATE = 0.04


def notional(text):
    """(USD amount, capped) from a field such as '25,000,000' or '650,000,000+'; (None, False) if empty."""
    text = text.strip()
    digits = "".join(c for c in text if c.isdigit() or c == ".")
    if not digits:
        return None, False
    return float(digits), text.endswith("+")


def annuity(rate, years):
    """Present value of 1 a year for `years` at annual `rate`: the swap's DV01 per unit notional, divided by 1 bp."""
    if abs(rate) < 1e-9:
        return years
    return (1 - (1 + rate) ** -years) / rate


def fixed_rate(r):
    """The trade's fixed rate as a decimal; None if absent or outside -5% to 20% (a malformed field)."""
    for field in ("Fixed rate-Leg 1", "Fixed rate-Leg 2"):
        try:
            rate = float(r[field])
        except (ValueError, KeyError):
            continue
        return rate if -0.05 <= rate <= 0.20 else None
    return None


def eligible(r):
    """(tenor in years, bucket) for a trade in the design's sample, else None."""
    if r["UPI FISN"] != "NA/Swap OIS USD" or "SOFR" not in r["UPI Underlier Name"].upper():
        return None
    if r["Action type"] != "NEWT" or r["Event type"] != "TRAD" or r["Notional currency-Leg 1"] != "USD":
        return None
    try:
        execution = dt.date.fromisoformat(r["Execution Timestamp"][:10])
        effective = dt.date.fromisoformat(r["Effective Date"][:10])
        expiration = dt.date.fromisoformat(r["Expiration Date"][:10])
    except ValueError:
        return None
    if not 0 <= (effective - execution).days <= 5:
        return None
    tenor = (expiration - effective).days / 365.25
    bucket = next((name for lo, hi, name in BUCKETS if lo <= tenor < hi), None)
    return None if bucket is None else (tenor, bucket)


def classify_day(rows):
    """Aggregate one day's rows: {(category, bucket): totals} and the outright 10-year fixed rates.

    A package trade with a package spread is grouped with the others sharing its execution second, platform and
    spread; a group of one swap is `single_spread`, of two or more `curve_spread`. Package trades without a spread are
    `package_no_spread`; the rest `outright`.
    """
    kept = []
    for r in rows:
        e = eligible(r)
        if e is None:
            continue
        amount, capped = notional(r["Notional amount-Leg 1"])
        if amount is None:
            continue
        tenor, bucket = e
        rate = fixed_rate(r)
        dv01 = amount * annuity(DEFAULT_RATE if rate is None else rate, tenor) * 1e-4 / 1e6
        package = r["Package indicator"].strip().upper() == "TRUE"
        spread = r["Package transaction spread"].strip()
        key = (r["Execution Timestamp"][:19], r["Platform identifier"], spread) if package and spread else None
        kept.append((key, package, bucket, tenor, rate, amount, capped, dv01))
    sizes = collections.Counter(k[0] for k in kept if k[0] is not None)
    totals = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0.0])
    tens = []
    for key, package, bucket, tenor, rate, amount, capped, dv01 in kept:
        if key is not None:
            category = "single_spread" if sizes[key] == 1 else "curve_spread"
        elif package:
            category = "package_no_spread"
        else:
            category = "outright"
            if 9.5 <= tenor <= 10.5 and rate is not None:
                tens.append(rate)
        t = totals[(category, bucket)]
        t[0] += 1
        t[1] += amount / 1e6
        t[2] += dv01
        if capped:
            t[3] += 1
            t[4] += dv01
    return totals, tens


def fetch_day(day):
    try:
        with urllib.request.urlopen(DTCC.format(d=day), timeout=180) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        return day, None, f"HTTP {error.code}"
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        name = z.namelist()[0]
        text = z.read(name).decode("utf-8", errors="replace")
    totals, tens = classify_day(csv.DictReader(io.StringIO(text)))
    return day, {"sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body), "totals": totals, "tens": tens}, None


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read()


def main(end=None):
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"dtcc": {}, "series": {}}
    end = end or dt.date.today()
    days = [START + dt.timedelta(n) for n in range((end - START).days)]
    todo = [d for d in days if d.weekday() < 5 and d.isoformat() not in manifest["dtcc"]]
    daily_path, rates_path = RAW / "daily.csv", RAW / "daily_rates.csv"
    new_daily, new_rates = not daily_path.exists(), not rates_path.exists()
    with open(daily_path, "a", newline="") as fd, open(rates_path, "a", newline="") as fr, \
            concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        wd, wr = csv.DictWriter(fd, DAILY_FIELDS), csv.DictWriter(fr, RATE_FIELDS)
        if new_daily:
            wd.writeheader()
        if new_rates:
            wr.writeheader()
        for n, (day, result, error) in enumerate(pool.map(fetch_day, todo), 1):
            key = day.isoformat()
            if result is None:
                print(f"{key}: {error}", flush=True)
                continue
            for (category, bucket), t in sorted(result["totals"].items()):
                wd.writerow({"date": key, "category": category, "bucket": bucket, "trades": t[0],
                             "notional_musd": round(t[1], 3), "dv01_musd": round(t[2], 6), "capped_trades": t[3],
                             "capped_dv01_musd": round(t[4], 6)})
            if result["tens"]:
                wr.writerow({"date": key, "trades": len(result["tens"]),
                             "median_fixed_rate": statistics.median(result["tens"])})
            manifest["dtcc"][key] = {"url": DTCC.format(d=day), "sha256": result["sha256"], "bytes": result["bytes"]}
            fd.flush()
            fr.flush()
            if n % 20 == 0:
                MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
                print(f"{n}/{len(todo)} through {key}", flush=True)
    retrieved = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for m in OFR:
        body = fetch_json(OFR_URL.format(m=m))
        (RAW / f"{m}.json").write_bytes(body)
        manifest["series"][m] = {"url": OFR_URL.format(m=m), "sha256": hashlib.sha256(body).hexdigest(),
                                 "retrieved": retrieved}
    body = fetch_json(FRED_URL)
    (RAW / "DGS10.csv").write_bytes(body)
    manifest["series"]["DGS10"] = {"url": FRED_URL, "sha256": hashlib.sha256(body).hexdigest(), "retrieved": retrieved}
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main(dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None)
