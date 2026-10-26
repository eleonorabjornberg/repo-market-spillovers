"""Fetch DTCC's public CFTC cumulative rates files, keep the trades study 05 needs, and record each file.

For each weekday from START to the last available day, downloads the day's zip, keeps new spot-starting USD SOFR OIS
trades of 1.9-2.1 or 9.5-10.5 years' tenor (not packages), appends them to data/raw/dtcc/sofr_ois_trades.csv, records
the zip's SHA-256 in metadata/dtcc_manifest.json, and deletes the zip. Days already in the manifest are skipped, so the
script can be re-run to extend the series. DTCC keeps a rolling window of files; older days return 403.
"""
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
START = dt.date(2024, 11, 1)
URL = "https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_{d:%Y_%m_%d}.zip"
FIELDS = ["file_date", "execution", "effective", "expiration", "tenor_years", "fixed_rate", "notional"]
TENORS = ((1.9, 2.1), (9.5, 10.5))


def number(text):
    digits = "".join(c for c in text if c.isdigit() or c == ".")
    return float(digits) if digits else None


def keep(r):
    """The filtered trade as a dict, or None."""
    if r["UPI FISN"] != "NA/Swap OIS USD" or "SOFR" not in r["UPI Underlier Name"].upper():
        return None
    if r["Action type"] != "NEWT" or r["Event type"] != "TRAD" or r["Package indicator"].lower() != "false":
        return None
    rate = r["Fixed rate-Leg 1"] or r["Fixed rate-Leg 2"]
    if not rate or not r["Effective Date"] or not r["Expiration Date"] or not r["Execution Timestamp"]:
        return None
    execution = dt.date.fromisoformat(r["Execution Timestamp"][:10])
    effective = dt.date.fromisoformat(r["Effective Date"][:10])
    expiration = dt.date.fromisoformat(r["Expiration Date"][:10])
    if not 0 <= (effective - execution).days <= 5:
        return None
    tenor = (expiration - effective).days / 365.25
    if not any(lo <= tenor <= hi for lo, hi in TENORS):
        return None
    notional = number(r["Notional amount-Leg 1"] or r["Notional amount-Leg 2"])
    if not notional:
        return None
    return {"execution": execution.isoformat(), "effective": effective.isoformat(),
            "expiration": expiration.isoformat(), "tenor_years": round(tenor, 3), "fixed_rate": float(rate),
            "notional": notional}


def main():
    out_dir = ROOT / "data" / "raw" / "dtcc"
    out_dir.mkdir(parents=True, exist_ok=True)
    trades_path = out_dir / "sofr_ois_trades.csv"
    manifest_path = ROOT / "metadata" / "dtcc_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    new_file = not trades_path.exists()
    with open(trades_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        day = START
        while day <= dt.date.today():
            key = day.isoformat()
            if day.weekday() < 5 and key not in manifest:
                try:
                    with urllib.request.urlopen(URL.format(d=day), timeout=120) as response:
                        body = response.read()
                except urllib.error.HTTPError as e:
                    if e.code not in (403, 404):  # anything else may be transient: stop, and resume on re-run
                        raise
                    manifest[key] = {"status": e.code}
                    day += dt.timedelta(days=1)
                    continue
                z = zipfile.ZipFile(io.BytesIO(body))
                kept = 0
                with z.open(z.namelist()[0]) as member:
                    for r in csv.DictReader(io.TextIOWrapper(member, "utf-8")):
                        t = keep(r)
                        if t:
                            writer.writerow({"file_date": key, **t})
                            kept += 1
                manifest[key] = {"url": URL.format(d=day), "sha256": hashlib.sha256(body).hexdigest(),
                                 "kept_trades": kept,
                                 "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
                f.flush()
                manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
                print(key, kept, flush=True)
            day += dt.timedelta(days=1)
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
