# Study 19: who pays above the facility's line, and did they use the facility? — result

Design: [`docs/design-study-19-who-pays-above-the-line.md`](../../docs/design-study-19-who-pays-above-the-line.md),
committed before the data was fetched. Section 3 was added **after** the first results, and is labelled post hoc.
Every figure is read from [`result.json`](result.json). Data: the New York Fed's reference rates and standing repo
operations, 29 July 2021 – 23 October 2026. One day (5 August 2021) has no percentiles and is left out.

"The line" is the standing repo facility's rate, the top of the Fed's target range. A "breach day" is a day on which
SOFR's 99th percentile closed above it.

## In one line

Since full allotment, the top of the market pays above the Fed's line mainly in cleared bilateral repo, where dealers
lend to clients such as hedge funds, not in tri-party repo. On most such days nobody used the facility. Since April
2026, every breach has been a small premium of 1–5 bp in that segment, on days when tri-party rates sat well below the
line and the facility was idle. The ceiling holds for the firms that can reach it. The rest pay a dealer's markup on
top.

## 1. Where are the expensive trades? (Q1, pre-registered)

| | Before full allotment (Jul 2021 – 10 Dec 2025) | After (11 Dec 2025 – 23 Oct 2026) |
|---|---:|---:|
| Days | 1,089 | 217 |
| Breach days | 79 | 35 |
| … with tri-party's (TGCR) 99th percentile also above the line | 27 (34.2%) | **8 (22.9%)** |
| … with BGCR's (tri-party + GCF) also above | 44 (55.7%) | 13 (37.1%) |
| Mean gap, SOFR's 99th percentile minus TGCR's, on breach days | 9.7 bp | 8.2 bp |
| Mean height of SOFR's 99th percentile above the line | 9.3 bp | 5.4 bp |
| **Verdict** | mixed | **outside tri-party (in DVP)** |

After full allotment, the expensive trades sit mostly in the segment SOFR adds to the other two: cleared bilateral
(DVP) repo. Before, they were spread more widely. The 22.9% is just inside the pre-set threshold of 25%.

## 2. Was the facility used on breach days? (Q2, pre-registered)

Median take-up was $0bn on breach days in both periods, as it was on other days. **Verdict: largely unused when the top
of the market paid more**, in both periods. The mean is higher: $3.3bn before and $6.1bn after full allotment. A few
days carry most of the take-up, the largest $74.6bn on 31 December 2025. On breach days after full allotment, most of
the take-up came in the morning operation (closing 08:30, $162bn in total) rather than the afternoon one (13:45, $52bn).

The design's "share of breach days with any take-up" is not informative. Many days show token amounts of a few
million dollars, which is why section 3 uses $1bn.

## 3. Post hoc: two kinds of breach day (decides nothing)

| After full allotment | Days | SOFR's 99th above the line | TGCR's 99th minus the line | TGCR also above | Mean take-up |
|---|---:|---:|---:|---:|---:|
| Take-up of at least $1bn | 10 | +11.1 bp | +2.3 bp | 6 of 10 | $21.4bn |
| Take-up below $1bn | 25 | +3.1 bp | −4.8 bp | 2 of 25 | $0.01bn |

**Pressure days.** The first ten run from 15 December 2025 to 15 April 2026: the year-end, early January, and the
mid-month Treasury settlement and tax dates. They are market-wide: tri-party is at or above the line too, and the
facility is used heavily.

**Quiet days.** The other 25 run to 31 August 2026, and all breaches since 15 April are of this kind. They are a small
premium, 1–5 bp, in cleared bilateral repo, while tri-party trades 5–9 bp below the line and no one uses the facility.
Before full allotment the same split holds: 25 pressure days and 54 quiet ones.

**Reading** (not tested). Dealers can borrow from the facility at the line; their clients cannot. On quiet days,
dealers fund themselves below the line in tri-party, so they have no reason to go to the Fed. The few basis points
above the line in cleared bilateral repo are what dealers charge clients, such as hedge funds, for their balance sheet.
The Fed's ceiling caps dealers' funding. It does not cap that markup. This fits the "eligible firms only" reading of
the facility, but the data show where expensive trades happen, not who did them.

## Limits

- **Daily data:** this study cannot see when within a day the expensive trades happen against the two operation times.
- **Percentiles are volume-weighted,** so a shift in the mix between segments can move them.
- **Counterparties are not observed.** "Hedge funds pay the premium" is a reading.
- **35 breach days after full allotment,** and the 25% threshold was only just met.
