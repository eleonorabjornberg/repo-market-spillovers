# Study 05: does repo stress spread outward, beyond calendar days? (H3) — result

Design: [`docs/design-study-05-spillback.md`](../../docs/design-study-05-spillback.md), committed before the run. Every
figure is read from [`result.json`](result.json). The daily swap series built here is committed as
[`swap_rates_daily.csv`](swap_rates_daily.csv). DTCC keeps only a rolling two-year window, so these numbers will
outlive the files they came from.

## Verdict: H3 not supported

Neither part meets its rule.

## Part A: repo shocks the calendar does not explain

**Shocks:** days with SOFR − IORB up at least 5 bp that are not calendar, FOMC or IORB-change days.
- **2018–19:** seven days, including 2019-09-12 and 2019-09-24 around the September 2019 spike.
- **2025–26:** seven days: 2025-04-08, 2025-06-25, 2025-07-25, 2025-10-21, 2025-12-26, 2026-05-26, 2026-07-13.
- **The floor regime:** none.

**Outcome:** the change over the shock day and the next.

| OFR financial stress index (composite) | Estimate | 95% interval |
|---|---:|---|
| **Main:** 2025–26, shock days − other days | −0.11 | [−0.36, +0.05] |
| Replication: 2018–19 | +0.02 | [−0.19, +0.25] |
| Placebo, shocks moved 10 days later | +0.07 | [−0.13, +0.23] |

After the repo shocks of 2025–26, broad market stress did not rise; if anything it eased slightly.

**Secondary outcomes:** 4 of 32 intervals exclude zero, against about 1.6 by chance.
- **2018–19:** larger 10-year moves (+2.8 bp in size [+0.1, +5.9]) and larger bill moves (+3.4 bp [+0.4, +7.0]).
- **2025–26:** Baa − 10y rose **+1.3 bp** [+0.4, +2.2] over the two days, with smaller-than-usual moves in size
  (−1.2 bp [−2.0, −0.4]). Credit widened by a little, consistently.

That last one is the only hint of spillback in the current regime. It is one of 32 comparisons on 7 days, so it is a
lead to watch, not a finding.

## Part B: swap spreads, November 2024 – September 2026

**Data:** daily 2-year and 10-year SOFR swap rates, the notional-weighted median of 98,052 qualifying trades over 516
days of DTCC's public reports. The swap spread is the swap rate minus the Treasury yield.
- **The 10-year spread** averaged −46 bp, ranging from −70 to −33.
- **April 2025 checks out:** it widened from −45 bp (1 Apr) to **−61 bp (10 Apr)**, matching the swap-spread collapse
  reported at the time, then recovered.

| Test (2025–26) | 10-year | 2-year |
|---|---|---|
| Pass-through: Δ swap spread per bp of Δ(SOFR − IORB) | −0.04 [−0.14, +0.06] | +0.05 [−0.14, +0.25] |
| Month-end rank correlation (n = 20) | +0.02 | +0.14 |

The hypothesis predicted a negative slope and a negative correlation: repo pressure cheapening Treasuries against
swaps. The slope's sign is right, but it is about zero, and month-end pressure is unrelated to swap spreads.

## What this means for the question

Read together with study 01 (calendar days), H3 now has its broadest public-data test, and the answer is the same:
**repo pressure in 2025–26 has not spread to wider markets at daily frequency.** That holds for broad stress, yields,
credit, equities, the dollar, and even swap spreads, the price most exposed to dealers' balance sheets.

The single hint is a 1.3 bp rise in Baa spreads after the seven largest non-calendar repo shocks.

April 2025 shows the direction again. Swap spreads widened by 16 bp in a week while repo moved 7 bp: the bond market's
stress reached swaps, and repo followed modestly. Repo did not lead.

## Limits

- **Seven shocks per regime:** a null is weak.
- **Part B has no comparison regime.** DTCC's window starts in November 2024.
- **Prints:** swap rates come from trades, not quotes. The 2-year series has two outlying prints: −96 bp on
  2026-10-21, outside the panel's dates, and −55 bp on 2026-08-03. Neither affects the 10-year main test.
