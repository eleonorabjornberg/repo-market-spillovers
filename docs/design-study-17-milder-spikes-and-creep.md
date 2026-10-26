# Study 17: why 2025–26 month-ends are milder than 2018–19's, and what drove the slow creep

Written on 26 October 2026, before this study's data was fetched. Requested by Eleonora after comparing the project
with the repo-market-model one-pager (October 2026).

The one-pager reports two things this study tries to explain:
- **Chart A:** a month-end added +5.8 bp to SOFR − IORB in 2018–19, +0.3 bp on the floor and +4.3 bp in 2025–26.
  Reserves were scarce in both 2018–19 and 2025–26, yet the effect was milder in 2025–26.
- **Chart B:** the yearly average spread crept up from −11.6 bp (2022) to −9.1, −6.9 and −2.9 bp (2025) as quantitative
  tightening drained the system.

**Disclosed beforehand.**
- **Seen:** the one-pager's figures above, and study 01's first stage on the same regimes. There, the extra month-end
  rise over the floor was +15.2 bp in 2018–19 and +5.0 bp in 2025–26, measured differently.
- **General knowledge, not checked against data:**
  - reserves were roughly twice as large in 2025–26 as in 2018–19 relative to bank assets, so the two periods may not
    overlap on that measure;
  - the Standing Repo Facility (SRF) has offered repo at the top of the target range since July 2021;
  - the interest rate on reserves was adjusted against the target range three times in 2018–19;
  - the Fed began buying bills to keep reserves ample in late 2025.

## Questions

**Part A, the milder spikes.** Three explanations, which are not exclusive:
- **(a) less scarcity:** reserves were simply less scarce in 2025–26;
- **(b) the SRF ceiling:** the facility caps the spikes;
- **(c) clearing:** sponsored clearing lets dealers net trades, so month-ends strain balance sheets less.

**Part B, the creep.** How much of the rise from 2022 to 2025 goes with the draining of reserves, and how much with
the draining of the Fed's overnight reverse repo facility (ON RRP)? And does the 2018–19 relationship between reserves
and the spread describe 2025–26?

## Data (FRED unless stated; daily unless stated)

- **Rates:**
  - `SOFR`, from 3 April 2018;
  - `DFEDTARU`, the top of the target range;
  - `IOER` to 28 July 2021, and `IORB` from 29 July 2021.
- **Reserves and the Fed's facilities:**
  - `WRESBAL`, reserve balances, weekly;
  - `TLAACBW027SBOG`, total assets of commercial banks, weekly;
  - `RRPONTSYD`, ON RRP take-up;
  - `RPONTSYD`, the Fed's overnight repo operations, which include SRF take-up.
- **Clearing:** FICC sponsored repo and reverse repo volumes (`FICC-SPONSORED_REPO_VOL`, `FICC-SPONSORED_REVREPO_VOL`)
  and total DVP repo volume (`REPO-DVP_TV_TOT-P`), from the OFR, as in study 07.

## Definitions

- **The spread, main measure:** `S` = SOFR − top of the target range, in bp. It is comparable across both eras,
  because it is unaffected by the 2018–19 adjustments of the rate on reserves. Since July 2021 it is also SOFR minus
  the SRF's minimum bid rate. SOFR − IOER/IORB, the one-pager's gauge, is reported beside it.
- **Scarcity by quantity:** `R` = reserve balances over commercial-bank total assets, in %, from the latest week on or
  before the day.
- **The regimes** are study 01's: `scarce_2018_19` (3 April 2018 – 31 December 2019), `floor_2021_23`, and
  `scarce_2025_26` (from 1 January 2025).
- **Month-end jump** for month m: `J_m` = the mean of `S` on m's last business day and the next month's first
  business day, minus the median of `S` over business days 6–15 of m.
  - A month is dropped if the target range changed between its sixth business day and the next month's first
    business day.
  - A month is a quarter-end if it is March, June, September or December.
- **Ordinary-day tightness** for month m: `B_m` = the median of `S` over business days 6–15 of m. This is the market's
  own reading of scarcity: how close repo trades to the ceiling on ordinary days.

