# Plan: are there warning signs of a bond-market crisis, and does the repo market show them?

Drafted 26 October 2026. Eleonora's decisions of 26 October 2026 are recorded at the end; the plan is in force with
them.

## The question

Eleonora's suspicion is that the repo market is affecting markets as a whole more than anyone realises, and that
looking hard at it would reveal warning signs of a coming crisis in the bond market.

The project turns that into claims that can each fail:

- **H1, the chain.** A larger share of the Treasury market than ever rests on short-term repo funding, and the chain
  is concentrated: a few kinds of borrower (leveraged funds), a few kinds of lender (money funds through FICC), one
  kind of collateral (Treasuries).
- **H2, amplification.** Shocks in the Treasury market now spread into repo, and more so as that chain has grown.
- **H3, spillback.** Repo stress spreads into wider markets: Treasuries, credit, equities, other funding markets.
- **H4, warning.** Indicators of the chain would have warned of past stress better than the standard warning signs
  (the yield curve, credit spreads, financial conditions).
- **H5, the transition.** The changes now under way are moving the chain's fragility, in a direction we can see as
  it happens. These are the end of QT, the Fed's bill purchases, and Treasury central clearing (cash trades on
  31 Dec 2026, repo on 30 Jun 2027).

A crisis can't be predicted with confidence from a handful of past ones, and the project doesn't claim to. What it
can deliver is an answer for each claim: supported, not supported, or untestable with public data, with the
evidence behind each.

## Where things stand

| Study | Hypothesis | Result |
|---|---|---|
| [Event study 01](results/event-study-01/result.md) | H3, on calendar days | **Not supported** at daily closes: calendar repo pressure does not move yields, VIX, credit, equities or the dollar more when reserves are scarce. |
| [Study 02](results/study-02/result.md) | Context for H1 and H4 | Today does not resemble the run-up to 2000 or 2007 on the indicators that flashed then. Three things have never been at today's levels: hedge-fund repo (10.4% of GDP), public debt (97% of GDP), credit spreads as tight as only in 1994–97. |
| [Study 03](results/study-03/result.md) | H1 | **Not supported** as specified: hedge-fund repo is at a record relative to private Treasuries (12.7%), and FICC's share of money funds' repo rose from 16% to 42%. But the basis-trade proxy is below 2019, and lending is less concentrated across counterparty types. |
| [Study 04](results/study-04/result.md) | H2 | **Supported for 2025–26 only** by its rule (+1.1 bp [0.0, 2.2]), but weak: the main test repeats the probe, a +10-day placebo is 84% as large, the 2018–19 replication has the opposite sign, there is no dose–response, and the effect is larger after rallies than sell-offs. |
| [Study 05](results/study-05/result.md) | H3 | **Not supported**: after 2025–26's non-calendar repo shocks the OFR stress index eased (−0.11 [−0.36, +0.05]); 10-year swap spreads (built from DTCC trades) show no pass-through from repo (−0.04 bp/bp [−0.14, +0.06]). Only hint: Baa +1.3 bp. |
| [Study 06](results/study-06/result.md) | H4 | **Cannot tell**: the best chain indicator (leveraged funds' futures short, AUROC 0.63) edges out the yield curve (0.58) by +0.05 [−0.14, +0.24]; no indicator warned reliably over eight episodes since 2017. |
| [Study 07](results/study-07/result.md) | H5 | **Clearing migration supported**: FICC's share of money-fund repo sped up by +19.8 pp a year [+13.3, +27.0] at the SEC's adoption of the rule and slowed after the extension (also on private repo alone, post hoc). The monthly public watch is live, with 1 of 8 flags on (complacency). |
| [Study 09](results/study-09/result.md) | Added: debt and the safe haven | **Not supported**: Treasuries' weaker haven role since 2020 tracks inflation (+5.9 pp per point), not federal debt (−0.07 pp per point [−0.43, +0.24]); repo moves less after panic sell-offs; household debt fell from 98% to 66% of GDP. |
| [Study 08](SYNTHESIS.md) | Synthesis | Published: repo stress has not spread to wider markets; shocks run from bonds to repo, weakly; no indicator warned reliably. New and untested: record hedge-fund repo, 97% federal debt, very tight credit spreads. Much of the shift to FICC is migration ahead of the clearing mandate. |
| [Study 10](docs/design-study-10-prospective.md) | Prospective | **Pending.** Set on 26 Oct 2026 with frozen code: (A) relief or disruption at the clearing deadlines against the two previous years' same days; (B) the credit lead on new repo shocks (10 needed); (C) whether the chain gives way in the next stress event (Eleonora's concern about the co-moving hedge-fund repo, sponsored repo and basis trade). |

