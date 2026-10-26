"""The watch (study 07, part 2): fetch the latest data, compute the flags fixed in docs/design-study-07-watch.md, and
build the public page.

Run monthly by .github/workflows/watch.yml. Writes:
  results/watch/latest.json        this run's readings and flags
  results/watch/flags_history.csv  one row per month (re-running a month replaces its row)
  results/watch/swap_daily.csv     daily 10-year SOFR swap spread, extended incrementally from DTCC
  site/index.html                  the public page
A monitor, not a study: it scores nothing and changes no verdict.
"""
import csv
import datetime as dt
import html
import io
import json
import pathlib
import statistics
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from spillovers import history as h  # noqa: E402
import fetch_chain  # noqa: E402
import fetch_dtcc  # noqa: E402
import study_10_prospective as s10  # noqa: E402

RAW = ROOT / "data" / "raw" / "watch"
OUT = ROOT / "results" / "watch"
SITE = ROOT / "site"
FRED = ["SOFR", "IORB", "BAA10Y", "DGS10"]
OFR_FSI = "https://www.financialresearch.gov/financial-stress-index/data/fsi.csv"
SWAP_SEED = ROOT / "results" / "study-05" / "swap_rates_daily.csv"
DEADLINES = {"Cash Treasury clearing": "2026-12-31", "Repo clearing": "2027-06-30"}
FLAGS = {
    "F1": ("Repo above the Fed's rate", "Monthly average SOFR − IORB above 0 bp: reserves no longer ample."),
    "F2": ("Repo spike", "A day with SOFR − IORB at 10 bp or more: stress beyond the calendar's usual."),
    "F3": ("Hedge-fund repo at a record", "Hedge funds' repo borrowing at its highest share of private Treasuries since 2013."),
    "F4": ("Basis trade at a record", "Leveraged funds' Treasury futures short above its previous peak share of private Treasuries."),
    "F5": ("Moving away from clearing", "Sponsored repo's share of cleared volume down three months running while hedge-fund repo has not fallen."),
    "F6": ("Swap spreads at April 2025 levels", "10-year SOFR swap spread at −60 bp or below on any day: dealer balance sheets strained."),
    "F7": ("Broad stress", "OFR financial stress index above 0 on average: more stress than usual across markets."),
    "F8": ("Complacency", "Baa − 10-year spread in the tightest 5% of its history since 1986: risk priced as if absent."),
}


def get(url):
    with urllib.request.urlopen(url, timeout=180) as response:
        return response.read()


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    fetched = {}
    for name, url in fetch_chain.targets():
        if name.startswith("BOGZ1"):
            continue
        (RAW / name).write_bytes(get(url))
        fetched[name] = url
    for s in FRED:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}"
        (RAW / f"{s}.csv").write_bytes(get(url))
        fetched[f"{s}.csv"] = url
    (RAW / "OFR_FSI.csv").write_bytes(get(OFR_FSI))
    fetched["OFR_FSI.csv"] = OFR_FSI
    return fetched


def fred(name):
    out = {}
    with open(RAW / f"{name}.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def ofr(name):
    return {d: float(v) for d, v in json.loads((RAW / name).read_text()) if v is not None}


def weighted_median(pairs):
    pairs = sorted(pairs)
    total, acc = sum(w for _, w in pairs), 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2:
            return v


def update_swaps(dgs10):
    """Extend results/watch/swap_daily.csv with DTCC days after its last date. Returns date -> 10y spread (bp)."""
    path = OUT / "swap_daily.csv"
    rows = {}
    if path.exists():
        with open(path, newline="") as f:
            rows = {r["date"]: r for r in csv.DictReader(f)}
    else:
        with open(SWAP_SEED, newline="") as f:
            for r in csv.DictReader(f):
                if r["sofr_swap_10y_pct"]:
                    rows[r["date"]] = {"date": r["date"], "swap_10y_pct": r["sofr_swap_10y_pct"],
                                       "trades_10y": r["trades_10y"], "spread_10y_bp": r["swap_spread_10y_bp"]}
    day = dt.date.fromisoformat(max(rows)) + dt.timedelta(days=1)
    today = dt.date.today()
    while day < today:
        if day.weekday() < 5:
            try:
                body = get(fetch_dtcc.URL.format(d=day))
            except urllib.error.HTTPError as e:
                if e.code not in (403, 404):
                    raise
                body = None
            if body:
                z = zipfile.ZipFile(io.BytesIO(body))
                trades = []
                with z.open(z.namelist()[0]) as member:
                    for r in csv.DictReader(io.TextIOWrapper(member, "utf-8")):
                        t = fetch_dtcc.keep(r)
                        if t and t["tenor_years"] >= 5 and t["execution"] == day.isoformat():
                            trades.append((t["fixed_rate"] * 100, t["notional"]))
                if len(trades) >= 5:
                    rate = weighted_median(trades)
                    key = day.isoformat()
                    spread = (rate - dgs10[key]) * 100 if key in dgs10 else None
                    rows[key] = {"date": key, "swap_10y_pct": f"{rate:.5f}", "trades_10y": len(trades),
                                 "spread_10y_bp": "" if spread is None else f"{spread:.2f}"}
        day += dt.timedelta(days=1)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "swap_10y_pct", "trades_10y", "spread_10y_bp"])
        w.writeheader()
        for k in sorted(rows):
            w.writerow(rows[k])
    return {k: float(r["spread_10y_bp"]) for k, r in rows.items() if r["spread_10y_bp"]}


