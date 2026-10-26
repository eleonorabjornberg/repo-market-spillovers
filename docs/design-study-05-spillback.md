# Study 05: does repo stress spread outward, beyond calendar days? (H3)

Written on 26 October 2026, before this study was run. Plan: [`PLAN.md`](../PLAN.md), H3. Study 01 tested H3 on
calendar days and found nothing at daily closes. This study takes the two routes study 01 could not.

**Disclosed beforehand.** While scoping (study 01's follow-up probe), the non-calendar repo shock days were listed:
- 2018–19: seven days;
- 2025–26: 2025-04-08, 2025-06-25, 2025-07-25, 2025-10-21, 2025-12-26, 2026-05-26 and 2026-07-13.

For those days and March 2020, the 10-year, VIX, S&P 500 and OFR stress index were seen on t−1, t and t+1. They were
small on the 2025–26 days apart from April 2025. DTCC's swap data has not been examined beyond one day's file
(2025-04-08), opened to read its columns.

## Claim

**H3:** repo stress spreads into wider markets.

## Part A: repo shocks the calendar does not explain

**Shock day t:** a panel business day with Δ(SOFR − IORB) ≥ 5 bp that is not a calendar day (study 01's labels) and
not an FOMC or IORB-change day.

**Outcomes:** the change over days t and t+1 together (close of t−1 to close of t+1). The two-day window allows for
SOFR being published the morning after the trades it measures. Measured for:
- **Main:** the OFR financial stress index (composite), a single broad measure of "markets as a whole".
- **Secondary:** the 10-year and 2-year yields, VIX, S&P 500, Baa − 10y, the broad dollar, overnight financial CP −
  IORB, 4-week bill − IORB.

**Comparison:** shock days against all other eligible days in the same regime. Each outcome is reported signed (a
rise in the stress index is stress) and as size (|change|). Intervals are 95% percentile bootstrap: 5,000 draws, seed
20261028.

**Placebo:** shock dates moved 10 business days later.

**Main test:** `scarce_2025_26`, the stress index, signed. **Replication:** `scarce_2018_19`.

## Part B: swap spreads, November 2024 to September 2026

**Data:** DTCC's public swap reports (CFTC cumulative rates files, from November 2024; DTCC keeps a rolling window, so
the derived daily series is committed as `results/study-05/swap_rates_daily.csv` before the files roll off).

**Daily 2-year and 10-year SOFR swap rates:** the notional-weighted median fixed rate of trades that are:
- USD SOFR OIS (`UPI FISN` "NA/Swap OIS USD", underlier containing "SOFR");
- new trades (`Action type` NEWT, `Event type` TRAD);
- not part of a package;
- spot-starting (effective date at most 5 calendar days after execution);
- of tenor 1.9–2.1 years or 9.5–10.5 years;
- executed on that day (UTC date of the execution timestamp).

A day with fewer than 5 such trades gets no rate.

**Swap spread** = swap rate − Treasury yield of the same tenor (FRED `DGS2`, `DGS10`), in bp. A more negative spread
means Treasuries cheapen against swaps, the usual sign of dealer balance-sheet strain.

**Tests**, within 2025–26 only, since there is no floor-regime data to difference against:
1. **Pass-through:** OLS slope of the daily change in the 10-year swap spread on the daily change in SOFR − IORB, over
   all eligible days. The spillover hypothesis predicts a negative slope.
2. **Month-end dose:** the rank correlation, across month-ends, between the month-end change in SOFR − IORB and the
   change in the 10-year swap spread over t and t+1. Predicted negative.
3. **The same two for the 2-year swap spread**, as secondary.

## What counts

- **Part A supports H3** if the main test is positive with its interval excluding zero, the replication has the same
  sign, and the placebo's interval includes zero.
- **Part B supports H3** if the 10-year pass-through slope is negative with its interval excluding zero (2,000 day-level
  bootstrap draws) and the month-end rank correlation is negative.
- **H3: supported** if both parts support it; **partly supported** if one does; **not supported** if neither does.

## Limits

- **Part A has seven shocks per regime**, so only large effects show. A null is weak.
- **Part B has no comparison regime.** It shows co-movement within the current regime, not a change in it.
- **The swap rate is derived from trades**, not quotes. The median filters off-market prints, but thin days are
  noisy.
- **The CFTC's weekly basis-trade proxy** is too coarse to respond to single shock days, so it is not used here.
