# Study 23: the dealer markup as a daily series — result

Design: [`docs/design-study-23-dealer-markup.md`](../../docs/design-study-23-dealer-markup.md), committed before this
study's new data was fetched. Every figure is read from [`result.json`](result.json).

**The markup** is SOFR's 99th percentile minus tri-party's (TGCR's) 99th percentile, in bp. It is the premium the
dearest trades in cleared bilateral repo pay over the dearest in tri-party. The series runs 2 April 2018 – 23 October
2026 (2,137 days).

## In one line

The markup is a balance-sheet price. It is about zero when reserves are abundant, about 7 bp on ordinary days when
they are scarce, and it jumps at every quarter-end, to about 31 bp at year-ends, when banks' balance sheets are
measured. The Fed's full allotment did not touch it, and the growth of sponsored clearing has not shrunk it.

## Q1, balance-sheet dates: it widens at quarter-ends (verdict)

| | Quarter-end turn days (68) | Other days | Difference |
|---|---:|---:|---|
| 99th percentiles | 18.2 bp (year-ends: 30.7 bp) | 6.5 bp | **+11.6 bp** [+5.3, +20.8] |
| 75th percentiles | 9.0 bp (year-ends: 10.6 bp) | 5.5 bp | +3.5 bp [+2.2, +5.0] |

The premium for cleared bilateral repo jumps when dealers' balance sheets are measured. Quarter-ends are reporting
dates for many banks, and year-end is when the G-SIB surcharge is set. This is the pattern a price for balance sheet
would show.

## Q2, full allotment: no change (reported)

On non-calendar days, the markup averaged 7.2 bp in 2025 before full allotment and 6.8 bp after: −0.4 bp [−0.8,
+0.05]. Full allotment caps what dealers pay for cash, not what they charge clients, as study 19 read it.

## Q3, sponsored clearing: no detectable narrowing (verdict)

Across 79 months since March 2020, the monthly markup on non-calendar days and the sponsored share of cleared repo are
**positively** correlated, at +0.63 [+0.09, +0.91]. That is not because clearing raises the markup. Both trended with
the return of scarce reserves.

| | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Markup, non-calendar days (bp) | 8.0 | 11.8 | 7.3 | 0.1 | −0.4 | 6.9 | 7.9 | 7.3 | 6.7 |
| Sponsored share of cleared repo (%) | – | – | 32.9 | 28.1 | 32.7 | 48.4 | 62.6 | 77.6 | 83.3 |

**Reading.** The markup vanished on the floor (2021–22), when reserves were abundant, and came back with scarcity in
2023. Since then it has held at about 7 bp while the sponsored share rose from 48% to 83%. Within the scarce years,
clearing's growth has not compressed it, at least not yet. Whether the June 2027 repo-clearing deadline does is a
question for study 10's deadline test.

## Limits

- **Percentiles are volume-weighted.** Some of the quarter-end jump may be the volume mix shifting between segments.
- **Counterparties are not observed.** "Markup to clients" remains a reading.
- **Q3 compares trends.** The table, not the correlation, is the evidence.