## Part A: tests and what would count

**A1, the gap (reported).** The mean `J` by regime, and 2025–26 minus 2018–19, with a 95% interval from a bootstrap
that resamples months within each regime (2,000 draws, seed 20261028).

**A2, at equal tightness: is it more than scarcity?**
- **Model.** Over the months of both scarce regimes: `J_m = a + b·B_m + c·quarter-end_m + d·[2025–26]_m`.
- **Interval.** For `d`, from the same bootstrap.
- **Overlap condition.** The comparison needs at least 5 months of each regime within the range of `B` both regimes
  cover. Otherwise the verdict is **cannot separate**.
- **Verdicts:**
  - **scarcity accounts for it** if `d`'s interval includes zero;
  - **something beyond scarcity damps the spikes** if its upper bound is below zero;
  - **2025–26 spikes are larger at equal tightness** if its lower bound is above zero.
- **The same model with `R` in place of `B`** is reported. If the regimes do not overlap on `R`, as expected, it is
  reported as **no overlap**, together with each regime's range of `R`. A shift in the reserve level at which spreads
  rise is then itself a finding.

**A3, the ceiling (descriptive, no verdict).** The SRF caps the tail; netting or scarcity would shift the whole
distribution. Reported by regime:
- the share of turn days (last and first business days) with `S` > 0, that is, SOFR above the top of the range;
- the largest `S` on a turn day;
- the 50th and 90th percentiles of the A2 residuals, without the 2025–26 term.

For 2025–26, also the mean `J` on turns with SRF take-up of at least $1bn against turns with less.

A gap in A2 concentrated in the upper tail, with similar medians, is **consistent with a ceiling**. A gap throughout
the distribution is **consistent with less strain on balance sheets**. Neither is proof.

**A4, clearing (descriptive, no verdict).** Within 2025–26, the model `J_m` on `B_m` and the sponsored share
(sponsored repo plus reverse repo over DVP volume, the month's mean), with its coefficient and interval. There are
about 20 months, so only a large effect could show.

## Part B: tests and what would count

**B1, reserves and ON RRP, 2021 onward.**
- **Model.** Over months from January 2021 to the latest: monthly mean `S` = a + b·R + c·Q, where `Q` is ON RRP
  take-up over bank assets (%).
- **Reported:** the change in mean `S` from 2022 to 2025, and how much of it `b·ΔR` and `c·ΔQ` account for.
- **Verdict.** **The two drains account for the creep** if the fitted change is at least 75% of the actual change.
  Otherwise, **something else contributed**.
- **Caveat.** `R` and `Q` trend together, so the split between them is unreliable. Only their combined account is
  tested.

**B2, did the 2018–19 relationship hold?**
- **Model.** Fit monthly mean `S` = a + b·R on the 2018–19 months.
- **Prediction.** The mean residual for 2025–26 months whose `R` lies inside 2018–19's range, with a bootstrap
  interval. Fewer than 5 such months means **cannot tell**.
- **Verdict (if testable).** If the residual's lower bound is above zero, **repo was tighter than reserves predict**:
  more demand for reserves or for repo funding. If its upper bound is below zero, it was looser.
- **Reported in any case,** without a verdict: the 2018–19 fit's prediction for 2025–26's actual `R`, with each
  regime's ranges. This shows how far the threshold for scarcity has moved.

## Limits

- **Two scarce regimes.** Every comparison between them rests on two periods that differ in many ways at once: the
  SRF, clearing, the size of the Treasury market, bank regulation, hedge-fund leverage. The tests can separate
  scarcity from "something else". Within "something else" they can only describe, not prove.
- **About 20 months each.** Only large effects show.
- **The market's own tightness `B`** is partly the outcome of the same forces. If clearing or the SRF calmed ordinary
  days too, A2 understates them.
- **Monthly averages** smooth out the days that matter for Part B.
- **Nothing here is a claim about repo-market-model's forecasts.** The one-pager's figures are development evidence,
  and this study does not re-score them.
