"""Study 14: what keeps Treasury repo outside central clearing? The uncleared segment, matched books, year-ends.

Design: docs/design-study-14-haircuts-netting.md (committed before the data was fetched).
Fetches the New York Fed's primary dealer statistics (FR 2004) into data/raw/s14/ with metadata/s14_manifest.json and
writes results/study-14/result.json and weekly.csv.
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import statistics
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "s14"
OUT = ROOT / "results" / "study-14"
VENUES = {"ub_general": "UBGUTSET", "ub_specified": "UBSUTSET", "cb_general": "CBGUTSET", "cb_specified": "CBSUTSET",
          "cb_sponsored": "CBSPUTSET", "tri_general": "TRIGUTSET", "tri_sponsored": "TRISPUTSET", "gcf": "GCFUTSET"}
TERMS = ("", "TAL30", "TAG30")
SIDES = {"repo": "PDSORA", "reverse_repo": "PDSIRRA"}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for side in SIDES.values():
        for code in VENUES.values():
            for term in TERMS:
                key = f"{side}-{code}{term}"
                url = f"https://markets.newyorkfed.org/api/pd/get/{key}.json"
                with urllib.request.urlopen(url, timeout=120) as response:
                    body = response.read()
                (RAW / f"{key}.json").write_bytes(body)
                manifest[f"{key}.json"] = {"url": url, "sha256": hashlib.sha256(body).hexdigest(),
                                           "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (ROOT / "metadata" / "s14_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


SUPPRESSED_AS_ZERO = False  # the sensitivity version (design amendment) sets this


def series(key):
    """date -> $bn; suppressed ('*') values left out, or zero in the sensitivity version."""
    out = {}
    for row in json.loads((RAW / f"{key}.json").read_text())["pd"]["timeseries"]:
        try:
            out[row["asofdate"]] = float(row["value"]) / 1000  # FR 2004 reports $ millions
        except ValueError:
            if SUPPRESSED_AS_ZERO:
                out[row["asofdate"]] = 0.0
    return out


def venue_totals(side):
    """week -> {venue: $bn summed over terms}; a venue is present only when all its terms are."""
    parts = {v: [series(f"{SIDES[side]}-{code}{t}") for t in TERMS] for v, code in VENUES.items()}
    weeks = sorted(set().union(*(set(p) for ps in parts.values() for p in ps)))
    out = {}
    for w in weeks:
        out[w] = {v: sum(p[w] for p in ps) for v, ps in parts.items() if all(w in p for p in ps)}
    return out


def uncleared_share(t):
    need = ("ub_general", "ub_specified", "cb_general", "cb_specified", "cb_sponsored")
    if not all(k in t for k in need):
        return None
    ub = t["ub_general"] + t["ub_specified"]
    allb = ub + t["cb_general"] + t["cb_specified"] + t["cb_sponsored"]
    return ub / allb * 100 if allb else None


def overlap(a, b):
    return min(a, b) / max(a, b) if max(a, b) else None


def mean13(values):
    v = [x for x in values if x is not None]
    return round(statistics.fmean(v), 3) if v else None


def measures():
    rep, rev = venue_totals("repo"), venue_totals("reverse_repo")
    weeks = sorted(set(rep) & set(rev))
    rows = []
    for w in weeks:
        a, b = rep[w], rev[w]
        cb_a = sum(a.get(k, 0) for k in ("cb_specified", "cb_sponsored")) if all(k in a for k in ("cb_specified", "cb_sponsored")) else None
        cb_b = sum(b.get(k, 0) for k in ("cb_specified", "cb_sponsored")) if all(k in b for k in ("cb_specified", "cb_sponsored")) else None
        rows.append({"week": w,
                     "rev_uncleared_bn": round(b["ub_general"] + b["ub_specified"], 1) if "ub_specified" in b and "ub_general" in b else None,
                     "rev_sponsored_bn": round(b["cb_sponsored"], 1) if "cb_sponsored" in b else None,
                     "rep_uncleared_bn": round(a["ub_general"] + a["ub_specified"], 1) if "ub_specified" in a and "ub_general" in a else None,
                     "M1_rev_uncleared_share": None if uncleared_share(b) is None else round(uncleared_share(b), 2),
                     "M1_rep_uncleared_share": None if uncleared_share(a) is None else round(uncleared_share(a), 2),
                     "M2_uncleared_specified": overlap(a["ub_specified"], b["ub_specified"]) if "ub_specified" in a and "ub_specified" in b else None,
                     "M2_cleared_specified_sponsored": overlap(cb_a, cb_b) if cb_a is not None and cb_b is not None else None})
    complete = [r for r in rows if r["M1_rev_uncleared_share"] is not None and r["M1_rep_uncleared_share"] is not None]
    first, last = complete[:13], complete[-13:]
    q1 = {k: {"first_13_weeks": mean13(r[k] for r in first), "last_13_weeks": mean13(r[k] for r in last)}
          for k in ("M1_rev_uncleared_share", "M1_rep_uncleared_share", "rev_uncleared_bn", "rev_sponsored_bn", "rep_uncleared_bn")}
    d = q1["M1_rev_uncleared_share"]["last_13_weeks"] - q1["M1_rev_uncleared_share"]["first_13_weeks"]
    q1_verdict = "shrinking" if d <= -10 else "holding" if abs(d) < 10 else "growing"
    m2 = [r["M2_uncleared_specified"] for r in rows if r["M2_uncleared_specified"] is not None]
    q2 = {"uncleared_specified_mean": round(statistics.fmean(m2), 3),
          "uncleared_specified_first_13": mean13(r["M2_uncleared_specified"] for r in first),
          "uncleared_specified_last_13": mean13(r["M2_uncleared_specified"] for r in last),
          "cleared_specified_sponsored_mean": mean13(r["M2_cleared_specified_sponsored"] for r in rows)}
    q2["large_matched_book"] = q2["uncleared_specified_mean"] > 0.7
    q2["shrank"] = q2["uncleared_specified_last_13"] <= q2["uncleared_specified_first_13"] - 0.1
    by_week = {r["week"]: r["M1_rev_uncleared_share"] for r in rows}
    q3 = {}
    for y in (2022, 2023, 2024, 2025):
        ye = [w for w in weeks if f"{y}-12-17" <= w <= f"{y}-12-31"]
        before = [w for w in weeks if f"{y}-11-15" <= w < f"{y}-12-17"][-4:]
        after = [w for w in weeks if f"{y + 1}-01-01" <= w <= f"{y + 1}-02-10"][:4]
        vals = lambda ws: [by_week[w] for w in ws if by_week.get(w) is not None]  # noqa: E731
        if vals(ye) and vals(before) and vals(after):
            q3[str(y)] = {"year_end": round(statistics.fmean(vals(ye)), 2), "before": round(statistics.fmean(vals(before)), 2),
                          "after": round(statistics.fmean(vals(after)), 2)}
            q3[str(y)]["dip"] = q3[str(y)]["year_end"] < min(q3[str(y)]["before"], q3[str(y)]["after"])
    q3_verdict = sum(v["dip"] for v in q3.values()) >= 3
    return rows, {"weeks": [weeks[0], weeks[-1]], "n_weeks": len(weeks), "n_complete_weeks": len(complete),
                  "first_window": [first[0]["week"], first[-1]["week"]], "last_window": [last[0]["week"], last[-1]["week"]],
                  "Q1_uncleared_segment": {**q1, "change_pp": round(d, 2), "verdict": q1_verdict},
                  "Q2_matched_book": q2, "Q3_year_end": {"by_year": q3, "dip_in_3_of_4": q3_verdict}}


def main():
    global SUPPRESSED_AS_ZERO
    fetch()
    rows, main_result = measures()
    SUPPRESSED_AS_ZERO = True
    _, sensitivity = measures()
    SUPPRESSED_AS_ZERO = False
    result = {"design": "docs/design-study-14-haircuts-netting.md", "manifest": "metadata/s14_manifest.json",
              **main_result, "sensitivity_suppressed_as_zero": sensitivity}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    with open(OUT / "weekly.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
