# Study 07: the clearing migration, and the watch — result

Design: [`docs/design-study-07-watch.md`](../../docs/design-study-07-watch.md), committed before the run. Every figure
is read from [`result.json`](result.json) or [`../watch/latest.json`](../watch/latest.json).

## Part 1: is the growth of cleared repo a migration ahead of the mandate? Supported

This tests Eleonora's point that traders have been preparing for the SEC's June 2027 repo-clearing deadline for years.
Each series gets a segmented trend, with breaks fixed in advance at the SEC's adoption of the rule (Dec 2023) and its
extension of the deadlines (Feb 2025). Slopes are in percentage points per year; intervals come from a moving-block
bootstrap.

| Series | Slope before Dec 2023 | Dec 2023 – Jan 2025 | From Feb 2025 | Change at adoption |
|---|---:|---:|---:|---|
| FICC's share of money-fund repo | +1.2 | **+21.0** | +2.4 | **+19.8** [+13.3, +27.0] |
| Sponsored reverse repo, % of cleared DVP | +3.5 | **+13.0** | +2.1 | **+9.5** [+3.7, +15.0] |
| Sponsored repo, % of cleared DVP | +2.4 | +11.8 | +3.6 | +9.4 [+5.7, +13.1] |

Both decisive series meet the rule, so the verdict is **supported**. FICC's share of money-fund repo had been flat for
four years (15.7% in June 2019, 16.2% in November 2023). It then rose to 35.9% in the 14 months after the rule was
adopted. When the deadline was pushed back, the climb slowed to a tenth of that pace, and the share was 39.6% in
September 2026. Both breaks are sharp, and both fall on the regulatory dates.

**Post hoc check, the Fed's RRP.** Money funds pulled most of their cash out of the Fed's reverse repo facility in
2023–24, the same window, which lifts FICC's share of their *total* repo mechanically. Excluding the Fed, FICC's share
of their *private* repo shows the same shape:

| | Estimate |
|---|---|
| Slope before Dec 2023 | +2.5 pp a year |
| Slope from Dec 2023 | +15.3 pp a year |
| Change at adoption | **+12.8** [+8.0, +18.1] |
| Slope after the extension | +1.9 pp a year |

Cash leaving the RRP could still have chosen sponsored repo partly for other reasons, so this narrows the confounder
but does not remove it.

**What this changes:** study 03 read FICC's growing share as concentration, a possible warning sign. Much of it is the
market doing what the regulator required, ahead of time, which nets positions and eases dealers' balance sheets. The
risk it creates is different: more of the system's cash now depends on one central counterparty, FICC, working on the
worst day.

## Part 2: the watch

A public page rebuilt on the 3rd of each month by [`.github/workflows/watch.yml`](../../.github/workflows/watch.yml),
from fresh data, with the eight flags fixed in the design. First build, for September 2026:

| Flag | State | Reading |
|---|---|---|
| F1 Repo above the Fed's rate | off | SOFR − IORB averaged −1.8 bp |
| F2 Repo spike | off | highest day +1 bp |
| F3 Hedge-fund repo at a record | off | 12.7% of private Treasuries (Jun 2026), below the Oct 2025 peak |
| F4 Basis trade at a record | off | 2.9%, below the Oct 2024 peak |
| F5 Moving away from clearing | off | sponsored share steady at 46–47% |
| F6 Swap spreads at April 2025 levels | off | lowest −45 bp |
| F7 Broad stress | off | OFR index −2.5 |
| **F8 Complacency** | **on** | Baa − 10y at 148 bp, tighter than 96.5% of months since 1986 |

**Watch at work:** the OFR index had risen to −1.5 by 22 October, during that month's sell-off, so October's build will
show whether F7 moves.

## Erratum (26 October 2026, study 13)

The test above passed by its pre-registered rule, but its description overstates the timing. A first break in mid- to
late 2022, around the rule's proposal (14 September 2022), fits all three series better than December 2023
([study 13, C6](../study-13/result.md), post hoc). "Flat for four years (15.7% in June 2019, 16.2% in November 2023)"
compared two endpoints: the share fell to 2–4% in 2022, when money funds' cash sat at the Fed's reverse repo facility,
and rose from late 2022. The slowdown after the February 2025 extension holds under every start date; saturation is an
alternative explanation not ruled out.

