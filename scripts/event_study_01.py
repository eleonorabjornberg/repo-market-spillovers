"""Event study 01: do repo pressure days move wider markets more when reserves are scarce?

Design: docs/design-event-study-01.md (committed before the first run).
Inputs: data/panel.csv and data/fomc_calendar.json (scripts/build_panel.sh), data/raw/*.csv (scripts/fetch_fred.py).
Writes: results/event-study-01/result.json and chart.svg. The result page, result.md, is written by hand from
result.json.
"""
import hashlib
import json
import math
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from spillovers import events as ev  # noqa: E402
from spillovers import outcomes as oc  # noqa: E402
from spillovers import stats  # noqa: E402

DRAWS = 5000
MIN_EVENTS = 10  # raised from 3 after the first run: see "Amendments" in the design
SEED = 20261026
MAIN_EVENT = "month_end"
MAIN_CONTRAST = ("scarce_2025_26", "floor_2021_23")
REPLICATION = ("scarce_2018_19", "floor_2021_23")
OUT = ROOT / "results" / "event-study-01"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_changes(rows):
    dates = [r["date"] for r in rows]
    iorb = {r["date"]: r["iorb"] for r in rows}
    spread = {r["date"]: (r["sofr"] - r["iorb"]) * 100 for r in rows if r["sofr"] is not None}
    changes = {
        "spread_chg_bp": oc.daily_changes(dates, {d: v / 100 for d, v in spread.items()}, "bp"),
        "spread_level_bp": {d: spread.get(d) for d in dates[1:]},
    }
    for series, (name, kind) in oc.FRED_SERIES.items():
        changes[name] = oc.daily_changes(dates, oc.read_fred(ROOT / "data" / "raw" / f"{series}.csv"), kind, iorb)
    return dates, changes


def summarise(point, draws):
    lo, hi = stats.interval(draws)
    return {"estimate": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)],
            "excludes_zero": bool(lo > 0 or hi < 0)}


