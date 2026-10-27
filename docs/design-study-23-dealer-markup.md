# Study 23: the dealer markup as a daily series

Written on 27 October 2026, before this study's new data was fetched. Study 19 found that since full allotment, the
expensive trades above the standing repo facility's rate sit in cleared bilateral repo, as a small premium over
tri-party on quiet days. It read this as a markup dealers charge their clients. This study measures the premium every
day since SOFR began and asks when it widens.

**Already known:** study 19's breach-day figures. On breach days after full allotment, SOFR's 99th percentile
averaged 8.2 bp above tri-party's (9.7 bp before). No full daily series has been computed.

## The series

**Markup** = SOFR's 99th percentile minus TGCR's 99th percentile, in bp, every day from 2 April 2018 (New York Fed
reference rates). A secondary version uses the 75th percentiles, the middle of the expensive side.

## Questions and what would count

- **Q1, balance-sheet dates.** The mean markup on quarter-end turn days (the last business day of March, June,
  September and December and the next business day) minus all other days, with a bootstrap interval resampling days
  within each year (2,000 draws, seed 20261031). It **widens at quarter-ends** if the lower bound is above zero.
  Year-ends are reported separately, without a verdict.
- **Q2, full allotment.** The mean markup on non-calendar days (study 10's definition) from 11 December 2025, minus the
  same over 2025 before then. Reported with its interval, no verdict, since full allotment caps dealers' funding, not
  the markup.
- **Q3, sponsored clearing.** The monthly mean markup on non-calendar days against the sponsored share of cleared repo
  (FICC sponsored repo plus reverse repo over DVP volume, OFR), 2018–2026: a correlation with a block bootstrap by
  year. It **narrows as sponsored clearing grows** if the upper bound is below zero. That would fit the idea that
  clearing lets dealers net and charge less.
- **Reported:** yearly means, and the series on the watch as a weekly reading.

## Limits

- **Percentiles are volume-weighted** across segments. A change in the mix can move the gap without any trade's price
  changing.
- **Counterparties are not observed.** "Markup to clients" is the reading from study 19, not a measurement.
- **Q3 is a time trend against a time trend.** Sponsored clearing grew alongside many other changes.
