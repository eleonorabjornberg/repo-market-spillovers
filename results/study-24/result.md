# Study 24: can public data see the swap-spread trade? — result

**Test, with a weak verdict.** Design: [`docs/design-study-24-swap-spread-visibility.md`](../../docs/design-study-24-swap-spread-visibility.md),
committed before the data was fetched. Every figure is read from [`result.json`](result.json).

**Sources:** DTCC's public swap reports, 513 trading days from 7 November 2024 to 6 November 2026 (DTCC's files for 1–6
November 2024 have left its rolling window); the OFR Hedge Fund Monitor (Form PF, quarterly, to June 2026; the CFTC's
leveraged-fund futures DV01, weekly); FRED `DGS10`. Each input's SHA-256 is in `metadata/s24_manifest.json`.

## In one line

By the design's rules, a public measure of the swap-spread trade can be built from DTCC's swap reports: it passes both
tests. But both passes are marginal. The Form PF correlation lands exactly on the threshold (0.6, on six quarters), and
April 2025 is above its interval by 0.4 points. Read it as "public data can see this trade a little", not "public data
tracks it".

## The measure

A swap-spread trade puts one swap in a package with a Treasury (or a Treasury future). A swap-curve trade puts two or
three swaps in one package. So package trades that carry a package spread are grouped by execution second, platform and
spread. A group with one swap is a **single-swap spread package**, the candidate swap-spread trade. Risk is DV01: notional
× annuity factor × 1 bp.

- Single-swap spread packages are **14.2%** of all new SOFR swap DV01 over the two years.
- As a check on the inputs, the 10-year SOFR swap spread built from outright trades minus `DGS10` is at plausible levels:
  −44.8 bp in the first week and −38.6 bp in the last, within −57.0 to −36.6 bp.

## The tests

| | Question | Reading | Rule | Outcome |
|---|---|---|---|---|
| Q1 | Does it track hedge funds' rate derivatives (Form PF)? | Spearman 0.6 over six quarters (2025 Q1 – 2026 Q2) | ≥ 0.6 | **Passes, on the threshold** |
| Q2 | Does it see the April 2025 unwind? | April share 15.29%; January–March 14.08% [13.31%, 14.90%] | above the interval | **Passes, narrowly** |

**Q1, by quarter.** The quarterly flow, against the change in hedge funds' rate-derivative gross notional:

| Quarter | Single-swap spread DV01 ($m per bp, new trades) | Form PF change ($bn gross notional) |
|---|---:|---:|
| 2025 Q1 | 515.0 | +906 |
| 2025 Q2 | 539.5 | +1,177 |
| 2025 Q3 | 477.7 | +534 |
| 2025 Q4 | 451.1 | +788 |
| 2026 Q1 | 627.8 | +1,766 |
| 2026 Q2 | 534.1 | −185 |

The two series agree on the busiest quarter (2026 Q1) and that 2025 Q3 was quiet. They disagree on 2026 Q2, when Form PF
exposure fell while new spread packages stayed busy. New trades and a change in the stock are different things, which
this test cannot separate: an unwind is also new trades.

**Q2, by week.** The single-swap share of SOFR swap DV01 peaked at 16.38% in the week of 7 April 2025, the week of the
swap-spread unwind the Fed describes, then fell back to 13.88% and 14.40% by late April.

## Reported only

| | Question | Reading |
|---|---|---|
| Q3 | Does the monthly flow move with leveraged funds' futures DV01? | correlation 0.074 [−0.39, +0.57], 23 months: **no visible link** |
| Q4 | Does the weekly flow move with the 10-year swap spread? | correlation −0.199 [−0.44, +0.05], 104 weeks: **no clear link** |

Both reported intervals include zero. Of the design's four intervals, about 0.4 would exclude zero by chance.

## What changed over two years (descriptive)

| | Dec 2024 – Feb 2025 | Aug – Oct 2026 |
|---|---:|---:|
| Single-swap spread DV01, $m per bp | 454.7 | 639.2 |
| Share of all SOFR swap DV01 | 13.26% | 15.19% |
| of which 1.5–4 years | 23.8 | 66.1 |
| 4–8 years | 159.2 | 187.7 |
| 8–15 years | 167.2 | 240.9 |
| 15–31 years | 104.5 | 144.5 |

The front end grew most: single-swap spread DV01 at 1.5–4 years nearly tripled. That fits the Dallas Fed's account of
front-end swap-spread wideners replacing the basis trade (McCormick, Ramaswamy and De Vere, 16 October 2026), and study
13's finding that the futures decline sits in the 2-year contract. It is descriptive, and its first and last three
months were not chosen to test it. Over the same span leveraged funds' net futures DV01 went from −$475.6m to −$421.3m
per bp.

## What public data hides (Q5)

- **Direction.** No trade says who paid fixed, so a new position and an unwind look the same. This is the main limit.
- **Size.** 8.95% of SOFR swap DV01 is reported at a capped notional, so large trades are understated; for single-swap
  spread packages the share is 1.74%.
- **Structure.** 24.46% of package trades carry no package spread and cannot be classified.
- **Counterparty.** The prime-brokerage flag was FALSE on every trade seen in the design's check, so it cannot single out
  hedge funds.

## Limits

- Six quarters is too few for a strong test of Q1; one quarter's rank would move the correlation across the threshold.
- Legs of one curve package executed in different seconds would be counted as single-swap packages.
- The measure counts new trades of every user, not hedge funds alone.
- **One change after the design:** the fetch first stopped on a malformed fixed rate. Rates outside −5% to 20% are now
  treated as missing (4% assumed), as the design already did for absent rates, and every day was re-fetched under the
  same rule.

## What it means

The futures basis was visible every week. The trade that replaced it is visible only faintly: a measure can be built
that moves with Form PF and caught the April 2025 unwind, but it carries no direction, and both of its passes are on the
margin. Anyone relying on public data for crowding in the swap-spread trade should treat it as a rough flow gauge, not
a position.
