"""Study 16: daily long-dated and 10-year USD SOFR swap volume from DTCC's public cumulative rates files.

Design: docs/design-study-16-data-centre-debt.md. For each weekday from 1 November 2024, downloads the day's zip, sums
new spot-starting, non-package USD SOFR OIS trades executed that day into two tenor buckets, appends one row to
data/raw/s16/dtcc_daily.csv, records the zip's SHA-256 in metadata/s16_dtcc_manifest.json and discards the zip.
Days already in the manifest are skipped, so it resumes where it stopped.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_dtcc  # noqa: E402

START = dt.date(2024, 11, 1)
BUCKETS = {"long": (19.5, 100.0), "ten": (9.5, 10.5)}
FIELDS = ["date", "long_notional", "long_trades", "ten_notional", "ten_trades"]


def bucket(r, day):
    """The trade's bucket and notional, or None (same filter as fetch_dtcc.keep, other tenors)."""
    if r["UPI FISN"] != "NA/Swap OIS USD" or "SOFR" not in r["UPI Underlier Name"].upper():
        return None
    if r["Action type"] != "NEWT" or r["Event type"] != "TRAD" or r["Package indicator"].lower() != "false":
        return None
    if not r["Effective Date"] or not r["Expiration Date"] or not r["Execution Timestamp"]:
        return None
    if r["Execution Timestamp"][:10] != day.isoformat():
        return None
    effective = dt.date.fromisoformat(r["Effective Date"][:10])
    expiration = dt.date.fromisoformat(r["Expiration Date"][:10])
    if not 0 <= (effective - day).days <= 5:
        return None
    tenor = (expiration - effective).days / 365.25
    notional = fetch_dtcc.number(r["Notional amount-Leg 1"] or r["Notional amount-Leg 2"])
    if not notional:
        return None
    for name, (lo, hi) in BUCKETS.items():
        if lo <= tenor <= hi:
            return name, notional
    return None


def main():
    out = ROOT / "data" / "raw" / "s16"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "dtcc_daily.csv"
    manifest_path = ROOT / "metadata" / "s16_dtcc_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        day = START
        while day < dt.date.today():
            key = day.isoformat()
            if day.weekday() < 5 and key not in manifest:
                try:
                    with urllib.request.urlopen(fetch_dtcc.URL.format(d=day), timeout=300) as response:
                        body = response.read()
                except urllib.error.HTTPError as e:
                    if e.code not in (403, 404):
                        raise
                    manifest[key] = {"status": e.code}
                else:
                    sums = {"long_notional": 0.0, "long_trades": 0, "ten_notional": 0.0, "ten_trades": 0}
                    z = zipfile.ZipFile(io.BytesIO(body))
                    with z.open(z.namelist()[0]) as member:
                        for r in csv.DictReader(io.TextIOWrapper(member, "utf-8")):
                            b = bucket(r, day)
                            if b:
                                sums[f"{b[0]}_notional"] += b[1]
                                sums[f"{b[0]}_trades"] += 1
                    w.writerow({"date": key, **sums})
                    f.flush()
                    manifest[key] = {"sha256": hashlib.sha256(body).hexdigest(),
                                     "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
                manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
                print(key, manifest[key].get("status", "ok"), flush=True)
            day += dt.timedelta(days=1)


if __name__ == "__main__":
    main()
