"""Fetch study 02's long-history series into data/raw/long/ and record them in metadata/long_manifest.json.

FRED series are fetched in full; the OFR financial stress index and one OFR Hedge Fund Monitor series come from OFR.
Raw files are not committed; the manifest records retrieval time and SHA-256.
"""
import datetime as dt
import hashlib
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spillovers.history import INDICATORS  # noqa: E402

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
OFR_FSI = "https://www.financialresearch.gov/financial-stress-index/data/fsi.csv"
OFR_HF = "https://data.financialresearch.gov/hf/v1/series/timeseries?mnemonic={id}"
EXTRA = ["NFCI"]  # the stress definition, weekly


def sources():
    ids = set(EXTRA)
    for spec in INDICATORS.values():
        ids |= {spec[k] for k in ("num", "den", "minus") if k in spec}
    return sorted(ids)


def url_and_file(source):
    if source.startswith("OFR:"):
        return OFR_FSI, "OFR_FSI.csv"
    if source.startswith("OFRHF:"):
        mnemonic = source.split(":", 1)[1]
        return OFR_HF.format(id=mnemonic), f"OFRHF_{mnemonic}.json"
    return FRED.format(id=source), f"{source}.csv"


def main():
    raw = ROOT / "data" / "raw" / "long"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for source in sources():
        url, name = url_and_file(source)
        if name in manifest:
            continue
        with urllib.request.urlopen(url, timeout=120) as response:
            body = response.read()
        (raw / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        print(name, len(body))
    (ROOT / "metadata" / "long_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
