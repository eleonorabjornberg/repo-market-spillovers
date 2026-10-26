# Study 07: the watch (H5), and the clearing migration

Written on 26 October 2026, before the test below was run and before the watch page existed. Plan:
[`PLAN.md`](../PLAN.md), H5. Eleonora's decisions: the watch runs monthly on a schedule and its page is public. The
clearing test follows her note (26 Oct 2026) that traders have been preparing for the June 2027 repo-clearing deadline
for years.

**Disclosed beforehand.** Study 03's chart of FICC's share of money-fund repo has been seen. It rose from about 16% in
mid-2019, dipped in 2021–22, and climbed steeply from 2023 to about 42% by mid-2026. Sponsored repo as a share of DVP
volume has also been seen (rising steadily since 2021). The break months below were chosen from the regulatory
calendar, not from those charts. But because the charts were seen, the test can confirm a break but not discover one.

## Part 1: the clearing-migration test (one-off)

**Claim:** the growth of cleared repo is, at least in part, a structural move ahead of the SEC's mandate, rather than
only a build-up of leverage.

**Series (monthly, study 03's definitions):**
- C1, FICC's share of money-fund repo (from 2014);
- M6, FICC sponsored repo and sponsored reverse repo as shares of cleared DVP volume (from 2020).

**Break months, fixed from the regulatory calendar:**
- **2023-12:** the SEC adopted the rule on 13 Dec 2023.
- **2025-02:** the SEC extended the deadlines on 25 Feb 2025.

**Model:** a segmented linear trend for each series, with slopes before 2023-12, from 2023-12 to 2025-01, and from
2025-02 on. The intervals come from a moving-block bootstrap of residuals (blocks of 6 months, 2,000 draws, seed
20261031).

**What counts:**
- **Migration supported** if, for C1 and for sponsored reverse repo's share, the slope after 2023-12 exceeds the slope
  before it, with the interval of the difference excluding zero.
- **Partly supported** if one of the two series meets it.
- The 2025-02 break is reported, and decides nothing.

**What it would mean:** if supported, part of study 03's "concentration in FICC" is the market doing what the regulator
asked, which nets exposures and reduces dealer balance-sheet strain. That makes it less a warning sign than it looked.
The risk shifts to FICC itself, a single point of failure.

## Part 2: the watch (recurring)

A public page, rebuilt monthly by a scheduled GitHub Actions workflow. It shows the latest reading of each indicator,
its history, and the flags below, set now, before the first build. It also counts down to the clearing deadlines
(31 Dec 2026 cash, 30 Jun 2027 repo).

The watch reads SOFR and IORB from FRED directly, not from repo-market-model's pinned panel, so it stays current. It is
a monitor, not a study: it scores nothing and changes no verdict.

**Flags**, each on or off at each monthly run:

| Flag | On when | Why |
|---|---|---|
| F1 Repo above the Fed's rate | the month's average SOFR − IORB > 0 bp | reserves no longer ample |
| F2 Repo spike | any day in the month with SOFR − IORB ≥ 10 bp | stress beyond the calendar's usual |
| F3 Hedge-fund repo at a record | hedge-fund repo / private Treasuries at its highest since 2013 | leverage still building |
| F4 Basis trade at a record | leveraged funds' futures short / private Treasuries above its previous peak | the classic basis trade rebuilding |
| F5 Moving away from clearing | sponsored reverse repo's share of DVP has fallen for three months running while hedge-fund repo has not fallen | leverage moving to uncleared repo before the deadline |
| F6 Swap spreads at April 2025 levels | 10-year SOFR swap spread ≤ −60 bp on any day | dealer balance-sheet strain |
| F7 Broad stress | OFR financial stress index monthly average > 0 | markets under more stress than average |
| F8 Complacency | Baa − 10y in the lowest 5% of its history since 1986 | risk priced as if absent (study 02) |

**What a flag means.** Studies 04–06 found that none of these indicators reliably warned of past stress. The page says
so beside the flags. A flag says "this has changed", not "a crisis is coming".

## Notes added after the first build (26 October 2026)

- **F5's leg.** F5 is defined on sponsored *reverse* repo, which per the OFR's definitions is mostly money funds
  lending cash, not hedge funds borrowing it. So F5 detects money funds' cash leaving clearing, not hedge funds'
  borrowing leaving it. The flag stays as fixed here. The page's description of F5 was corrected to say "sponsored
  reverse repo"; it had said "sponsored repo".
- **A reading added (not a flag).** The watch now shows FICC sponsored repo (the hedge-fund leg) over hedge funds' Form
  PF repo borrowing, quarterly: a public proxy for how much hedge-fund repo is centrally cleared ahead of the June 2027
  deadline. It sets no flag and changes no rule.
- **Weekly runs (26 October 2026, Eleonora's decision).** The workflow runs every Monday instead of on the 3rd of each
  month. The flags are unchanged: each is still scored on the last complete month, and that month's row in
  `results/watch/flags_history.csv` is re-scored each week until the next month ends, so late-published data can still
  change it. The daily charts now run to the latest data, and the OFR stress index is charted daily; those are display
  changes only.

- **A second reading added (not a flag), 26 October 2026.** The watch now shows, weekly, the share of primary dealers'
  Treasury reverse repo (their cash lending) that is uncleared bilateral, from the New York Fed's FR 2004 statistics:
  study 14's measure M1, with weeks that have a suppressed venue left out. Because the share dips every year-end, the
  page compares the latest four weeks with the same weeks 52 weeks earlier, never with the weeks just before. It sets
  no flag and changes no rule. Its first reading: 55.4% in the four weeks to 14 October 2026, against 54.2% a year
  earlier.
