"""Fetch study 09's series (full histories from FRED) into data/raw/s09/ with metadata/s09_manifest.json."""
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERIES = ["VIXCLS", "DGS10", "CPIAUCSL", "FYGFDPUN", "GDP", "CMDEBT", "MORTGAGE30US"]


def main():
    raw = ROOT / "data" / "raw" / "s09"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for s in SERIES:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
        with urllib.request.urlopen(url, timeout=120) as response:
            body = response.read()
        (raw / f"{s}.csv").write_bytes(body)
        manifest[f"{s}.csv"] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                                "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        print(s, len(body))
    (ROOT / "metadata" / "s09_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
