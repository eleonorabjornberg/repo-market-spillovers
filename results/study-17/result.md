# Study 17: why 2025–26 month-ends are milder than 2018–19's, and what drove the slow creep — result

Design: [`docs/design-study-17-milder-spikes-and-creep.md`](../../docs/design-study-17-milder-spikes-and-creep.md),
committed before any data was fetched. Section 3 holds checks added **after** the first results. They are labelled post
hoc and decide nothing. Every figure is read from [`result.json`](result.json). Data to 23 October 2026.

The spread here is SOFR minus the top of the Fed's target range, in bp. A month-end jump is the mean of the spread on
the last business day of the month and the first of the next, minus its median on business days 6–15 of the month.

## In one line

Ordinary month-ends were no milder in 2025–26 than in 2018–19. What changed is the extremes. Quarter-ends, and above
all year-end 2018, spiked far higher before the Fed's standing repo facility existed. Since then, the worst turn day
reached 22 bp above the facility's rate, against 65 bp in 2018–19: a ceiling that leaks but holds back the extremes.
The slow creep from 2022 to 2025 goes mostly with the draining of the Fed's reverse repo facility, then of reserves.

## 1. The milder spikes (Part A, pre-registered)

**A1, the gap: not confirmed.** By this measure, month-end jumps were about the same in both scarce regimes:

| | Months | Mean jump |
|---|---:|---:|
| Scarce 2018–19 | 15 | +6.9 bp |
| Floor 2021–23 | 29 | +1.0 bp |
| Scarce 2025–26 | 17 | +6.2 bp |
| **2025–26 minus 2018–19** | | **−0.6 bp** [−3.9, +2.8] |

**A2, at equal tightness: scarcity accounts for it** (the 2025–26 term is +0.0 bp [−5.0, +4.3]). Compared at the same
ordinary-day tightness, 2025–26 jumps are the same size as 2018–19's. Both regimes covered the same range of
ordinary-day spreads (−21 to −1 bp, and −21.5 to −5 bp). Within them, the size of the jump hardly depends on how tight
ordinary days were (+0.13 per bp [−0.35, +0.54]).

**Measured by reserves, the two regimes do not overlap.** Reserves were 8.6–12.3% of bank assets in 2018–19 and
11.4–14.4% in 2025–26, so they cannot be compared at the same level of reserves. Repo reached the same tightness with
noticeably more reserves in 2025–26. The level at which reserves become scarce has risen.

**A3, the ceiling (descriptive).**

| | 2018–19 | 2025–26 |
|---|---:|---:|
| Turn days with SOFR above the top of the range | 33.3% | 5.9% |
| Largest turn-day spread above the top (months kept by the design) | 26 bp | 12 bp |
| Median residual / 90th percentile | −0.9 / +5.2 bp | −0.8 / +8.9 bp |

In 2025–26, turns with standing repo facility take-up of at least $1bn jumped +12.2 bp (3 turns), against +5.0 bp
without (14). The facility is used when pressure is high, as it should be. It does not stop the jump.

**A4, clearing (descriptive): nothing visible.** Within 2025–26, a higher sponsored share of cleared repo is not
associated with smaller jumps: −0.11 bp per point [−1.08, +0.73], 17 months.

## 2. The slow creep (Part B, pre-registered)

Yearly means, in bp, with reserves and ON RRP take-up as % of bank assets:

| | 2018 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SOFR − top of range | −4.4 | −8.1 | −21.1 | −21.5 | −19.1 | −16.9 | −12.9 | −11.4 |
| SOFR − IOER/IORB (the one-pager's gauge) | −0.6 | +6.6 | −8.8 | −11.5 | −9.1 | −6.9 | −2.9 | −1.4 |
| Reserves | 11.4 | 9.0 | 17.9 | 15.0 | 14.1 | 14.4 | 13.2 | 11.8 |
| ON RRP | 0.0 | 0.0 | 3.2 | 8.8 | 7.6 | 1.7 | 0.4 | 0.0 |

**B1, the two drains: they account for the creep** (82%). From 2022 to 2025 the spread rose 8.7 bp. The fitted model
attributes 7.1 bp of it to the two drains: 4.8 bp to the fall in ON RRP and 2.3 bp to the fall in reserves. As the
design warned, the split between the two is unreliable, because they trended together. Their combined account is the
result. The order is clear from the table, though. Money funds' spare cash left the Fed's reverse repo facility first
(2022–24), and only once it was nearly gone did falling reserves take over (2025–26).

**B2, the 2018–19 relationship: not informative** (post hoc judgement). The design fitted the spread on reserves over
2018–19 and predicted 2025–26. The fit has the wrong sign: more reserves, tighter repo (+0.97 bp per point). Its verdict
("looser than reserves predict", −4.7 bp [−8.2, −0.9]) should not be read. The design assumed that SOFR minus the top of
the range is unaffected by the Fed's 2018–19 adjustments to the rate on reserves. That was wrong: the adjustments were
made to pull market rates down within the range, and they did. So within 2018–19 the spread moved with policy as well
as with reserves.

## 3. Post hoc: where the gap is (decides nothing)

The design dropped months in which the target range changed. In 2018 that removed three of the quarter-ends (June,
September, December), because the Fed raised rates in those months. Keeping every month, which is safe for this
measure because SOFR moves with the range:

| | 2018–19 | 2025–26 | Difference |
|---|---:|---:|---|
| All month-ends (21 each) | +10.1 bp | +7.3 bp | −2.9 [−9.7, +2.2] |
| Quarter-ends (7 each) | +17.7 bp (median 14.0) | +7.9 bp (median 8.0) | −9.9 [−26.4, +2.1] |
| Other month-ends (14 each) | +6.4 bp | +7.0 bp | +0.6 [−3.0, +4.6] |

Ordinary month-ends are the same. The gap the one-pager shows sits in quarter-ends, and above all in one: **year-end
2018, +62 bp**. In 2018–19 SOFR reached 65 bp above the top of the range (2 January 2019). In 2025–26 the largest
turn-day spread was 22 bp above it (31 October 2025). The 2018–19 quarter-ends are also mixed. September and December
2019 came after the Fed began its own repo operations, and December 2019 jumped only +0.5 bp.

**Reading.** This fits a ceiling more than anything else: the standing repo facility, in place since July 2021,
removes the extreme spikes but leaks on reporting dates. Ordinary month-ends, which do not reach the ceiling, are as
large as before. Less scarcity does not fit, because at equal tightness the jumps are the same. Clearing shows no
effect within 2025–26. With 7 quarter-ends a side and one dominant outlier, none of this is a test. It is where to
look.

**For the one-pager.** Chart A's 2018–19 month-end effect is probably lifted by year-end 2018. Checking it in
repo-market-model without that date, or with quarter-ends apart, would show whether the "milder in 2025–26" reading
holds. This project does not touch the parent model's results.

## Limits

- **Two scarce regimes, about 20 months each,** that differ in many ways at once.
- **One outlier drives the quarter-end gap.** The year-end 2018 spike coincided with a stock-market sell-off and the
  Fed's December hike.
- **The facility series** (`RPONTSYD`) counts all the Fed's overnight repo operations. In 2019 these were emergency
  operations, not the standing facility.
- **The design's comparability assumption failed for B2,** as explained above. The same Fed adjustments also moved
  ordinary-day tightness `B` in 2019, so A2's comparison at equal tightness is less clean for 2019 than for 2018.
- **Monthly averages** smooth over the days that matter.
