# Study 20: full allotment or bill purchases? And why repo now gets tight with more reserves — result

Design: [`docs/design-study-20-allotment-and-threshold.md`](../../docs/design-study-20-allotment-and-threshold.md),
committed before its new data was fetched or any of its measures computed. It uses study 17's data and month-end
measure:
- **jump `J`:** the spread on the last and first business days around a month-end, minus the median of business days
  6–15;
- **ordinary-day tightness `B`:** that median, in SOFR minus the top of the Fed's range.

Every figure is read from [`result.json`](result.json). Data to 23 October 2026.

## In one line

Repo gets tight when reserves fall to about a tenth of the federal debt held by the public, in 2018–19 and again in
2025–26. Measured that way the scarcity threshold has not moved: reserves have simply had to grow with the debt they
back. Since full allotment, month-end jumps have roughly halved while ordinary days got slightly tighter, not looser.
That points to the facility rather than the Fed's bill purchases, but the gap is not statistically clear yet.

## Part A: full allotment or the bill purchases?

Months of the 2025–26 scarce regime: 11 before full allotment (January–November 2025), 10 after (December 2025 –
September 2026).

| | Before | After | After minus before |
|---|---:|---:|---|
| Ordinary-day tightness `B` | −15.7 bp | −12.1 bp | **+3.6 bp** [−0.4, +7.4] |
| Month-end jump `J` | +9.5 bp | +4.9 bp | |
| Largest turn-day spread above the top of the range | 22 bp (31 Oct 2025) | 12 bp (31 Dec 2025) | |

**A1, did ordinary days loosen? No.** If anything they got tighter, by 3.6 bp. The interval just includes zero. The
bill purchases, sized by the New York Fed to keep reserves "ample" against rising Treasury balances, did not make
ordinary days visibly looser.

**A2, jumps at equal tightness: no detectable difference** (pre-set verdict). Holding `B` and quarter-ends fixed,
jumps after full allotment were 6.7 bp smaller, with an interval of [−12.3, +1.3] that includes zero. Ten months is
too few to be sure.

**Reading.** Ordinary days did not loosen, but the spikes shrank and the largest fell from 22 to 12 bp. That pattern
fits the facility capping the pressure points better than it fits more reserves. It is a direction, not a result.
Study 18's year-end test and more months will tell.

## Part B: why repo now gets tight with more reserves

Comparable months, those whose ordinary-day tightness lies in the range both scarce regimes covered (−21 to −5 bp):
15 in 2018–19 and 20 in 2025–26.

| Reserves as % of… | 2018–19 (median) | 2025–26 (median) | 2025–26 as % of 2018–19 |
|---|---:|---:|---:|
| Commercial-bank assets | 9.61 | 12.03 | 125.1% |
| GDP | 7.75 | 9.40 | 121.3% |
| **Federal debt held by the public** | **10.09** | **9.62** | **95.3%** |

**B1 verdict: the shift disappears under reserves as a share of federal debt held by the public.** Against bank assets
or GDP, repo got as tight in 2025–26 with a fifth to a quarter more reserves than in 2018–19. Against the government
debt that repo finances, the two scarce regimes look alike: about a tenth.

**Reading.** The amount of reserves the system needs seems to grow with the stock of Treasuries to be financed. Dealers
and hedge funds hold and fund those Treasuries in repo, and the cash for that comes ultimately from reserves. In the
comparable months, debt held by the public was $16.2 trillion (2018–19 median) against $30.9 trillion (2025–26), and
reserves $1.64 trillion against $3.05 trillion. Both roughly doubled, so "ample" now means about twice as many
reserves. This is a
description, not a cause: other measures were not tried, and the debt and reserves both trended over the same years.

## Limits

- **Ten months after full allotment,** and they overlap rate cuts and the clearing transition.
- **`B` captures the reserves channel only partly** (design). If the bill purchases calmed month-ends directly, A2
  credits the facility with some of that.
- **2019's ordinary-day tightness** was moved by the Fed's adjustments of the rate on reserves (study 17), so B1's 2019
  months are less cleanly comparable.
- **Three ratios, one match.** With more measures tried, one matching by chance becomes likelier. The design set these
  three in advance, and the match is close (95%), but a single descriptive match is not proof.
