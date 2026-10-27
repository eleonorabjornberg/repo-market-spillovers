# Is the repo market signalling a crisis?

*What public data shows about the US repo market, the leverage behind the Treasury market, and warning signs,
2018–2026. Eleonora Björnberg, with Claude. October 2026.*

## The short answer

Not yet, at least not in any way public data can detect. Ten studies looked for the repo market's fingerprints on wider
markets, and for warning signs of a crisis in the bond market. They found:

- **Repo stress has not spread to wider markets.** On the days repo was most strained, Treasury yields, stock prices,
  volatility, credit spreads, the dollar and swap spreads did not move more than usual.
- **The direction runs the other way.** When stress came (March 2020, April 2025), it started in the bond market, and
  repo followed. In April 2025 the bond market's worst week in years moved repo by 7 basis points, less than an
  ordinary quarter-end.
- **No indicator warned reliably.** Over eight stress episodes since 2017, neither the repo-market indicators nor the
  standard warning signs did much better than a coin flip.

What *has* changed is the scale and shape of the borrowing behind the Treasury market:
- hedge funds' repo borrowing is near a record relative to the market;
- federal debt held by the public is 97% of GDP;
- credit spreads are as tight as they have been only once before, in the mid-1990s.

None of these has a track record to say what it means, because none has been here before. A public weekly watch now
tracks them: the **[Repo Market Watch](index.html)**.

## Why the repo market

The repo market is where cash is lent overnight against collateral, mostly US Treasury securities. The OFR puts the
amount outstanding at about $13.5 trillion, roughly 40% of GDP, across all its segments; about 70% of it is backed by
Treasuries.¹ Hedge funds are the largest borrowers (about $3 trillion) and money market funds
the largest lenders (about $3 trillion). It is how leveraged investors finance their Treasury holdings, and how
money funds earn on their cash. If it seizes up, those holders must sell, and the Treasury market, the base of global
finance, feels it. That happened in September 2019 (repo rates spiked to 5%) and in March 2020 (the "dash for cash").

The gauge throughout is the **SOFR − IORB spread**: the overnight repo rate minus the rate the Fed pays banks on their
reserves. Deeply negative means cash is plentiful; near zero and above means it is getting scarce. It averaged −11.5 bp
in 2022 and −1.3 bp in 2026.

## The questions, and what the data said

Each study fixed its design, its tests and what would count against it before looking at the data. Anything decided
afterwards is labelled as such in the study.

| Question | Verdict | Study |
|---|---|---|
| Does repo pressure move wider markets? | **No**, on calendar days or beyond them | [01](results/event-study-01/result.md), [05](results/study-05/result.md) |
| Does today look like the run-up to 2000 or 2007? | **No**, on the measures that flashed then; three new features | [02](results/study-02/result.md) |
| Does a record, concentrated repo chain sit under the Treasury market? | **Not as specified**: record hedge-fund repo, but the basis-trade proxy is shrinking | [03](results/study-03/result.md) |
| Do Treasury shocks now spread into repo? | **Weakly, in 2025–26 only**, and not the way forced selling would | [04](results/study-04/result.md) |
| Would repo indicators have warned of past stress? | **Cannot tell**; nothing warned reliably | [06](results/study-06/result.md) |
| Is the growth of cleared repo a move ahead of the SEC's mandate? | **Yes** | [07](results/study-07/result.md) |
| Does high federal debt make Treasuries a worse safe haven? | **Not detectably**; inflation explains it | [09](results/study-09/result.md) |
| Would corporate bonds or repo cushion a stock-market bust? | **Only while Treasuries act as a haven**: corporate collateral is a small part of repo, and corporate yields rise with Treasury yields in 9 of 10 panics when Treasuries sell off | [15](results/study-15/result.md) |
| What keeps Treasury repo outside central clearing? | **The uncleared market grew alongside clearing**: a large matched book, mostly zero-haircut netted packages, that enters clearing only at year-ends | [14](results/study-14/result.md) |
| Does data-centre borrowing reach the swap market, as the Dallas Fed suggests? | **Not visibly**: debt up $95bn to $334bn in a year, but long-dated swap trading no heavier around the bond deals | [16](results/study-16/result.md) |
| Why are recent month-end spikes milder than 2018–19's? | **Only the extremes are**: ordinary month-ends are as large; the standing repo facility caps the worst spikes, leakily | [17](results/study-17/result.md) |
| What does hedge-fund repo fund now that the basis trade shrank? | **Still Treasuries**, now hedged more with swaps than futures | [11](results/study-11/result.md) |
| Can better warning indicators be found? | **Not yet**: two promising, unproven candidates | [12](results/study-12/result.md) |
| What happens at the clearing deadlines, and in the next stress? | **Pending**: tests set before the data exists | [10](docs/design-study-10-prospective.md) |

