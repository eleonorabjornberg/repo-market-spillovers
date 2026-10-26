# Study 10: three prospective tests — the clearing deadlines, the credit lead, and the chain under stress

Written on 26 October 2026, before any of the data these tests score exists. The analysis code,
`scripts/study_10_prospective.py`, is committed with this design and frozen with it. The monthly watch workflow runs
it, and each test reports "pending" until its data is complete.

**Why prospective.** Every earlier study looked back at data that had already happened, and some of it had been seen.
These three tests are set before their outcomes happen, so their results cannot be shaped by hindsight. This is the
strongest evidence the project can produce.

**Already known when this was written:**
- the comparison dates (all before October 2026) and their values;
- the October 2026 rise in the OFR stress index (from −2.5 in September to −1.5 on 22 October), which falls before
  every test window below.

**Data:** the watch's sources (`scripts/watch.py`):
- SOFR and IORB, FRED, from which SOFR − IORB in bp;
- Baa − 10y, FRED;
- the 10-year SOFR swap spread, `results/watch/swap_daily.csv`, from DTCC;
- the OFR financial stress index;
- FICC sponsored reverse repo and cleared DVP volume, OFR;
- hedge-fund repo, Form PF via OFR;
- leveraged funds' Treasury futures positions, CFTC.

**Non-calendar day:** a business day that is not among the first two or last two business days of its month, not on
day 13–17 of its month, and not a day on which IORB changed. This approximates studies 01–05's calendar without
repo-market-model's panel, which the watch does not read.

## Part A: the clearing deadlines

**Deadlines:**
- **D1, 31 Dec 2026:** cash Treasury trades must be cleared. It is also year-end.
- **D2, 30 Jun 2027:** repo must be cleared. It is also a quarter-end.

**Comparators:** each deadline is compared with the same calendar day in the two previous years, so year-end and
quarter-end effects net out:
- D1 against 31 Dec 2024 and 31 Dec 2025;
- D2 against 30 Jun 2025 and 30 Jun 2026.

**A1, migration (D2):** sponsored reverse repo's share of DVP volume, the mean of Jul–Sep 2027 minus the mean of
Apr–Jun 2027.
- **Migration jump** if at least +3 pp.
- For D1 the same is reported (Jan–Mar 2027 against Oct–Dec 2026), but decides nothing, since D1 covers cash trades,
  not repo.

**A2, relief on the day:** Δ(SOFR − IORB) on the deadline day (from the previous business day), against the same on
each comparator. Relief if it is smaller than both by at least 2 bp.

**A3, disruption around the day:** the standard deviation of daily Δ(SOFR − IORB) on non-calendar days within 10
business days either side of the deadline, against the same around each comparator. Disruption if it exceeds both by
at least 50%.

**A4, swap spreads:** the change in the 10-year swap spread from 20 business days before to 20 after the deadline,
against the same around each comparator. Relief if it is above both (Treasuries cheapened less, or richened).

**Verdict for each deadline:**
- **relief** if A2 and A4 both show relief and A3 shows no disruption;
- **disruption** if A3 shows disruption and A2 does not show relief;
- **mixed** if A3 shows disruption together with relief on A2 or A4;
- **no visible effect** otherwise.

A1 is reported beside it.

**A5, what is left outside clearing (descriptive):** quarterly mean sponsored reverse repo volume divided by hedge-fund
repo borrowing, for Q2 2026, Q2 2027 and Q3 2027. The two are measured differently, so only the direction is read.

**When:**
- D1's verdict is computed once data runs to 20 business days after 31 Dec 2026 (end of January 2027);
- D2's once it runs to the end of September 2027.

## Part B: the credit lead, tested forward

Study 05 found Baa − 10y rose 1.3 bp [+0.4, +2.2] over the two days after non-calendar repo shocks in 2025–26: one of
32 comparisons on 7 days. This tests it on new days only.

- **Days:** non-calendar business days from 2 November 2026.
- **Shock:** Δ(SOFR − IORB) of at least 5 bp.
- **Outcome:** the change in Baa − 10y from the close before the shock day to the close after it, in bp.
- **Test:** mean outcome on shock days minus on other eligible days; 95% percentile bootstrap, 5,000 draws, seed
  20261101.
- **When:** run once 10 shock days have accumulated, or on 31 Dec 2028 if fewer have (then reported with its n).
- **Confirmed** if the difference is positive with its interval excluding zero; **not confirmed** otherwise.

## Part C: the chain under stress

Eleonora's concern: hedge-fund repo, sponsored repo and the basis trade move together (r = 0.89–0.97 in levels,
2021–26), which looks like one crowded trade funded overnight. If the chain is fragile, the first real stress should
show it.

**Stress onset:** the first business day from 2 November 2026 on which the OFR financial stress index is at least 1.0
above its value 20 business days earlier (study 06's mechanical definition).

**Window:** 5 business days before the onset to 40 after.

**Measures:**
- **C1:** the highest SOFR − IORB on a non-calendar day in the window. Strained if at least 10 bp.
- **C2:** leveraged funds' net Treasury futures short, its lowest weekly value within 8 weeks after the onset against
  its last value before it. An unwind if it falls by at least 10%.
- **C3:** the 10-year swap spread, its lowest value in the window minus its value 5 business days before the onset.
  Reported.

**Verdict:**
- **the chain gave way** if C1 is strained and C2 shows an unwind;
- **strained** if one of them holds;
- **held** if neither.

The same measures are computed now for April 2025 as a reference (onset 10 March 2025 by the same definition): they
describe a stress the chain is known to have absorbed.

**When:** computed once the window is complete. If no onset has occurred by 31 Dec 2028, it is reported as "no stress
event".

## Limits

- **A single deadline is one event.** Anything else happening that day or week moves the measures; the comparators
  net out only the calendar.
- **The non-calendar rule approximates** the earlier studies' calendar.
- **Part C scores one episode.** Its verdict describes that episode, not the chain in general.

## Erratum (26 October 2026, after this design was committed, before any scored data existed)

A5 divides FICC *sponsored reverse repo* by hedge funds' repo borrowing. Per the OFR's definitions, sponsored reverse
repo is mostly money funds *lending* cash. The hedge-fund leg is sponsored *repo*, mostly hedge funds borrowing cash.
A5 therefore does not measure "what is left outside clearing" for hedge funds. It is kept unchanged, and the
correctly-legged ratio is reported beside it as `A5_erratum_sponsored_repo_over_hf_repo`. A5 is descriptive and decides
no verdict, so no test changes. A1 measures money funds' side of the migration, which sponsored reverse repo is right
for, and is unaffected.
