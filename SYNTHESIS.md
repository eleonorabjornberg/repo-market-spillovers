# Is the repo market signalling a crisis?

*What public data shows about the US repo market, the leverage behind the Treasury market, and warning signs,
2018–2026. Eleonora Björnberg, with Claude. October 2026.*

## The short answer

Not yet, at least not in any way public data can detect. Six studies looked for the repo market's fingerprints on wider
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

None of these has a track record to say what it means, because none has been here before. A public monthly watch now
tracks them: the **[Repo Market Watch](index.html)**.

## Why the repo market

The repo market is where cash is lent overnight against collateral, mostly US Treasury securities. About $3 trillion a
day changes hands in the cleared part alone. It is how leveraged investors finance their Treasury holdings, and how
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
| What does hedge-fund repo fund now that the basis trade shrank? | **Still Treasuries**, now hedged more with swaps than futures | [11](results/study-11/result.md) |
| Does high federal debt make Treasuries a worse safe haven? | **Not detectably**; inflation explains it | [09](results/study-09/result.md) |

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

### 2. Today does not look like 2000 or 2007, but it is different

| | July 2007 | Today |
|---|---:|---:|
| Commercial paper − bill spread | 42 bp | about 0 |
| Financial conditions (Chicago Fed NFCI) | −0.37 | −0.53 (loose) |
| Repo, all collateral (% of GDP) | 34% | 22% |
| Household debt (% of GDP) | 96% | 66% |
| Federal debt held by the public (% of GDP) | 35% | **97%** |
| Hedge-fund repo borrowing (% of GDP) | n/a | **10.4%** (3.6% in 2013) |
| Baa − 10-year spread | 165 bp | **148 bp** |
| 10-year term premium | 0.79% | 0.96%, highest since 2010 |

Funding markets are calm, and overall leverage in repo is lower than before 2008. The leverage has moved: from
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
- FICC's share of money-fund repo was flat at about 16% from 2019 to November 2023;
- after the SEC adopted the rule in December 2023, it rose about 21 percentage points a year;
- when the deadlines were extended in February 2025, it slowed to about 2 a year.

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

The episodes were: February 2018, Q4 2018, September 2019, COVID, the UK gilt crisis, SVB, the yen carry unwind and
the April 2025 tariff shock. The repo indicators did slightly better than the standard ones, but every interval
includes a coin flip. Most of these episodes came out of calm.

## What to watch

The watch tracks eight flags monthly, fixed before its first build:
- repo trading above the Fed's rate;
- repo spikes;
- hedge-fund repo or the basis trade at a record;
- borrowing moving away from clearing before the deadline;
- swap spreads at April 2025 levels;
- broad stress;
- complacency in credit.

In September 2026 one was on: **complacency**, with Baa spreads tighter than 96.5% of months since 1986. October's
sell-off pushed the OFR's stress index from −2.5 to −1.5, and the next build will show whether that holds.

The two clearing deadlines are the events to watch. They move the most leveraged part of the market into new plumbing,
on a fixed date.

## What this cannot see

- **Bilateral uncleared repo**, its haircuts and its counterparties. That is where leverage would hide before the
  clearing deadline, and no public dataset covers it.
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
  checksummed. Market data comes from FRED, the OFR, the CFTC, the US Treasury and DTCC.
- **Pre-registration:** every study's design was committed before its first run. Changes made after seeing data are
  marked post hoc in the study.
- **Figures:** every number on a study's result page is read from that study's `result.json`.
