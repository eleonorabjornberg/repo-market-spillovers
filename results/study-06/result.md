# Study 06: would the chain have warned? (H4) — result

Design: [`docs/design-study-06-warning.md`](../../docs/design-study-06-warning.md), committed before the run, including
the list of stress events (Eleonora asked Claude to fix it). Every figure is read from [`result.json`](result.json).

**One deviation from the design.** The design put the scoring period's start at March 2017, by its rule "the first
month in which every indicator has 36 months of history". The FICC series has gaps, so its 36th observed month is
November 2017. The rule governs, so the period runs **November 2017 – September 2025** (95 months). It still holds named
events 6–13, as the design said.

## Verdict: cannot tell

Each month, each indicator is scored by its percentile within its own history up to that month (no look-ahead). A
month counts as positive if a named stress event begins in the next six months: 44 of 95 months. Events in the period:
- Volmageddon (Feb 2018);
- the Q4 2018 sell-off;
- the repo spike (Sep 2019);
- COVID (Feb 2020);
- the UK gilt crisis (Sep 2022);
- SVB (Mar 2023);
- the yen carry unwind (Aug 2024);
- the tariff shock (Apr 2025).

| Indicator | AUROC, named events | 95% interval | AUROC, mechanical events |
|---|---:|---|---:|
| **Chain:** leveraged funds' futures short / private Treasuries | **0.63** | [0.37, 0.84] | 0.60 |
| Chain: FICC share of money-fund repo | 0.60 | [0.29, 0.86] | 0.51 |
| Chain: hedge-fund repo / private Treasuries | 0.53 | [0.28, 0.77] | 0.52 |
| **Standard:** 10y − 3m curve (low = warning) | **0.58** | [0.34, 0.81] | 0.55 |
| Standard: NFCI | 0.52 | [0.19, 0.82] | 0.47 |
| Standard: Baa − 10y (high = warning) | 0.43 | [0.13, 0.71] | 0.36 |
| Standard: NFCI leverage subindex | 0.41 | [0.15, 0.70] | 0.33 |

An AUROC of 0.5 is a coin flip; 1.0 would be perfect warning.

**Main test:** best chain indicator (futures short) minus best standard (yield curve) = **+0.05** [−0.14, +0.24], and
+0.05 [−0.14, +0.23] on the mechanical events (31 OFR stress-index surges since 2010). Positive, but the interval spans
zero widely, so the design's verdict is "cannot tell".

## What this means for the question

**No indicator here, chain or standard, warned of stress reliably.** The best did modestly better than a coin flip,
and all the intervals cross 0.5. Two standard indicators did *worse* than chance over this period. Wide credit spreads
and high leverage readings did not precede these episodes; most of them hit from calm.

That is the fair answer to "will the repo market reveal the warning signs?", using the public data and the eight
episodes since 2017: **it might, a little. The basis-trade proxy edges out the yield curve, but the record is too
short to tell skill from luck.**

**Where the indicators stand now** (their percentile within their own history):

| Indicator | Latest | Score |
|---|---|---:|
| FICC share of money-fund repo | Sep 2026 | 95% |
| Hedge-fund repo / private Treasuries | Jun 2026 | 94% |
| Leveraged funds' futures short | Sep 2026 | 77% |
| NFCI leverage subindex | Sep 2026 | 70% |
| 10y − 3m curve | Sep 2026 | 68% |
| NFCI | Sep 2026 | 34% |
| Baa − 10y | Sep 2026 | 4% (spreads very tight) |

The chain indicators read high, but over 2017–2025 a high reading on them was a weak guide to stress in the next six
months.

## Limits

- **Eight named events.** Each chain series starts in 2013–14, so there is no 2008 to learn from.
- **The "best" indicator** on each side is chosen on the full period, an optimism both sides share.
- **Six-month labels overlap**, so neighbouring months are not independent; the block bootstrap by year allows for
  some of that.
