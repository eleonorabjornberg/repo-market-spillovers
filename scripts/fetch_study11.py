"""Fetch study 11's OFR Hedge Fund Monitor series and TIC's Table 5 into data/raw/s11/, with metadata/s11_manifest.json."""
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
STRATEGIES = ("RV", "MACRO", "MULTI", "CREDIT", "EQUITY", "EVENT", "OTHER")
OFR = (["FPF-BORROW_REPO_SUM", "FPF-ASSETCLASS_LTREASURY_SUM", "FPF-ASSETCLASS_STREASURY_SUM",
        "FPF-ASSETCLASS_IRD_GNE_SUM", "FPF-ASSETCLASS_IRD_LGNE_SUM", "FPF-ASSETCLASS_IRD_SGNE_SUM"]
       + [f"FPF-STRATEGY_{s}_BORROWING_SUM" for s in STRATEGIES]
       + [f"FPF-STRATEGY_{s}_GNE_SUM" for s in STRATEGIES])
TIC = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt"


def main():
    raw = ROOT / "data" / "raw" / "s11"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = {}
    targets = [(f"{m}.json", f"https://data.financialresearch.gov/hf/v1/series/timeseries?mnemonic={m}") for m in OFR]
    targets.append(("TIC_slt_table5.txt", TIC))
    for name, url in targets:
        with urllib.request.urlopen(url, timeout=120) as response:
            body = response.read()
        (raw / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s11_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(len(manifest), "files")


if __name__ == "__main__":
    main()
