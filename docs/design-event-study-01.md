# Event study 01: do repo pressure days move wider markets?

Written on 26 October 2026, before the first run. Its one-line findings are only read once this design is
committed.

## The question

The repo-market-model one-pager (October 2026) shows that pressure in overnight funding lands on known calendar days
(the month-end turn, quarter-end, mid-month coupon settlements, tax dates). It also shows that the size of that pressure
depends on reserve scarcity: a month-end added about +5.8 bp to SOFR − IORB in 2018–19, +0.3 bp on the floor in
2021–23, and +4.3 bp in 2025–26.

That gives a natural experiment. The calendar sets the date and the reserve regime sets the dose. If repo pressure
reaches wider markets, the same calendar day should move them **more when reserves are scarce than when they are
abundant**. Comparing the same calendar day across regimes (a difference in differences) nets out what these days do
to markets for reasons unrelated to repo: month-end portfolio rebalancing, index flows, tax-date liquidity.

## Data

- **Repo side:** repo-market-model's published daily panel, built from that repository's tracked fixtures at a pinned
  commit and checked against its published digest (`scripts/build_panel.sh`). It provides SOFR, IORB, the coupon
  settlement amount and the tax-date flag. The spread is `(sofr − iorb) × 100` bp.
- **Wider markets:** FRED (`scripts/fetch_fred.py`). The raw files are not committed; their retrieval time and
  SHA-256 are recorded in `metadata/fred_manifest.json`. FRED serves the latest vintage, so a later fetch need not
  reproduce these bytes.

| Outcome | FRED series | Daily change measured as |
|---|---|---|
| 10-year Treasury yield | DGS10 | bp |
| 2-year Treasury yield | DGS2 | bp |
| 10s–2s curve | T10Y2Y | bp |
| VIX | VIXCLS | index points |
| S&P 500 | SP500 | log return, % |
| Baa corporate − 10-year Treasury | BAA10Y | bp |
| Broad trade-weighted dollar | DTWEXBGS | % |
| 30-day AA financial CP − IORB | RIFSPPFAAD30NB | bp |
| 4-week bill − IORB | DTB4WK | bp |
| ICE BofA US high yield OAS | BAMLH0A0HYM2 | bp (FRED serves only the last three years: 2025–26 only) |
| ICE BofA US corporate OAS | BAMLC0A0CM | bp (likewise) |

Each change is taken from the previous panel business day to the event day; a day where either end is missing is
dropped.

## Regimes (as on the one-pager)

- `scarce_2018_19`: 3 Apr 2018 – 31 Dec 2019
- `floor_2021_23`: 1 Jan 2021 – 31 Dec 2023
- `scarce_2025_26`: 1 Jan 2025 – end of panel (3 Sep 2026)

2020 (COVID, reserves flooding in) and 2024 (the transition) are reported but take no part in the comparison.

## Events

All are taken from panel business days:

- `month_end`: the last business day of each month (quarter-ends included). This is the main event.
- `month_start`: the first business day of each month (the other side of the turn).
- `quarter_end`: the last business day of March, June, September and December.
- `coupon_settle`: a day from the 13th to the 17th with coupon settlement > 0 that is not a month-end or month-start.
- `tax`: a day flagged `tax_date` in the panel that is not a month-end or month-start.

The baseline is every remaining day. FOMC decision days (meeting end dates plus unscheduled meetings, from
repo-market-model's `metadata/fomc_calendar.json`) and days on which IORB changed are dropped from both events and
baseline, so policy news is not mistaken for repo pressure.

## Statistics

For each regime, event and outcome:

- **signed effect:** mean change on event days − mean change on baseline days;
- **size effect:** mean |change| on event days − mean |change| on baseline days (does the market move *more*,
  in either direction?).

**The main comparison** is the difference in differences `scarce_2025_26 − floor_2021_23` on `month_end`, for the
size effect, across the four main outcomes: the 10-year yield, VIX, Baa − 10y, and CP − IORB. The 2018–19 regime is the
replication: an effect claimed for 2025–26 should have the same sign there.

Every figure carries a 95% percentile bootstrap interval: 5,000 draws, event days and baseline days resampled
separately within each regime, seed 20261026. Event days are about a month apart, so resampling them independently
is defensible. Baseline days are serially dependent in |change| (volatility clusters), so their interval is somewhat
too narrow; with thousands of baseline days against about 20 events, the event side dominates the width anyway.

A secondary check is the pass-through slope: an OLS regression of each daily market change on the daily spread change,
by regime, over all non-excluded days.

## What this study can and cannot show

- **Exploratory.** There are 11 outcomes × 5 events × 3 regimes, so some intervals will exclude zero by chance. The
  result page counts how many do, against the roughly 5% expected under no effect. Only the main comparison is a test.
- **Small samples.** Each regime has about 20–36 month-ends and 7–12 quarter-ends, so only a large effect would show.
- **Daily closes.** Effects inside the day, or in markets FRED does not carry (swap spreads, the cash–futures basis,
  the MOVE index, funding-sensitive FX swaps), are invisible here.
- **Disclosed beforehand:** while scoping this project, one cross-market look was taken. On each year's
  top-5%-spread days, the 4-week bill yield showed no consistent move.

## Amendments after the first run (26 October 2026)

The first run showed two defects in the design as written. Both fixes were made after its numbers had been seen, so
they are post hoc and are reported as such:

1. **The 30-day AA financial CP rate is mostly missing.** FRED publishes no rate on days with too few trades, which is
   most days from 2020 onwards (69–75% missing in 2024–26). The CP leg of the main test rested on 3 to 5 month-ends
   per regime. In the first run it gave +2.8 bp [0.6, 4.7], and that figure is void. The **overnight** AA financial CP
   rate (`RIFSPPFAAD01NB`, about 4% missing, i.e. holidays) replaces it in the main test. It is the unsecured
   counterpart of overnight repo, so it measures the nearest ring outward from repo, not markets as a whole. The 30-day
   series stays in the results as a secondary outcome.
2. **Minimum sample.** A regime-level cell is now reported only with at least 10 event days (the first run used 3).
   The ICE BofA spreads are reported for 2025–26 only, as the data section above already said. The first run had
   contrasted them against three floor-regime days.