def main():
    rng = random.Random(SEED)
    rows = ev.read_panel(ROOT / "data" / "panel.csv")
    labels, excluded = ev.classify(rows, ev.fomc_decision_dates(ROOT / "data" / "fomc_calendar.json"))
    dates, changes = build_changes(rows)

    outcome_names = ["spread_chg_bp", "spread_level_bp"] + [n for n, _ in oc.FRED_SERIES.values()]
    effects = {}   # (regime, event, outcome, measure) -> (point, draws)
    table = []
    counts = {}
    for regime in ev.REGIMES:
        in_regime = [d for d in dates[1:] if ev.regime_of(d) == regime and d not in excluded]
        base_days = [d for d in in_regime if not labels[d]]
        for outcome in outcome_names:
            ch = changes[outcome]
            measures = {"signed": lambda x: x, "size": abs}
            if outcome == "spread_level_bp":
                measures = {"signed": lambda x: x}
            for measure, f in measures.items():
                base = [f(ch[d]) for d in base_days if ch[d] is not None]
                base_draws = stats.boot_means(base, DRAWS, rng)
                for event in ev.EVENTS:
                    evs = [f(ch[d]) for d in in_regime if event in labels[d] and ch[d] is not None]
                    counts[(regime, event)] = max(counts.get((regime, event), 0), len(evs))
                    if len(evs) < MIN_EVENTS or len(base) < 30:
                        continue
                    if outcome in oc.RECENT_ONLY and regime != "scarce_2025_26":
                        continue
                    ev_draws = stats.boot_means(evs, DRAWS, rng)
                    point = stats.mean(evs) - stats.mean(base)
                    draws = [a - b for a, b in zip(ev_draws, base_draws)]
                    effects[(regime, event, outcome, measure)] = (point, draws)
                    table.append({"regime": regime, "event": event, "outcome": outcome, "measure": measure,
                                  "n_event": len(evs), "n_base": len(base), **summarise(point, draws)})

    def did(a, b, event, outcome, measure):
        if (a, event, outcome, measure) not in effects or (b, event, outcome, measure) not in effects:
            return None
        pa, da = effects[(a, event, outcome, measure)]
        pb, db = effects[(b, event, outcome, measure)]
        return summarise(pa - pb, [x - y for x, y in zip(da, db)])

    contrasts = []
    for event in ev.EVENTS:
        for outcome in outcome_names:
            for measure in ("signed", "size"):
                for a, b in (MAIN_CONTRAST, REPLICATION):
                    r = did(a, b, event, outcome, measure)
                    if r:
                        contrasts.append({"contrast": f"{a} - {b}", "event": event, "outcome": outcome,
                                          "measure": measure, **r})

    main_test = [c for c in contrasts if c["event"] == MAIN_EVENT and c["measure"] == "size"
                 and c["outcome"] in oc.MAIN_OUTCOMES]

    # multiplicity: market outcomes only, regime-level effects in the three compared regimes
    market = [t for t in table if t["regime"] in ev.COMPARED_REGIMES and not t["outcome"].startswith("spread")]
    multiplicity = {"intervals": len(market), "excluding_zero": sum(t["excludes_zero"] for t in market),
                    "expected_by_chance": round(0.05 * len(market), 1)}

    passthrough = []
    for regime in ev.REGIMES:
        in_regime = [d for d in dates[1:] if ev.regime_of(d) == regime and d not in excluded]
        for name, _ in oc.FRED_SERIES.values():
            pairs = [(changes["spread_chg_bp"][d], changes[name][d]) for d in in_regime
                     if changes["spread_chg_bp"][d] is not None and changes[name][d] is not None]
            if len(pairs) < 60:
                continue
            slope, (lo, hi) = stats.slope_with_interval([p[0] for p in pairs], [p[1] for p in pairs], 2000, rng)
            passthrough.append({"regime": regime, "outcome": name, "n": len(pairs),
                                "slope_per_bp": round(slope, 4), "ci95": [round(lo, 4), round(hi, 4)],
                                "excludes_zero": bool(lo > 0 or hi < 0)})

    manifest = json.loads((ROOT / "metadata" / "fred_manifest.json").read_text())
    stale = [s for s in oc.FRED_SERIES if sha256(ROOT / "data" / "raw" / f"{s}.csv") != manifest[s]["sha256"]]
    if stale:
        raise ValueError(f"data/raw differs from metadata/fred_manifest.json for {stale}: re-run fetch_fred.py")

    result = {
        "design": "docs/design-event-study-01.md",
        "panel_sha256": sha256(ROOT / "data" / "panel.csv"),
        "fred_manifest": "metadata/fred_manifest.json",
        "panel_span": [dates[0], dates[-1]],
        "seed": SEED, "draws": DRAWS,
        "excluded_days": len(excluded),
        "event_counts": {f"{r}/{e}": n for (r, e), n in sorted(counts.items())},
        "main_test": main_test,
        "multiplicity": multiplicity,
        "contrasts": contrasts,
        "effects": table,
        "passthrough": passthrough,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    (OUT / "chart.svg").write_text(chart(table))
    print(json.dumps({"main_test": main_test, "multiplicity": multiplicity}, indent=1))


def chart(table):
    """Month-end size effect (event mean |change| - baseline), by regime, for the main outcomes: a dot-and-whisker SVG."""
    regimes = ev.COMPARED_REGIMES
    colors = {"scarce_2018_19": "#d97706", "floor_2021_23": "#64748b", "scarce_2025_26": "#b91c1c"}
    panels = ["spread_chg_bp"] + list(oc.MAIN_OUTCOMES)
    titles = {"spread_chg_bp": "SOFR − IORB (bp)", "ust10y_bp": "10y Treasury (bp)", "vix_pts": "VIX (pts)",
              "baa_10y_bp": "Baa − 10y (bp)", "cp_on_fin_iorb_bp": "O/N financial CP − IORB (bp)"}
    pw, ph, top = 200, 230, 60
    w = pw * len(panels) + 20
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {ph + top + 40}" font-family="sans-serif" '
           f'font-size="11"><rect width="100%" height="100%" fill="#fff"/>',
           '<text x="10" y="20" font-size="14" font-weight="bold">Month-end: extra size of the daily move '
           '(mean |Δ| on month-end − other days), 95% bootstrap interval</text>',
           '<text x="10" y="38" fill="#555">Spillover would show as the scarce regimes sitting above the floor '
           'regime in every panel.</text>']
    for i, outcome in enumerate(panels):
        rows = {t["regime"]: t for t in table if t["event"] == MAIN_EVENT and t["outcome"] == outcome
                and t["measure"] == "size" and t["regime"] in regimes}
        lo = min([0] + [r["ci95"][0] for r in rows.values()])
        hi = max([0] + [r["ci95"][1] for r in rows.values()])
        pad = (hi - lo) * 0.1 or 1
        lo, hi = lo - pad, hi + pad
        x0 = 10 + i * pw
        y = lambda v: top + 20 + (hi - v) / (hi - lo) * (ph - 40)  # noqa: E731
        out.append(f'<text x="{x0 + pw / 2}" y="{top + 8}" text-anchor="middle" font-weight="bold">'
                   f'{titles[outcome]}</text>')
        out.append(f'<line x1="{x0 + 20}" x2="{x0 + pw - 10}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="#999" '
                   f'stroke-dasharray="3,3"/>')
        for v in (lo + pad, hi - pad):
            out.append(f'<text x="{x0 + 16}" y="{y(v) + 4:.1f}" text-anchor="end" fill="#555">{v:.1f}</text>')
        for j, regime in enumerate(regimes):
            r = rows.get(regime)
            if not r:
                continue
            cx = x0 + 50 + j * (pw - 90) / 2
            c = colors[regime]
            out.append(f'<line x1="{cx}" x2="{cx}" y1="{y(r["ci95"][0]):.1f}" y2="{y(r["ci95"][1]):.1f}" '
                       f'stroke="{c}" stroke-width="2"/>')
            out.append(f'<circle cx="{cx}" cy="{y(r["estimate"]):.1f}" r="4" fill="{c}"/>')
            out.append(f'<text x="{cx}" y="{ph + top + 2}" text-anchor="middle" fill="{c}">'
                       f'{regime.split("_")[0]}</text>')
            out.append(f'<text x="{cx}" y="{ph + top + 15}" text-anchor="middle" fill="{c}">'
                       f'{regime.split("_", 1)[1].replace("_", "–")}</text>')
    out.append("</svg>\n")
    return "\n".join(out)


if __name__ == "__main__":
    main()
