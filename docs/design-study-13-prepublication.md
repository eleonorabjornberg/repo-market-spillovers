# Study 13: pre-publication checks on the article's claims

Written on 26 October 2026, before these checks were run. Eleonora is drafting a newspaper article from this project's
findings; before anything is sent out, each claim the draft leans on is checked against the way it is most likely to
be wrong. Descriptive and diagnostic; it tests no new hypothesis.

**Disclosed beforehand.** The quarterly values of the hedge-fund clearing proxy (FICC sponsored repo over hedge funds'
Form PF repo borrowing) were seen while building the watch: 19.9% (Q3 2024), 28.9% (Q4 2024), 25.7% (Q1 2025), 25.5%
(Q2 2025), 29.2% (Q3 2025), 35.2% (Q4 2025), 33.9% (Q1 2026), 31.3% (Q2 2026). They suggest a fourth-quarter bump,
which is why check C1 exists.

## The checks, and what would count against each claim

**C1. "The hedge-fund side of clearing has slipped" (draft: 35% at end-2025 to 31% in mid-2026).**
- **Risk:** seasonality. Sponsored repo is used more around quarter- and year-ends, so a fourth quarter against a
  second quarter can fall for calendar reasons alone.
- **Check:** compare like with like, each quarter against the same quarter a year earlier. Also compare the
  year-end month alone against neighbouring months, using monthly sponsored repo volume.
- **The claim survives** only if Q2 2026 is below Q2 2025, or Q1 2026 below Q1 2025. Otherwise it is withdrawn, and
  the article says the share is still rising year on year.

**C2. "The basis trade peaked in October 2024 and has shrunk by about 30%."**
- **Risk:** face value treats a 2-year and a 30-year contract alike. If funds shifted to longer contracts, the risk
  (duration) may not have fallen.
- **Check:** weight each contract's net short by an approximate duration of its cheapest-to-deliver: 2Y 1.9, 5Y 4.2,
  10Y 6.3, Ultra 10Y 8.5, Bond 12.0, Ultra Bond 18.0 years. These are fixed here, from typical deliverables.
- **The claim survives** if the duration-weighted short is also at least 15% below its peak, with the peak in 2024 or
  2025.

**C3. "The hedge has moved from futures to swaps."**
- **Risk:** derivative exposure may have grown for unrelated reasons, everywhere and all along.
- **Check:** compare the futures short as a share of hedge funds' long Treasury exposure in Q3 2024 and Q2 2026.
  Also compare the growth of hedge funds' interest-rate derivatives from Q3 2024 to Q2 2026 with its own growth over
  the previous seven quarters, Q4 2022 to Q3 2024.
- **The reading is strengthened** if the futures cover fell and derivative growth sped up after Q3 2024. It is
  **weakened** if derivative growth was as fast or faster before.

**C4. "Repo stayed calm through October's bond swings."**
- **Risk:** the median repo rate can stay calm while the upper end of the distribution spikes.
- **Check:** SOFR's 99th percentile minus IORB, daily, October 2026, from the New York Fed's API via FRED (`SOFR99`).
- **The claim survives** if that never exceeds 10 bp on a day that is not a month-end.

**C5. Is the angle fresh?**
- **Check:** a search of public reporting and official publications from 2025–26 for the basis-trade decline and a
  shift to swap hedges.
- **Reported, not scored:** if it is widely reported, the article should cite that reporting instead of presenting
  the shift as new.

Each check's result is written to `results/study-13/result.json`. The fact-check sheet and the draft are corrected to
match before anything is sent.
