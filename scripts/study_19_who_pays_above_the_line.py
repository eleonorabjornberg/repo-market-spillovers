"""Study 19: who pays above the standing repo facility's line, and did they use the facility?

Design: docs/design-study-19-who-pays-above-the-line.md (committed before the data was fetched).
Fetches into data/raw/s19/ with metadata/s19_manifest.json and writes results/study-19/result.json.
"""
import bisect
import csv
import datetime as dt
import hashlib
import json
import pathlib
import statistics
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "s19"
OUT = ROOT / "results" / "study-19"
START, FULL_ALLOTMENT = "2021-07-29", "2025-12-11"
API = "https://markets.newyorkfed.org/api"


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    urls = {"secured.json": f"{API}/rates/secured/all/search.json?startDate={START}&endDate={today}",
            "DFEDTARU.csv": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFEDTARU"}
    for year in range(2021, int(today[:4]) + 1):  # operations, one request per year
        a, b = max(START, f"{year}-01-01"), min(today, f"{year}-12-31")
        urls[f"rp_{year}.json"] = f"{API}/rp/results/search.json?startDate={a}&endDate={b}&operationTypes=Repo"
    manifest = {}
    for name, url in urls.items():
        with urllib.request.urlopen(url, timeout=180) as response:
            body = response.read()
        (RAW / name).write_bytes(body)
        manifest[name] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                          "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s19_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def line_series():
    out = {}
    with open(RAW / "DFEDTARU.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    keys = sorted(out)
    return lambda d: out[keys[bisect.bisect_right(keys, d) - 1]]


def rates():
    """date -> {"SOFR": {...}, "BGCR": {...}, "TGCR": {...}} with rate and 99th percentile in %."""
    out = {}
    for r in json.loads((RAW / "secured.json").read_text())["refRates"]:
        if r["type"] not in ("SOFR", "BGCR", "TGCR"):
            continue
        try:
            out.setdefault(r["effectiveDate"], {})[r["type"]] = {"rate": float(r["percentRate"]),
                                                                  "p99": float(r["percentPercentile99"])}
        except (TypeError, ValueError, KeyError):
            continue  # "NA": the day is left out, since all three rates are needed
    return {d: v for d, v in out.items() if len(v) == 3}


def takeup():
    """date -> {"total": $bn, "by_close_time": {time: $bn}} over all standing repo operations that day."""
    out = {}
    for f in sorted(RAW.glob("rp_*.json")):
        for op in json.loads(f.read_text()).get("repo", {}).get("operations", []):
            if op.get("operationType") != "Repo" or op.get("term") != "Overnight":
                continue
            amt = float(op.get("totalAmtAccepted") or 0) / 1e9
            day = out.setdefault(op["operationDate"], {"total": 0.0, "by_close_time": {}})
            day["total"] += amt
            day["by_close_time"][op.get("closeTime", "?")] = day["by_close_time"].get(op.get("closeTime", "?"), 0.0) + amt
    return out


def above(rate, line):
    return rate - line > 1e-9


def period_measures(days, rt, line, tk):
    breach = [d for d in days if above(rt[d]["SOFR"]["p99"], line(d))]
    other = [d for d in days if d not in breach]
    q1 = {"n_days": len(days), "n_breach_days": len(breach)}
    if breach:
        for t in ("TGCR", "BGCR"):
            n = sum(above(rt[d][t]["p99"], line(d)) for d in breach)
            q1[f"{t}_p99_also_above"] = n
            q1[f"{t}_p99_also_above_pct"] = round(n / len(breach) * 100, 1)
        q1["mean_gap_sofr_p99_minus_tgcr_p99_bp"] = round(
            statistics.fmean((rt[d]["SOFR"]["p99"] - rt[d]["TGCR"]["p99"]) * 100 for d in breach), 1)
        q1["mean_sofr_p99_above_line_bp"] = round(statistics.fmean((rt[d]["SOFR"]["p99"] - line(d)) * 100 for d in breach), 1)
        share = q1["TGCR_p99_also_above_pct"]
        q1["verdict"] = ("outside tri-party (in DVP)" if share <= 25 else "everywhere" if share >= 75 else "mixed")
    take = lambda ds: [tk.get(d, {}).get("total", 0.0) for d in ds]  # noqa: E731
    q2 = {}
    if breach:
        tb, to = take(breach), take(other)
        q2 = {"median_takeup_breach_days_bn": round(statistics.median(tb), 2),
              "median_takeup_other_days_bn": round(statistics.median(to), 2) if to else None,
              "mean_takeup_breach_days_bn": round(statistics.fmean(tb), 2),
              "share_breach_days_with_any_takeup_pct": round(sum(x > 0 for x in tb) / len(tb) * 100, 1),
              "share_other_days_with_any_takeup_pct": round(sum(x > 0 for x in to) / len(to) * 100, 1) if to else None,
              "max_takeup_breach_day_bn": round(max(tb), 2)}
        med = q2["median_takeup_breach_days_bn"]
        q2["verdict"] = ("largely unused when the top of the market paid more" if med < 1 else
                         "used" if med >= 5 else "mixed")
        times = {}
        for d in breach:
            for t, amt in tk.get(d, {}).get("by_close_time", {}).items():
                times[t] = times.get(t, 0.0) + amt
        q2["takeup_on_breach_days_by_operation_close_time_bn"] = {t: round(v, 2) for t, v in sorted(times.items())}
    return q1, q2, breach


def split(breach, rt, line, tk):
    """Post hoc (added after the first results): breach days with facility take-up of at least $1bn against the rest.
    Many days show token take-up of a few million dollars, so "any take-up" is not informative."""
    out = {}
    for label, keep in (("takeup_at_least_1bn", lambda d: tk.get(d, {}).get("total", 0.0) >= 1),
                        ("takeup_below_1bn", lambda d: tk.get(d, {}).get("total", 0.0) < 1)):
        ds = [d for d in breach if keep(d)]
        if not ds:
            out[label] = {"n": 0}
            continue
        out[label] = {"n": len(ds),
                      "mean_sofr_p99_above_line_bp": round(statistics.fmean((rt[d]["SOFR"]["p99"] - line(d)) * 100 for d in ds), 1),
                      "mean_tgcr_p99_minus_line_bp": round(statistics.fmean((rt[d]["TGCR"]["p99"] - line(d)) * 100 for d in ds), 1),
                      "tgcr_p99_also_above": sum(above(rt[d]["TGCR"]["p99"], line(d)) for d in ds),
                      "mean_takeup_bn": round(statistics.fmean(tk.get(d, {}).get("total", 0.0) for d in ds), 2),
                      "first_day": ds[0], "last_day": ds[-1]}
    return out


def main():
    if "--no-fetch" not in sys.argv:
        fetch()
    rt, line, tk = rates(), line_series(), takeup()
    days = sorted(d for d in rt if d >= START)
    result = {"design": "docs/design-study-19-who-pays-above-the-line.md", "manifest": "metadata/s19_manifest.json",
              "data": [days[0], days[-1]], "periods": {}}
    for label, a, b in (("before full allotment", START, "2025-12-10"), ("after full allotment", FULL_ALLOTMENT, "9999")):
        ds = [d for d in days if a <= d <= b]
        q1, q2, breach = period_measures(ds, rt, line, tk)
        result["periods"][label] = {"from": ds[0], "to": ds[-1], "Q1_where": q1, "Q2_takeup": q2,
                                    "post_hoc_split": split(breach, rt, line, tk),
                                    "breach_days": [{"date": d, "sofr_p99_above_bp": round((rt[d]["SOFR"]["p99"] - line(d)) * 100, 1),
                                                     "tgcr_p99_above_bp": round((rt[d]["TGCR"]["p99"] - line(d)) * 100, 1),
                                                     "takeup_bn": round(tk.get(d, {}).get("total", 0.0), 2)}
                                                    for d in breach]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "breach_days"} for k, v in result["periods"].items()},
                     indent=1))


if __name__ == "__main__":
    main()
