"""Study 11: count new USD SOFR OIS swap trades by day, tenor bucket and package flag, from DTCC's public reports.

Writes data/raw/dtcc/packages_daily.csv (resumable: days already there are skipped). Only counts and notionals are
kept; the trade-level files are not stored.
"""
import csv
import datetime as dt
import io
import pathlib
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_dtcc import START, URL, number  # noqa: E402

BUCKETS = ((2.0, 5.0, "2-5y"), (5.0, 12.0, "5-12y"), (12.0, 31.0, "12-31y"))
FIELDS = ["date", "bucket", "package", "trades", "notional"]


def classify(r):
    """(bucket, package) for a qualifying trade, else None."""
    if r["UPI FISN"] != "NA/Swap OIS USD" or "SOFR" not in r["UPI Underlier Name"].upper():
        return None
    if r["Action type"] != "NEWT" or r["Event type"] != "TRAD":
        return None
    if not (r["Effective Date"] and r["Expiration Date"] and r["Execution Timestamp"]):
        return None
    execution = dt.date.fromisoformat(r["Execution Timestamp"][:10])
    effective = dt.date.fromisoformat(r["Effective Date"][:10])
    if not 0 <= (effective - execution).days <= 5:
        return None
    tenor = (dt.date.fromisoformat(r["Expiration Date"][:10]) - effective).days / 365.25
    bucket = next((name for lo, hi, name in BUCKETS if lo <= tenor < hi), None)
    package = r["Package indicator"].lower()
    if bucket is None or package not in ("true", "false"):
        return None
    return bucket, package == "true"


def main():
    path = ROOT / "data" / "raw" / "dtcc" / "packages_daily.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if path.exists():
        with open(path, newline="") as f:
            done = {r["date"] for r in csv.DictReader(f)}
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        day = START
        while day < dt.date.today():
            key = day.isoformat()
            if day.weekday() < 5 and key not in done:
                try:
                    with urllib.request.urlopen(URL.format(d=day), timeout=120) as response:
                        body = response.read()
                except urllib.error.HTTPError as e:
                    if e.code not in (403, 404):
                        raise
                    body = None
                agg = {}
                if body:
                    z = zipfile.ZipFile(io.BytesIO(body))
                    with z.open(z.namelist()[0]) as member:
                        for r in csv.DictReader(io.TextIOWrapper(member, "utf-8")):
                            c = classify(r)
                            n = number(r["Notional amount-Leg 1"] or r["Notional amount-Leg 2"]) if c else None
                            if c and n:
                                t, notional = agg.get(c, (0, 0.0))
                                agg[c] = (t + 1, notional + n)
                for (bucket, package), (t, notional) in sorted(agg.items()):
                    w.writerow({"date": key, "bucket": bucket, "package": int(package), "trades": t,
                                "notional": round(notional)})
                if not agg:  # holiday or no file: a marker row so the day is not fetched again
                    w.writerow({"date": key, "bucket": "", "package": "", "trades": 0, "notional": 0})
                f.flush()
                print(key, sum(t for t, _ in agg.values()), flush=True)
            day += dt.timedelta(days=1)


if __name__ == "__main__":
    main()
