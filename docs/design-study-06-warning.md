# Study 06: would the chain have warned? (H4)

Written on 26 October 2026, before any indicator was scored against the events below. Plan: [`PLAN.md`](../PLAN.md),
H4. Eleonora's decision of 26 October 2026: widen the stress events beyond NFCI onsets, with Claude fixing the list.

**Disclosed beforehand:**
- **Levels already seen:** the chain indicators' levels (study 03) and the standard indicators' (study 02) have been
  seen, though not set against these events.
- **History of the events:** their history is common knowledge.

## Claim

**H4:** indicators of the repo chain would have warned of stress better than the standard warning signs.

## Stress events (fixed here)

**Named episodes**, from the first trading day of stress (US date):

| # | Episode | Onset |
|---|---|---|
| 1 | Flash crash and first euro-area crisis | 2010-05-06 |
| 2 | US downgrade and second euro-area crisis | 2011-08-01 |
| 3 | Taper tantrum | 2013-05-22 |
| 4 | Treasury flash rally | 2014-10-15 |
| 5 | China devaluation sell-off | 2015-08-20 |
| 6 | "Volmageddon" | 2018-02-02 |
| 7 | Q4 2018 sell-off | 2018-10-10 |
| 8 | Repo spike | 2019-09-16 |
| 9 | COVID, Treasury dash for cash | 2020-02-24 |
| 10 | UK gilt (LDI) crisis | 2022-09-23 |
| 11 | Regional banks (SVB) | 2023-03-09 |
| 12 | Yen carry unwind | 2024-08-01 |
| 13 | Tariff shock and Treasury sell-off | 2025-04-03 |

Events after 2026-03 are left out, because a six-month window after them is not yet observed. That includes October
2026's tech sell-off.

**Mechanical events (robustness):** the first day the OFR financial stress index has risen by at least 1.0 over the
previous 20 business days, at least 60 business days after the previous such event.

## Indicators

All are monthly, from their studies' definitions.

**Chain (study 03):**
- hedge-fund repo / private Treasuries (2013–);
- leveraged funds' net short Treasury futures / private Treasuries (2006–);
- FICC's share of money-fund repo (2014–).

**Standard (study 02):**
- 10y − 3m curve (inverted: low = warning);
- Baa − 10y spread (high = warning);
- NFCI (high = warning);
- NFCI leverage subindex (high = warning).

## Scoring

1. **Label:** a month is positive if a named event's onset falls in the following six months.
2. **Score (pseudo out of sample):** each month, the indicator's percentile within its own history up to that month
   (expanding window, at least 36 months of history), with warning direction applied.
3. **Common period:** from the first month in which every indicator has 36 months of history (March 2017; the FICC
   series starts in March 2014) to September 2025, the last month whose six-month window ends by March 2026. That
   period holds named events 6 to 13.
4. **Measure:** AUROC of each indicator's score for the label, over the common period.
5. **Main test:** the best chain indicator's AUROC minus the best standard indicator's AUROC. Both "bests" are chosen
   by full-period AUROC, a disclosed optimism shared by both sides. The interval is a block bootstrap by calendar
   year: 2,000 draws, seed 20261030.

## What counts

- **H4 supported:** the main difference is positive with its interval excluding zero, and its sign holds on the
  mechanical events.
- **Not supported:** the difference is negative with its interval excluding zero.
- **Cannot tell:** otherwise. This is the expected outcome, given about 8 events in the common period, and the
  result says so plainly.