## The studies

Each study keeps to the project's rules: its design is written and committed before it runs, its result page reads
every figure from its `result.json`, and anything decided after seeing data is labelled post hoc. One study is one
pull request.

### Study 03: map of the chain (H1). Descriptive, data in hand.

**Question:** who borrows in repo against Treasuries, who lends, through which channel, and how has that changed
since 2010?

**Data:**
- OFR Hedge Fund Monitor (Form PF, quarterly, 2013–):
  - hedge funds' repo borrowing;
  - long and short Treasury exposure;
  - leverage by fund size.
- OFR Short-term Funding Monitor:
  - money funds' repo lending by counterparty, monthly from 2010–14: through FICC (sponsored), the Fed's RRP,
    domestic and foreign banks;
  - cleared DVP, GCF and tri-party repo volumes, daily from 2018;
  - FICC sponsored volumes, daily from 2020.
- NY Fed primary-dealer statistics: dealer repo and reverse repo by collateral.
- The Fed's Financial Accounts: repo by sector since 1945.

**Output:** a picture of the chain at four dates (2007, 2014, 2019, today), with measures of concentration:
- the share of money-fund repo through FICC;
- hedge funds' share of Treasury repo borrowing;
- hedge funds' short Treasury exposure as a stand-in for the basis trade.

**Can fail:** the chain might be no more concentrated, relative to the Treasury market's size, than in 2019. Scale
everything by Treasury debt outstanding, not only by GDP.

**Effort:** one to two sessions.

### Study 04: does Treasury-market stress now spread into repo? (H2). Test, daily data in hand.

**Question:** on days after large Treasury-market moves, does the repo spread rise, and has that response grown with
the chain (H1)?

**Design:**
- **Shock days** are the top 5% of daily |Δ10y| in each regime and the top 5% of rises in Treasury volatility (OFR
  stress index, volatility category). Calendar days are excluded, as in study 01.
- **Outcome:** the repo spread on the next day and over the next 3 days.
- **Main comparison:** 2025–26 against 2021–23, with 2018–19 as the replication. A dose–response check asks whether
  the response scales with hedge-fund repo/GDP across the quarters 2013–26.
- **Cases:** March 2020 and April 2025, described day by day.
- **Placebo:** shocks shifted by ±10 business days.

**Can fail:** the probe's +1.1 bp does not replicate in 2018–19 (it did not in the probe), or disappears with the
placebo. The design is written knowing the probe, and says so.

**Effort:** one session.

### Study 05: does repo stress spread outward, beyond calendar days? (H3, second test)

**Question:** do repo shocks that the calendar does not explain move wider markets? And do the funding-sensitive
markets respond to calendar pressure, the markets study 01 could not see?