### 1. Repo stress has not spread to wider markets

The calendar gives a natural experiment. Repo pressure lands on known days (month-ends, quarter-ends, tax dates,
Treasury settlements), and how hard depends on reserves: a month-end added about 16 bp to SOFR − IORB in 2018–19, under
1 bp when reserves were abundant (2021–23), and 5 bp in 2025–26. If repo pressure moved wider markets, they should move
more on those days when reserves are scarce.

They don't. The extra month-end move in the 10-year yield, VIX and corporate credit spreads, scarce regime minus
abundant, was indistinguishable from zero in both scarce periods.

The same held for:
- the seven largest repo jumps since 2025 that the calendar doesn't explain (the OFR's stress index eased slightly
  after them);
- daily swap spreads, built for this project from about 98,000 public swap trades. Swap spreads are the Treasury price
  most exposed to dealers' balance sheets, yet they showed no pass-through from repo.

The single hint: corporate (Baa) spreads rose 1.3 bp in the two days after those seven repo jumps.

The calendar's grip has not weakened either ([study 17](results/study-17/result.md)). Ordinary month-ends lifted repo
rates as much in 2025–26 as in 2018–19. What changed is the extremes. Year-end 2018 sent SOFR 65 bp above the top of
the Fed's range; since the standing repo facility began offering cash at that rate, the worst turn day has reached
22 bp above it, on 31 October 2025. Since the Fed moved the facility to full allotment in December 2025, SOFR has not
closed above its rate once in 2026, but the most expensive 1% of trades has, on about one day in eight: the facility
caps the benchmark, not the top of the market. Those expensive trades sit in cleared bilateral repo, where dealers lend
to clients such as hedge funds; since April 2026 they have been a premium of 1–5 bp on days when tri-party repo traded
well below the line and nobody used the facility ([study 19](results/study-19/result.md)). The ceiling caps dealers'
own funding, not what they charge clients. That markup is a balance-sheet price: it is about zero when reserves are
abundant, about 7 bp when they are scarce, and it jumps at every quarter-end, to about 31 bp at year-ends
([study 23](results/study-23/result.md)). Study 18 has set down, in advance, what the turn of 2026 to 2027 will test. The slow rise in repo rates since
2022 went mostly with money funds' cash leaving the Fed's reverse repo facility, and then with falling reserves.
How many reserves count as "ample" has grown with the government's debt: repo got tight when reserves fell to about a
tenth of federal debt held by the public, at $1.6 trillion in 2018–19 and at $3.1 trillion in 2025–26
([study 20](results/study-20/result.md)). The match holds for every way of counting the debt and for none of the
alternatives tried, GDP, bank assets or the size of the repo market ([study 22](results/study-22/result.md)). In 2026
the ratio has stayed at 9.3–10%, the lowest since 2019; whether that keeps calling scarcity is now being tested on
months to come ([study 21](results/study-21/result.md)).

### 2. Today does not look like 2000 or 2007, but it is different

| | July 2007 | Today |
|---|---:|---:|
| Commercial paper − bill spread | 42 bp | about 0 |
| Financial conditions (Chicago Fed NFCI) | −0.37 | −0.53 (loose) |
| Repo liabilities, all collateral (% of GDP)² | 34% | 22% |
| Household debt (% of GDP) | 96% | 66% |
| Federal debt held by the public (% of GDP) | 35% | **97%** |
| Hedge-fund repo borrowing (% of GDP) | n/a | **10.4%** (3.6% in 2013) |
| Baa − 10-year spread | 165 bp | **148 bp** |
| 10-year term premium | 0.79% | 0.96%, highest since 2010 |

Funding markets are calm, and overall leverage in repo, relative to the economy, is lower than before 2008. The leverage has moved: from
households and dealer balance sheets financing mortgages in 2007, to the government's debt and hedge funds financing
Treasuries today. Credit spreads this tight have occurred only in 1994–97, and the warning they gave then was LTCM in
1998.

### 3. The chain behind the Treasury market

Scaled by the Treasuries the private market has to hold ($26.6 trillion in mid-2026):
- **Hedge-fund repo** rose from 9.4% (2019) to 12.7%, near its record (13.1%, October 2025).
- **The basis trade's public proxy**, leveraged funds' net short in Treasury futures, peaked at $1.15 trillion in
  October 2024. It has shrunk since, to $0.80 trillion, while hedge-fund repo held. [Study 11](results/study-11/result.md)
  narrows down why: the repo still funds Treasuries (long holdings grew in step with it), but the hedge has moved from
  futures (−16%) to rate derivatives such as swaps (+47% gross). The growth sits with multi-strategy and relative-value
  funds, not macro funds. Same exposure, carried where public data sees it less clearly.
