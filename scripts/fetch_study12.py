"""Fetch study 12's series into data/raw/s12/ with metadata/s12_manifest.json (FRED
OFR Form PF aggregates)."""
import datetime as dt
import hashlib
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRED = ["VIXCLS", "NASDAQCOM", "DGS10", "CRDQUSAPABIS", "GDP", "BOGZ1FL664090005Q", "T10Y3M", "BAA10Y", "NFCI"]
OFR = ["FPF-BORROW_REPO_GAVN10_PERCENT", "FPF-ALLQHF_GAVN10_LEVERAGERATIO_AVERAGE",
       "FPF-STRATEGY_RV_LEVERAGERATIO_GAVWMEAN", "FPF-ALLQHF_FINANCINGLIQUIDTYLE1_PERCENT",
       "FPF-ALLQHF_FINANCINGLIQUIDTYGT1LE7_PERCENT", "FPF-ALLQHF_PORTFOLIOLIQUIDITYLE1_PERCENT",
       "FPF-ALLQHF_PORTFOLIOLIQUIDITYGT1LE7_PERCENT"]


def main():
    raw = ROOT / "data" / "raw" / "s12"
    raw.mkdir(parents=True, exist_ok=True)
    targets = [(f"{s}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}") for s in FRED]
    targets += [(f"{m}.json", f"https://data.financialresearch.gov/hf/v1/series/timeseries?mnemonic={m}") for m in OFR]
    manifest = {}
    for name, url in targets:
        with urllib.request.urlopen(url, timeout=120) as response:
            body = response.read()
        (raw / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s12_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(len(manifest), "files")


if __name__ == "__main__":
    main()