**Design:**
- **Shocks:** non-calendar repo shocks (Δspread ≥ 5 bp; 7 in 2018–19, 7 in 2025–26) with matched placebo days.
- **Outcomes:** those of study 01, plus:
  - Treasury-market liquidity (the Fed's fitted yield-curve data);
  - dealer positions;
  - hedge funds' Treasury exposure in the following quarter.
- **Funding-sensitive markets:** the futures basis and swap spreads, if the data can be had (see "Data").

**Can fail:** with 7 shocks per regime, only large effects can show, so a null here is weak and will be reported as
such.

**Effort:** one session with current data; two to three more if swap spreads are built from DTCC trade reports.

### Study 06: would the chain have warned? (H4). Test, and the hardest one.

**Question:** do indicators of the chain (H1) give earlier or cleaner warning of stress than the standard ones?

**Design:**
- **More stress events.** Four NFCI onsets are too few, so the outcome is widened to defined stress events since
  2010, from three sources:
  - OFR stress index spikes;
  - repo spread spikes;
  - the named episodes: 2011 euro crisis, 2013 taper tantrum, 2014 flash rally, 2019, 2020, 2022 gilt crisis,
    2023 SVB, April 2025.
- **Pre-registration.** The list of events and the stress definition are fixed in the design before any indicator is
  scored against them.
- **Scoring.** Pseudo out of sample, expanding window. Each indicator's hit rate and false alarm rate are compared
  with the curve, credit spreads and the NFCI.

**Can fail:** this is the most likely to come back "cannot tell": the chain series start in 2010–14, which gives
perhaps 8 events. If so, that answer is the result.

**Effort:** two sessions.

### Study 07: the watch (H5). Recurring.

**Question:** as clearing comes in and the Fed's balance sheet changes, is the chain growing, shrinking or shifting?

**Design:** a page refreshed monthly from the studies' scripts. It carries:
- the chain indicators (study 03);
- the amplification estimate on a rolling window (study 04);
- standard stress measures for context;
- the two clearing deadlines marked.

It also tracks the **clearing migration** (added 26 Oct 2026 after Eleonora's note that traders have been
preparing for the June 2027 repo deadline for years). Is the growth of sponsored and cleared repo a structural move
ahead of the mandate rather than a build-up of fragility? The test: does sponsored repo's trend break upward at the
SEC's adoption of the rule (13 Dec 2023) and at its extension (Feb 2025)? It also tracks how much of hedge funds' repo
still sits outside FICC as the deadline nears. The design fixes these break dates before the data is examined.

It also sets out, beforehand, what would count as deterioration, for example sponsored repo falling while
hedge-fund repo holds, which would mean the borrowing has moved to uncleared bilateral repo. This is the part that
watches for warning signs going forward, instead of in hindsight.

**Effort:** one session to build; a few minutes a month to run, which could be a scheduled task.

### Study 08: synthesis

One report answering the question at the top: for each of H1–H5, supported, not supported or untestable, with the
evidence, the limits, and what a reader should watch. It would be written for a reader outside the project, and
published as a page if wanted.

**Effort:** one session.

## Order and dependencies

```
03 map (H1) ──┬──> 04 amplification (H2) ──┬──> 06 warning (H4) ──> 08 synthesis
              │                            │
              └──> 07 watch (H5) <─────────┘
05 spillback (H3): independent; its funding-market part waits on data access
```

Studies 03 and 04 can start now. 05's first part can too. 06 needs 03 and 04. 07 needs 03, and 04 for its rolling
estimate. Total: about eight to ten sessions, plus two to three if swap spreads are built from DTCC data.

## Data

| Source | Gives | Status |
|---|---|---|
| FRED | rates, spreads, yields, Financial Accounts, NFCI, GDP | open |
| OFR (stress index, Hedge Fund Monitor, Short-term Funding Monitor) | hedge-fund repo and Treasury exposure, money-fund repo by counterparty, cleared repo volumes, sponsored repo | open |
| NY Fed (markets API, primary dealers) | dealer positions and financing, SOFR, SRF and RRP operations | open |
| Fed (fitted yield curve, H.4.1) | Treasury curve, balance sheet | open |
| Treasury Fiscal Data | issuance, TGA, settlements | open |
| repo-market-model panel | the daily repo spread and calendar, pinned and digest-checked | in use |
| CFTC Traders in Financial Futures (`publicreporting.cftc.gov`, `www.cftc.gov`) | leveraged funds' Treasury futures positions: the direct basis-trade measure | **blocked**: needed for 03 and 05 at full strength |
| DTCC public swap reports (`pddata.dtcc.com`) | SOFR swap trades, from which swap spreads can be built | **blocked**: needed for 05's swap-spread part |
| FINRA TRACE Treasury aggregates (`api.finra.org`) | Treasury trading volumes | **blocked**: optional |
| SEC N-MFP (`www.sec.gov`) | fund-level detail behind OFR's money-fund aggregates | **blocked**: optional now that OFR covers the aggregates |
| MOVE index, futures prices, cross-currency basis | | not free; out of scope |

## Rules for the whole project

1. **Design before data.** Every study's design is committed before its first run. Anything seen beforehand is
   disclosed; anything changed afterwards is labelled post hoc.
2. **Every claim can fail.** Each study states in its design what result would count against its hypothesis, and
   reports it if that is what comes back.
3. **Figures from `result.json` only.** No typed numbers on result pages.
4. **Count the comparisons.** Where a study makes many, it reports how many intervals exclude zero against what
   chance gives.
5. **Independent of repo-market-model.** This project reads the parent's panel at a pinned commit and digest and
   never writes to it. A finding enters the parent only through its own directive process.
6. **No forecast of a crisis.** Results say what the evidence supports, with its limits.

## Eleonora's decisions (26 October 2026)

1. **Scope:** all five claims, H1–H5, in the order above.
2. **Network:** the CFTC, DTCC, FINRA and SEC hosts have been added to the environment's network policy.
3. **Study 06 stress events:** widened beyond the NFCI onsets to named episodes since 2010. Claude fixes the list in
   study 06's design, before any indicator is scored against it.
4. **The watch:** study 07 runs monthly on a schedule, and its page is public.
5. **Audience:** the synthesis is written to be published.
6. **Review:** Claude merges each study's pull request itself once its checks pass; she does not review each one.