def ratio(num, den):
    return {k: v / den[k] * 100 for k, v in num.items() if k in den and den[k]}


def flags_from(readings, hf, fut, sponsored, month):
    """The eight flags of docs/design-study-07-watch.md, from this month's readings and the monthly series.

    hf: hedge-fund repo % of private Treasuries (quarterly, carried to months); fut: leveraged funds' futures short %
    of private Treasuries; sponsored: sponsored reverse repo % of DVP volume. Only months up to `month` are read.
    """
    hf = {k: v for k, v in hf.items() if k <= month}
    fut = {k: v for k, v in fut.items() if k <= month}
    hf_m, fut_m = max(hf), max(fut)
    hf_v, fut_v = hf[hf_m], fut[fut_m]
    sp_keys = sorted(k for k in sponsored if k <= month)[-4:]
    hf_prev = [v for k, v in hf.items() if k < hf_m]
    hf_prev_q = hf.get(h.month_add(hf_m, -3))
    fut_prev = [v for k, v in fut.items() if k < fut_m]
    return {
        "F1": readings["sofr_iorb_month_avg_bp"] is not None and readings["sofr_iorb_month_avg_bp"] > 0,
        "F2": readings["sofr_iorb_month_max_bp"] is not None and readings["sofr_iorb_month_max_bp"] >= 10,
        "F3": bool(hf_prev) and hf_v >= max(hf_prev),
        "F4": bool(fut_prev) and fut_v > max(fut_prev),
        "F5": len(sp_keys) == 4 and all(sponsored[a] > sponsored[b] for a, b in zip(sp_keys, sp_keys[1:]))
        and hf_prev_q is not None and hf_v >= hf_prev_q,
        "F6": readings["swap_spread_10y_month_min_bp"] is not None and readings["swap_spread_10y_month_min_bp"] <= -60,
        "F7": readings["ofr_fsi_month_avg"] is not None and readings["ofr_fsi_month_avg"] > 0,
        "F8": readings["baa_10y_bp"]["percentile"] <= 5,
    }


