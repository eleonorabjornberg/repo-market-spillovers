"""Fetch study 03's series into data/raw/chain/ and record them in metadata/chain_manifest.json.

Sources: FRED, Treasury's Monthly Statement of the Public Debt (Fiscal Data API), OFR (Hedge Fund Monitor and
Short-term Funding Monitor) and the CFTC's Traders in Financial Futures. Raw files are not committed.
"""
import datetime as dt
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRED = ["BOGZ1FL892150005Q", "TREAST"]
OFR_HF = ["FPF-BORROW_REPO_SUM", "FPF-ASSETCLASS_LTREASURY_SUM", "FPF-ASSETCLASS_STREASURY_SUM",
          "FICC-SPONSORED_REPO_VOL", "FICC-SPONSORED_REVREPO_VOL"]
OFR_STFM = ["MMF-MMF_RP_TOT-M", "MMF-MMF_RP_wFICC-M", "MMF-MMF_RP_wFR-M", "MMF-MMF_RP_wDFI-M", "MMF-MMF_RP_wFFI-M",
            "MMF-MMF_RP_wOCP-M", "REPO-DVP_TV_TOT-P"]
# CFTC contract code -> face value per contract, USD
CFTC_CONTRACTS = {"042601": 200_000, "044601": 100_000, "043602": 100_000, "043607": 100_000, "020601": 100_000,
                  "020604": 100_000}
MSPD = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/debt/mspd/mspd_table_1"
        "?filter=security_type_desc:eq:Marketable&fields=record_date,security_class_desc,debt_held_public_mil_amt"
        "&sort=record_date&page[size]=10000")
CFTC = ("https://publicreporting.cftc.gov/resource/gpe5-46if.json?" + urllib.parse.urlencode({
    "$select": "report_date_as_yyyy_mm_dd,cftc_contract_market_code,lev_money_positions_long,lev_money_positions_short",
    "$where": "cftc_contract_market_code in(" + ",".join(f"'{c}'" for c in CFTC_CONTRACTS) + ")",
    "$order": "report_date_as_yyyy_mm_dd", "$limit": "50000"}))


def targets():
    for s in FRED:
        yield f"{s}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
    for m in OFR_HF:
        yield f"OFRHF_{m}.json", f"https://data.financialresearch.gov/hf/v1/series/timeseries?mnemonic={m}"
    for m in OFR_STFM:
        yield f"OFR_{m}.json", f"https://data.financialresearch.gov/v1/series/timeseries?mnemonic={m}"
    yield "MSPD_marketable.json", MSPD
    yield "CFTC_TFF_treasury.json", CFTC


def main():
    raw = ROOT / "data" / "raw" / "chain"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, url in targets():
        with urllib.request.urlopen(url, timeout=180) as response:
            body = response.read()
        (raw / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        print(name, len(body))
    (ROOT / "metadata" / "chain_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