- **Money funds' cash** increasingly reaches borrowers through one channel, FICC's sponsored repo: 16% of their repo in
  2019, 42% in 2026.

### 4. Most of that shift is the market preparing for central clearing

Traders said they had been preparing for the SEC's clearing mandate for years. The data agrees:
- FICC's share of money-fund repo was 2–4% through 2022, when most of their cash sat at the Fed's reverse repo
  facility;
- it began climbing around the SEC's proposal of the rule in September 2022 and reached 36% by January 2025 (an
  earlier version of this page dated the rise to the rule's adoption in December 2023: [study 13](results/study-13/result.md)
  corrected it);
- after the deadlines were extended in February 2025, it slowed to about 2 points a year. The extension may explain
  that, or the easy migration may simply have been done.

The same shape shows in sponsored repo's share of cleared volume, and survives excluding the Fed's own facility. That
makes the concentration less a warning sign than the market following the rule ahead of time; netting through a
clearinghouse eases dealers' balance sheets. The risk it leaves is different: more of the system's cash depends on one
central counterparty working on the worst day. Cash Treasury trades must be cleared from 31 December 2026, repo from
30 June 2027.

### 5. Shocks run from bonds to repo, and only weakly

After the biggest bond-market days of 2025–26, repo rose about 1 bp the next day. That is weak evidence:
- a placebo nearly as large;
- no replication in 2018–19;
- no link to the size of hedge-fund borrowing;
- larger after rallies than after sell-offs, the opposite of forced deleveraging.

**The two big episodes:**
- **March 2020:** repo reached +44 bp.
- **April 2025:** the 10-year yield rose 14 bp in a day and the swap spread collapsed 16 bp in a week, yet repo rose
  only 7 bp, to zero, and was back below IORB within three days. The Fed's Standing Repo Facility, which caps repo
  rates, and the move to clearing are the likely reasons.

### 6. Debt and the safe haven

Across 260 stock-market panic days since 1990, Treasuries rallied less reliably after 2020: yields rose on a third of
panic days, against one in seven in 2008–19. But inflation explains that, not the debt level; the 1990s, with the least
debt, had the least reliable haven. A moderate debt effect cannot be ruled out.

When Treasuries did sell off in a panic, repo felt *less* pressure, not more. Household debt is down from 98% of GDP in
2008 to 66%, and panics widen mortgage spreads by about 2 bp regardless of how much households owe.

Corporate bonds give no cover in that case ([study 15](results/study-15/result.md)). On panic days when the 10-year yield
rose, the Baa corporate yield rose too on 89% of them [83, 94]. Since 2020, corporate yields rose on 46% of panic days,
against 18% in 2008–19. In repo itself corporate bonds are a small corner: dealers' repo against them was about $167bn
in 2026, against about $3.4 trillion against Treasuries. In March 2020 dealers' corporate repo did not shrink, but the
Fed had just opened a facility that lent to dealers against corporate bonds. In 2008 it was different: in the same
dealer data, financing against corporate securities fell 42% from mid-2007 to the months after Lehman, while against
Treasuries it fell 17% and against agency and mortgage securities it held. Lenders pulled back from private
collateral, as the New York Fed's own researchers found with confidential tri-party data (corporate-bond collateral
down roughly 44%, Treasury margins unchanged). So a stock-market bust, say in AI shares,
would be cushioned by the repo market only while Treasuries rally. When they do not, as on some days of March 2020
and more often since inflation returned, Treasuries and corporate bonds fall together.

The companies building AI data centres are a growing part of that corporate market ([study 16](results/study-16/result.md)).
Alphabet, Amazon, Meta, Microsoft, Oracle and CoreWeave owed $334bn at their latest fiscal year-ends, up $95bn in a
year, and most of it is due after five years. The Dallas Fed has suggested that their borrowing reaches the Treasury
market through swaps. In public swap reports it does not show: trading in 20- and 30-year swaps was no heavier
around their 14 registered bond deals than on other days (+6%, interval −16% to +30%). Their largest financings,
through joint ventures and private placements, cannot be seen at all.

### 7. No indicator warned

Every month from November 2017 to September 2025, each indicator was scored by where it stood in its own history up to
then, and checked for whether stress followed within six months:

| Indicator | Record (AUROC: 0.5 = coin flip, 1 = perfect) |
|---|---:|
| Leveraged funds' Treasury futures short | 0.63 |
| FICC share of money-fund repo | 0.60 |
| 10y − 3m yield curve | 0.58 |
| Hedge-fund repo | 0.53 |
| Financial conditions (NFCI) | 0.52 |
| Baa − 10y spread | 0.43 |
| NFCI leverage | 0.41 |