def compute(run_date):
    month = h.month_add(run_date[:7], -1)  # the latest complete month
    m = h.complete_months
    sofr, iorb = fred("SOFR"), fred("IORB")
    spread_daily = {d: (sofr[d] - iorb[d]) * 100 for d in sofr if d in iorb}
    spread_month = [v for d, v in spread_daily.items() if d[:7] == month]
    dgs10 = fred("DGS10")
    swaps = update_swaps(dgs10)

    mspd = {}
    for r in json.loads((RAW / "MSPD_marketable.json").read_text())["data"]:
        mspd[r["record_date"]] = mspd.get(r["record_date"], 0.0) + float(r["debt_held_public_mil_amt"])
    fed = m(fred("TREAST"), "daily")
    phmt = {k: v / 1e3 - fed[k] / 1e3 for k, v in m(mspd, "monthly").items() if k in fed}
    hf = ratio({k: v / 1e9 for k, v in m(ofr("OFRHF_FPF-BORROW_REPO_SUM.json"), "quarterly").items()}, phmt)
    fut_daily = {}
    for r in json.loads((RAW / "CFTC_TFF_treasury.json").read_text()):
        d = r["report_date_as_yyyy_mm_dd"][:10]
        face = fetch_chain.CFTC_CONTRACTS[r["cftc_contract_market_code"]]
        fut_daily[d] = fut_daily.get(d, 0.0) + (float(r["lev_money_positions_short"])
                                                - float(r["lev_money_positions_long"])) * face / 1e9
    fut = ratio(m(fut_daily, "daily"), phmt)
    sponsored = ratio(m(ofr("OFRHF_FICC-SPONSORED_REVREPO_VOL.json"), "daily"),
                      m(ofr("OFR_REPO-DVP_TV_TOT-P.json"), "daily"))
    ficc_share = ratio(m(ofr("OFR_MMF-MMF_RP_wFICC-M.json"), "monthly"), m(ofr("OFR_MMF-MMF_RP_TOT-M.json"), "monthly"))
    with open(RAW / "OFR_FSI.csv", newline="") as f:
        fsi_daily = {r["Date"]: float(r["OFR FSI"]) for r in csv.DictReader(f) if r["OFR FSI"]}
    fsi = h.to_monthly(fsi_daily)
    baa = h.to_monthly({d: v * 100 for d, v in fred("BAA10Y").items()})

    def latest(s, upto=month):
        keys = [k for k in s if k <= upto]
        return (max(keys), s[max(keys)]) if keys else (None, None)

    hf_m, hf_v = latest(hf)
    fut_m, fut_v = latest(fut)
    sp_keys = sorted(k for k in sponsored if k <= month)[-4:]
    baa_hist = [v for k, v in baa.items() if k <= month]
    baa_m, baa_v = latest(baa)
    readings = {
        "sofr_iorb_month_avg_bp": round(statistics.fmean(spread_month), 2) if spread_month else None,
        "sofr_iorb_month_max_bp": round(max(spread_month), 2) if spread_month else None,
        "hf_repo_pct_phmt": {"month": hf_m, "value": round(hf_v, 2) if hf_v else None},
        "levfund_futures_short_pct_phmt": {"month": fut_m, "value": round(fut_v, 2) if fut_v else None},
        "sponsored_revrepo_pct_dvp": {k: round(sponsored[k], 2) for k in sp_keys},
        "ficc_share_mmf_repo": {"month": latest(ficc_share)[0], "value": round(latest(ficc_share)[1], 2)},
        "swap_spread_10y_month_min_bp": min((v for d, v in swaps.items() if d[:7] == month), default=None),
        "ofr_fsi_month_avg": round(fsi[month], 3) if month in fsi else None,
        "baa_10y_bp": {"month": baa_m, "value": round(baa_v, 1), "percentile": round(
            100 * sum(x <= baa_v for x in baa_hist) / len(baa_hist), 1)},
    }
    flags = flags_from(readings, hf, fut, sponsored, month)
    upto = lambda s, start="": {k: v for k, v in s.items() if start <= k and k[:7] <= month}  # noqa: E731
    charts = {
        "spread": upto(spread_daily, h.month_add(month, -23)),
        "hf": upto(hf, "2013-01"),
        "fut": upto(fut, "2013-01"),
        "sponsored": upto(sponsored),
        "swaps": upto(swaps),
        "fsi": upto(fsi, "2013-01"),
    }
    return month, readings, flags, charts


