# Study 18: year-end 2026, set down in advance

Written on 26 October 2026, more than two months before the event. The code that scores it,
`scripts/study_18_year_end_2026.py`, is committed with this design and frozen with it. The weekly watch workflow runs
it. It reports "pending" until the data is in, then the verdicts below, whatever they are.

**Why this date.** The turn from 2026 to 2027 is three events at once:
- the first year-end at which the Fed's standing repo facility runs at full allotment from the start (since 11
  December 2025);
- the SEC's deadline for central clearing of cash Treasury trades (31 December 2026);
- the year-end on which banks' G-SIB capital surcharges are measured.

This study cannot separate the three. It records what the repo market does on the day that combines them. Study 10
scores the clearing deadline separately, against earlier year-ends.

**Already known when this was written** (study 17 and its addendum):
- From 2 January to 23 October 2026, SOFR never closed above the facility's line (0 of 203 days). Its 99th
  percentile did on 25 of them (12.3%), by up to 14 bp.
- At year-end 2025, just after full allotment began, SOFR closed above the line on 3 of 14 days and its 99th
  percentile on 10 of 14.
- Before full allotment, the largest month-end gap was 22 bp (31 October 2025).

## Data

- **FRED:** `SOFR`, `SOFR99` (SOFR's 99th percentile), `IORB`, `DFEDTARU` (the top of the target range).
- **New York Fed:** standing repo operation results from the Markets API (`/api/rp/results/search.json`, operation
  type Repo), for take-up on the turn days.

## Definitions

- **The line** is the facility's rate. The FOMC's implementation note of 10 December 2025 set it at the top of the
  target range, so the line is `DFEDTARU` on each day. If a later implementation note sets the facility's rate
  elsewhere, the line follows the note. That is the only judgement the scoring may need, and it will be recorded.
  IORB + 10 bp is reported beside it.
- **The turn days** are the last business day of 2026 and the first business day of 2027, as dated by SOFR
  observations.
- **Comparator:** the turn of 2025 to 2026, measured the same way.

## Tests and verdicts

**T1, the benchmark.** Did SOFR close above the line on either turn day?
- **held** if on neither;
- **breached** if on either, with the largest gap in bp.

**T2, the top of the market.** Did SOFR's 99th percentile close above the line on either turn day?
- **held** if on neither;
- **breached** if on either, with the largest gap in bp.

**T3, against the previous year-end.** The largest gap of SOFR above the line over the two turn days, against the
same at the turn of 2025.
- **milder** if smaller by at least 2 bp;
- **worse** if larger by at least 2 bp;
- **similar** otherwise.

A turn on which SOFR stays at or below the line has a gap of zero.

**Reported, no verdict:** take-up at the facility's operations on the two turn days, and the same for the 2025 turn.

## Forecasts, made now

Written down so they can be wrong:
- **T1: held.** The benchmark has not closed above the line in 2026. Year-end is the hardest test, though, and the
  2025 turn breached three weeks after full allotment began.
- **T2: breached.** The 99th percentile went through the line on about one day in eight in 2026, and on 10 of 14 days
  at the 2025 year-end.
- **T3: milder.** The facility has had a year at full allotment, and reserves have been topped up by bill purchases
  since December 2025.

A wrong forecast is a result too. The page will say so.

## When it is scored

Once FRED has data for the fifth business day of 2027, so that late revisions have settled. Until then the status is
"pending". The script never rescores an event once its verdict is written. A rerun reproduces the same verdict from
the same data.

## Limits

- **One event.** Its result describes one year-end, not a rule.
- **Three causes at once** (above), which cannot be separated.
- **The line** depends on the facility's rate, which the Fed can change. A change before the year-end is recorded,
  and the line follows it.