A follow-up ([study 12](results/study-12/result.md)) searched for better indicators without overfitting: nine
candidates chosen in advance by mechanism, 22 stress events since 1990, a development and a test period. A combination
did no better than the yield curve. Two candidates look promising but unproven: the leverage of the 10 largest hedge
funds (0.74, but its data starts in 2013) and long spells of low volatility (good after 2013, worse than chance
before). Both are now tracked by the watch.

The episodes were: February 2018, Q4 2018, September 2019, COVID, the UK gilt crisis, SVB, the yen carry unwind and
the April 2025 tariff shock. The repo indicators did slightly better than the standard ones, but every interval
includes a coin flip. Most of these episodes came out of calm.

## What to watch

The watch, rebuilt every week, tracks eight flags fixed before its first build, each scored on the last complete
month:
- repo trading above the Fed's rate;
- repo spikes;
- hedge-fund repo or the basis trade at a record;
- borrowing moving away from clearing before the deadline;
- swap spreads at April 2025 levels;
- broad stress;
- complacency in credit.

In September 2026 one was on: **complacency**, with Baa spreads tighter than 96.5% of months since 1986. October's
sell-off pushed the OFR's stress index from −2.5 to −1.5; the watch's daily charts show it week by week, and October's
flags are scored once the month is complete.

The two clearing deadlines are the events to watch. They move the most leveraged part of the market into new plumbing,
on a fixed date. Three tests were set before either happens, with the code that scores them
([study 10](docs/design-study-10-prospective.md)):
- **The deadlines:** relief, disruption or no visible effect in repo and swap spreads, against the same days in the two
  previous years. The first verdict is due after January 2027.
- **The credit lead:** whether Baa spreads widen after new repo jumps, once there have been ten.
- **The chain under stress:** at the next stress surge, whether repo strains while the basis trade unwinds. April 2025,
  scored the same way, "held".

The watch also tracks the hedge-fund side of the migration still to come: FICC sponsored repo, mostly hedge funds
borrowing cash, equalled about 31% of hedge funds' repo borrowing in mid-2026, up from about 8% in 2021 and 6 points
higher than a year earlier. It jumps around each year-end, so compare a quarter with the same quarter a year before.

Since October 2026 it also shows, every week, how much of primary dealers' cash lending against Treasuries is
uncleared bilateral repo ([study 14](results/study-14/result.md)). In the four weeks to 14 October 2026 it was 55%,
against 54% in the same weeks a year earlier: eight months before the repo deadline, the segment the rule is meant to
shrink is no smaller a share than a year ago, and larger in dollars ($1.55 trillion against $1.44 trillion). Like the hedge-fund proxy, it dips each year-end,
so it is read against the same weeks a year before. And it tracks
study 12's two candidate indicators, on stress that has not happened yet.

## What this cannot see

- **Bilateral uncleared repo**, its haircuts and its counterparties. That is where leverage would hide before the
  clearing deadline. The New York Fed reports that 75% of these Treasury trades carry no haircut at all, and that only
  about 30% of hedge funds' repo with dealers was centrally cleared by late 2025.¹ No public dataset tracks either over
  time yet; the OFR's new collection is not in its public data feed.
- **Intraday stress**: everything here is daily closes.
- **Futures prices, the MOVE index and cross-currency funding**, which are not free.
- **More history.** The chain's data starts in 2013–14, so 2008 cannot be studied with it, and eight episodes are too
  few to establish any indicator's record.

A null result here means "not visible in daily public data", not "not there".

## How this was done

The project is open: code, data manifests, designs and results are at
[github.com/eleonorabjornberg/repo-market-spillovers](https://github.com/eleonorabjornberg/repo-market-spillovers).
- **Data:** the repo data comes from the companion project
  [repo-market-model](https://github.com/eleonorabjornberg/repo-market-model)'s published daily panel, pinned and
  checksummed. Market data comes from FRED, the OFR, the CFTC, DTCC, the US Treasury (including TIC) and the Federal
  Reserve.
- **Pre-registration:** every study's design was committed before its first run. Changes made after seeing data are
  marked post hoc in the study.
- **Figures:** every number on a study's result page is read from that study's `result.json`.

## Notes

1. Gara Afonso, Jun-Davinci Choi, Gonzalo Cisternas and Will Riordan, "Who's Borrowing and Lending in Repo Markets?"
   and "Follow the Cash! Microstructure of Repo Markets", Federal Reserve Bank of New York, *Liberty Street Economics*,
   28 and 29 September 2026. Their figures draw on OFR, Form PF and N-MFP data not all of which is public.

2. The Federal Reserve's Financial Accounts (series `BOGZ1FL892150005Q`): repo liabilities of all sectors. It is a
   narrower measure than the OFR's $13.5 trillion outstanding across all repo segments, so the two should not be
   compared with each other. The comparison with 2007 uses the same measure at both dates.