def svg_line(series, title, unit, threshold=None, threshold_label="", width=440, height=190, daily=False):
    keys = sorted(series)
    if len(keys) < 2:
        return ""
    vals = [series[k] for k in keys]
    lo, hi = min(vals + ([threshold] if threshold is not None else [])), max(vals + ([threshold] if threshold is not None else []))
    pad = (hi - lo) * 0.1 or 1
    lo, hi = lo - pad, hi + pad
    left, right, top, bottom = 44, 12, 12, 26
    x = lambda i: left + i / (len(keys) - 1) * (width - left - right)  # noqa: E731
    y = lambda v: top + (hi - v) / (hi - lo) * (height - top - bottom)  # noqa: E731
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">']
    for v in (lo + pad, (lo + hi) / 2, hi - pad):
        parts.append(f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                     f'<text class="tick" x="{left - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v:.1f}</text>')
    if threshold is not None:
        parts.append(f'<line class="threshold" x1="{left}" x2="{width - right}" y1="{y(threshold):.1f}" '
                     f'y2="{y(threshold):.1f}"/><text class="tick warn" x="{width - right}" y="{y(threshold) - 5:.1f}" '
                     f'text-anchor="end">{html.escape(threshold_label)}</text>')
    for j, i in enumerate((0, len(keys) // 3, 2 * len(keys) // 3, len(keys) - 1)):
        label = keys[i][:7] if daily or len(keys) <= 40 else keys[i][:4]
        anchor = "start" if j == 0 else "end" if j == 3 else "middle"
        parts.append(f'<text class="tick" x="{x(i):.1f}" y="{height - 6}" text-anchor="{anchor}">{label}</text>')
    parts.append(f'<polyline class="line" points="{pts}"/>')
    parts.append(f'<circle class="dot" cx="{x(len(keys) - 1):.1f}" cy="{y(vals[-1]):.1f}" r="3.5"/>')
    parts.append("</svg>")
    return (f'<figure><figcaption><span>{html.escape(title)}</span><span class="unit">{html.escape(unit)}'
            f' · {keys[-1]}: {vals[-1]:.1f}</span></figcaption>{"".join(parts)}</figure>')


def prospective_section(status):
    """Study 10's three pre-registered tests, as they stand."""
    a = status["A_clearing_deadlines"]
    rows = []
    for key, label in (("D1_cash_clearing", "Cash Treasury clearing, 31 Dec 2026"),
                       ("D2_repo_clearing", "Repo clearing, 30 Jun 2027")):
        e = a[key]
        rows.append((label, e.get("verdict") or "pending: scored after the deadline's window closes"))
    b = status["B_credit_lead"]
    rows.append(("Credit after repo shocks", b.get("verdict") or
                 f"pending: {b['n_shock_days']} of {s10.LEAD_MIN_SHOCKS} new repo shocks so far"))
    c = status["C_chain_under_stress"]
    rows.append(("The chain under stress", c.get("verdict") or "pending: no stress event yet (counting from 2 November 2026)"))
    ref = c.get("reference_april_2025")
    signed = lambda v, fmt: format(v, fmt).replace("-", "−")  # noqa: E731
    note = (f" For reference, April 2025 scores <b>{ref['verdict']}</b>: repo peaked at {ref['C1_max_noncal_spread_bp']:.0f} bp on"
            f" ordinary days and the basis-trade proxy changed {signed(ref['C2_futures_short_change_pct'], '+.1f')}%, while"
            f" the 10-year swap spread moved {signed(ref['C3_swap_spread_change_bp'], '+.0f')} bp.") if ref else ""
    trs = "".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(v)}</td></tr>" for k, v in rows)
    return (f'<h2>Pre-registered tests</h2><p class="note">Set on 26 October 2026, before their data existed, with the code '
            f'that scores them (<a href="https://github.com/eleonorabjornberg/repo-market-spillovers/blob/main/docs/'
            f'design-study-10-prospective.md">study 10</a>).{note}</p><table class="tests"><tbody>{trs}</tbody></table>')


def page(run_date, month, readings, flags, charts, prospective=""):
    today = dt.date.fromisoformat(run_date)
    countdown = "".join(
        f'<div class="deadline"><b>{(dt.date.fromisoformat(d) - today).days}</b> days<span>{html.escape(n)} · '
        f'{dt.date.fromisoformat(d):%-d %b %Y}</span></div>' for n, d in DEADLINES.items()
        if dt.date.fromisoformat(d) >= today)
    on = sum(flags.values())
    cards = "".join(
        f'<li class="flag {"on" if flags[k] else "off"}"><div class="state">{"ON" if flags[k] else "off"}</div>'
        f'<div><b>{k} · {html.escape(FLAGS[k][0])}</b><p>{html.escape(FLAGS[k][1])}</p></div></li>' for k in FLAGS)
    figs = "".join([
        svg_line(charts["spread"], "SOFR − IORB, last 24 months", "bp, daily", 0, "IORB", daily=True),
        svg_line(charts["swaps"], "10-year SOFR swap spread", "bp, daily", -60, "April 2025 stress (−60)", daily=True),
        svg_line(charts["hf"], "Hedge-fund repo borrowing", "% of private Treasuries"),
        svg_line(charts["fut"], "Leveraged funds' Treasury futures short", "% of private Treasuries"),
        svg_line(charts["sponsored"], "FICC sponsored reverse repo", "% of cleared DVP repo"),
        svg_line(charts["fsi"], "OFR financial stress index", "0 = average", 0, "average"),
    ])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Repo Market Watch</title>
<meta name="description" content="A monthly public watch on the US repo market and the leverage behind the Treasury market.">
<style>
:root{{--bg:#fafaf9;--fg:#1c1917;--muted:#57534e;--line:#e7e5e4;--card:#fff;--accent:#1e3a8a;--warn:#b91c1c;--ok:#15803d}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0c0a09;--fg:#f5f5f4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#93c5fd;--warn:#f87171;--ok:#4ade80}}}}
:root[data-theme="dark"]{{--bg:#0c0a09;--fg:#f5f5f4;--muted:#a8a29e;--line:#292524;--card:#1c1917;--accent:#93c5fd;--warn:#f87171;--ok:#4ade80}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1080px;margin:0 auto;padding:32px 16px 64px}}h1{{font-size:clamp(28px,5vw,40px);margin:0 0 6px;letter-spacing:-.02em}}
h2{{font-size:20px;margin:40px 0 12px}}.sub{{color:var(--muted);margin:0 0 20px;max-width:720px}}
.deadlines{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}}.deadline{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:200px}}
.deadline b{{font-size:28px;margin-right:6px}}.deadline span{{display:block;color:var(--muted);font-size:14px}}
.summary{{font-size:18px;padding:14px 16px;border-left:4px solid {"var(--warn)" if on else "var(--ok)"};background:var(--card);border-radius:6px}}
ul.flags{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px}}
.flag{{display:flex;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.flag p{{margin:4px 0 0;color:var(--muted);font-size:14px}}.state{{font-weight:700;font-size:13px;min-width:38px;text-align:center;border-radius:6px;padding:4px 0;height:fit-content}}
.on .state{{background:var(--warn);color:var(--bg)}}.off .state{{border:1px solid var(--line);color:var(--muted)}}
.figs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}}figure{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
figcaption{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;font-weight:600;font-size:14px;margin-bottom:6px}}.unit{{color:var(--muted);font-weight:400}}
svg{{width:100%;height:auto;display:block}}.line{{fill:none;stroke:var(--accent);stroke-width:1.6}}.dot{{fill:var(--warn)}}.grid{{stroke:var(--line)}}
.threshold{{stroke:var(--warn);stroke-dasharray:4 3}}.tick{{fill:var(--muted);font-size:12px}}.warn{{fill:var(--warn)}}
.note{{color:var(--muted);font-size:14px;max-width:760px}}
table.tests{{border-collapse:collapse;width:100%;max-width:760px;background:var(--card);font-size:15px}}table.tests td{{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}table.tests td:first-child{{font-weight:600;width:40%}}a{{color:var(--accent)}}
</style></head><body><main>
<nav style="font-size:15px;margin-bottom:20px">Repo Market Watch · <a href="findings.html">Findings: is the repo market signalling a crisis?</a></nav>
<h1>Repo Market Watch</h1>
<p class="sub">A monthly look at the US repo market and the leverage behind the Treasury market. Data to the end of
<b>{dt.date.fromisoformat(month + "-01"):%B %Y}</b>; built {today:%-d %B %Y}.</p>
<div class="deadlines">{countdown}</div>
<p class="summary"><b>{on} of {len(FLAGS)}</b> flags on this month.</p>
<h2>Flags</h2>
<ul class="flags">{cards}</ul>
<p class="note">A flag says something has changed, not that a crisis is coming. The project's studies found that none of
these indicators reliably warned of past stress (studies 04–06). The flags and their thresholds were fixed before the
first build, in <a href="https://github.com/eleonorabjornberg/repo-market-spillovers/blob/main/docs/design-study-07-watch.md">the design</a>.
Much of the growth in cleared repo since late 2023 is the market moving ahead of the clearing deadlines
(<a href="https://github.com/eleonorabjornberg/repo-market-spillovers/blob/main/results/study-07/result.md">study 07</a>).</p>
{prospective}
<h2>The readings</h2>
<div class="figs">{figs}</div>
<p class="note">Sources: FRED, the OFR (financial stress index, Hedge Fund Monitor, Short-term Funding Monitor), the CFTC
(Traders in Financial Futures), Treasury (Monthly Statement of the Public Debt), and DTCC's public swap reports.
"Private Treasuries" means marketable Treasury debt held by the public minus the Fed's holdings. The code, the studies
and their limits are at <a href="https://github.com/eleonorabjornberg/repo-market-spillovers">repo-market-spillovers</a>.</p>
</main></body></html>
"""


def main():
    run_date = dt.date.today().isoformat()
    fetched = fetch()
    month, readings, flags, charts = compute(run_date)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "latest.json").write_text(json.dumps({"run_date": run_date, "month": month, "flags": flags,
                                                 "readings": readings, "sources": fetched}, indent=1) + "\n")
    hist_path = OUT / "flags_history.csv"
    rows = {}
    if hist_path.exists():
        with open(hist_path, newline="") as f:
            rows = {r["month"]: r for r in csv.DictReader(f)}
    rows[month] = {"month": month, "run_date": run_date, **{k: int(v) for k, v in flags.items()}}
    with open(hist_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["month", "run_date", *FLAGS])
        w.writeheader()
        for k in sorted(rows):
            w.writerow(rows[k])
    SITE.mkdir(parents=True, exist_ok=True)
    status = s10.run(run_date)
    (SITE / "index.html").write_text(page(run_date, month, readings, flags, charts, prospective_section(status)))
    print(json.dumps({"month": month, "flags": flags, "readings": readings}, indent=1))


if __name__ == "__main__":
    main()
