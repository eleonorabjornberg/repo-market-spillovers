"""Fetch the wider-market series from FRED into data/raw/ and record them in metadata/fred_manifest.json.

The raw files are not committed (FRED's terms, and FRED serves only the latest vintage, so a re-fetch need not
reproduce them). The manifest records when each was retrieved and its SHA-256, so a result can be traced to the
bytes it read.
"""
import datetime as dt
import hashlib
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from spillovers.outcomes import FRED_SERIES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2017-01-01"


def main():
    raw = ROOT / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for series in sorted(FRED_SERIES):
        url = URL.format(series=series)
        with urllib.request.urlopen(url, timeout=120) as response:
            body = response.read()
        (raw / f"{series}.csv").write_bytes(body)
        lines = body.decode().strip().splitlines()
        manifest[series] = {
            "url": url,
            "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "sha256": hashlib.sha256(body).hexdigest(),
            "first_date": lines[1].split(",")[0],
            "last_date": lines[-1].split(",")[0],
        }
        print(series, manifest[series]["first_date"], "..", manifest[series]["last_date"])
    (ROOT / "metadata" / "fred_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
