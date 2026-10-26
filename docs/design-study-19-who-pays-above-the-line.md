# Study 19: who pays above the facility's line, and did they use the facility?

Written on 26 October 2026, before this study's data was fetched. It follows study 17's addendum:
- since full allotment (11 December 2025), SOFR has not closed above the standing repo facility's rate in 2026;
- SOFR's 99th percentile has, on about one day in eight.

The question is why the top of the market still pays more than the Fed's own offer.

**Disclosed beforehand.**
- **Seen:** the study 17 addendum counts for SOFR and its 99th percentile against the line, by period, and the 2025
  year-end figures from study 18. These are SOFR 12 bp and its 99th percentile 25 bp above the line on 31 December
  2025, with $74.6bn taken up at the facility. Also the shape of one operation record from the Markets API.
- **Not seen:** any tri-party (TGCR) or broad general collateral (BGCR) percentile, and facility take-up on any other
  day.

## Background: what each rate covers

- **TGCR:** tri-party repo, where money funds lend and dealers borrow.
- **BGCR:** tri-party plus FICC's GCF segment.
- **SOFR:** BGCR plus cleared bilateral (DVP) repo, where dealers lend to hedge funds and other clients, much of it
  sponsored.

If the expensive trades sit in DVP, SOFR's 99th percentile rises above the line while TGCR's and BGCR's do not.

**Who can use the facility.** Under the New York Fed's statement of 10 December 2025, only the facility's eligible
counterparties can, at two fixed operation times a day. Hedge funds are not among them.

## Data

- **New York Fed Markets API:** `/api/rates/secured/all/search.json`, giving SOFR, BGCR and TGCR with their 1st, 25th,
  75th and 99th percentiles and volumes. Also `/api/rp/results/search.json`, operation type Repo, for every standing
  repo operation. Both from 29 July 2021 to the latest.
- **FRED:** `DFEDTARU`, the top of the target range.

**The line** is the facility's rate, the top of the target range, as in study 18. A rate is above it if it closed
more than 0 bp above. Periods are split at 11 December 2025, the start of full allotment.

## Questions and what would count

**Q1, where are the expensive trades?** On the days when SOFR's 99th percentile is above the line ("breach days"),
how often are TGCR's and BGCR's 99th percentiles above it too?
- **Outside tri-party (in DVP)** if TGCR's 99th percentile is above the line on at most 25% of breach days.
- **Everywhere** if at least 75%.
- **Mixed** otherwise.

The same is reported for BGCR, for each period, with the mean gap between SOFR's and TGCR's 99th percentiles on breach
days.

**Q2, was the facility used on breach days?** Total take-up at the facility on each breach day, against all other days
in the same period.
- **Largely unused when the top of the market paid more** if median take-up on breach days is below $1bn. This fits
  the reading that the firms paying above the line could not, or did not, borrow from the facility.
- **Used** if the median is at least $5bn. Firms borrowed from it, and still some trades priced above it.
- **Mixed** otherwise.

Reported, without verdict: the share of breach days with any take-up, the largest take-up, and, after full
allotment, which of the two daily operations the take-up came in.

## Limits

- **Daily data.** SOFR and its percentiles cover a whole day's trades. Operations happen at two fixed times. This
  study cannot see trades priced before or after an operation within the day.
- **Percentiles are volume-weighted** across very different segments. A shift in the volume mix can move SOFR's 99th
  percentile without any single trade getting dearer.
- **Eligibility is not observed.** The data show where expensive trades happen, not who did them. "Hedge funds pay
  above the line" would be a reading, not a measurement.
- **About 200 days after full allotment,** and breach days are a fraction of those.
