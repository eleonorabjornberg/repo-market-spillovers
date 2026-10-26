# Study 04: do Treasury-market shocks spread into repo? (H2) — result

Design: [`docs/design-study-04-amplification.md`](../../docs/design-study-04-amplification.md), written before the run
and disclosing the exploratory probe it follows. Every figure is read from [`result.json`](result.json).
- **Shock (S1):** day t−1 in the top 5% of |Δ10y| within its regime.
- **Outcome (Y1):** the change in SOFR − IORB on the next day t. Calendar, FOMC and IORB-change days are excluded.
- **Intervals:** 95% bootstrap, 5,000 draws.

## Verdict: "supported for 2025–26 only" by the rule fixed in advance, but weak in substance

| Test | Estimate (bp) | 95% interval | Rule asks |
|---|---:|---|---|
| **Main:** 2025–26 − floor 2021–23 | **+1.11** | [+0.02, +2.24] | positive, excluding 0: **met** |
| Replication: 2018–19 − floor | −2.17 | [−5.17, +0.39] | same sign: **not met** |
| Placebo, shocks moved 10 days later | +0.93 | [−0.10, +1.95] | includes 0: met |
| Placebo, shocks moved 10 days earlier | +0.49 | [−0.42, +1.50] | includes 0: met |
| Dose–response: \|Δ10y\| × hedge-fund repo share | −0.004 | [−0.019, +0.013] | positive, excluding 0: **not met** |

The rule gives "supported for 2025–26 only". The record should also say why that verdict is weak:

1. **The main test is not new evidence.** Its definition is the probe's, and it reproduces the probe's number.
2. **The interval barely clears zero:** its lower end is +0.02 bp.
3. **The +10-day placebo is 84% of the main effect.** Its interval just includes zero, so the rule passes it, but an
   effect that nearly survives moving the shock two weeks is mostly about volatile *periods* in 2025–26, not about
   the shock *day*. Large bond moves cluster, and so do small repo rises.
4. **Nothing else lines up:**
   - the 2018–19 replication points the other way;
   - repo does not respond more when hedge-fund repo is larger;
   - the second shock measure (OFR volatility rises) gives −0.60 bp [−1.72, +0.78] in 2025–26.
5. **The direction is the wrong way round for forced selling.** In 2025–26, rallies (yields down) were followed by
   +1.27 bp [+0.07, +2.41], and sell-offs by +0.81 bp [−0.61, +2.54]. Leveraged funds forced to cut long Treasury
   positions would show up after sell-offs.

| Outcome, 2025–26 − floor | Estimate (bp) | 95% interval |
|---|---:|---|
| Y1 next-day spread | +1.11 | [+0.02, +2.24] |
| Y2 three-day spread | +1.48 | [−0.83, +3.97] |
| Y3 next-day 75th percentile of SOFR − IORB | +1.19 | [−0.15, +2.61] |

## The two episodes

**March 2020** (a run):
- the spread rose from −1 bp on 9 March to +10 bp on 12 March;
- after the 10-year moved 21 bp on 16 March, the spread reached **+44 bp on 17 March**, with its 75th percentile at
  +64 bp;
- it fell back to 0 the next day, when the Fed's repo operations and asset purchases took hold.

**April 2025** (a ripple):
- the 10-year rose 14 bp on 7 April, and repo rose 7 bp on 8 April, from −7 bp to 0 bp: back to IORB, not above it;
- by 11 April the spread was −7 bp again;
- the 75th percentile peaked at +10 bp on 9 April.

In 2025 the bond market's worst week in years moved repo by less than an ordinary quarter-end.

## What this means for the question

The idea that the bond market now drags repo with it gets little support at daily frequency. There is a small
next-day association in 2025–26, but it doesn't replicate, doesn't scale with leverage, and doesn't point the way
forced deleveraging would. The April 2025 stress test passed with a few basis points of repo pressure.

Three things could still be hiding it, so these are limits, not an all-clear:
- **The Fed's backstop:** the Standing Repo Facility now caps how far repo rates can rise.
- **The clearing migration (study 03):** cleared repo nets balance sheet and absorbs shocks better.
- **Daily data:** intraday stress is invisible here.

The first two are what study 07 watches.

## Limits

- **Few shocks:** about 24 per regime.
- **Common causes:** shared drivers (refundings, data surprises) can move both markets.
- **The panel** ends on 3 Sep 2026.
- **Dose–response** relies on Form PF's quarterly hedge-fund repo, carried to days.
