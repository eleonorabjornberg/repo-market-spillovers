# Plan: are there warning signs of a bond-market crisis, and does the repo market show them?

Drafted and decided on 26 October 2026 (Eleonora's decisions are at the end). Last brought up to date on 26 October
2026, after study 12. Each study's design, with what was seen before it ran, is in [`docs/`](docs); its figures are in
`results/<study>/result.json`; the findings for a general reader are in [`SYNTHESIS.md`](SYNTHESIS.md).

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

## Where each claim stands

| Claim | Verdict so far | Evidence |
|---|---|---|
| H1 the chain | **Not supported as specified, but the exposure is real.** Hedge-fund repo is near its record (12.7% of private Treasuries). The basis-trade proxy has shrunk since October 2024, because the hedge moved from futures to swaps; the repo still funds Treasuries. | 03, 11 |
| H2 amplification | **Weak, 2025–26 only.** About +1 bp in repo the day after big bond moves, with a near-equal placebo, no replication and no link to leverage. | 04 |
| H3 spillback | **Not supported.** Neither calendar nor non-calendar repo pressure moved wider markets or swap spreads. One lead, Baa +1.3 bp, is now being tested on new data. | 01, 05, 10B |
| H4 warning | **Cannot tell.** No indicator, repo-chain or standard, warned reliably. A search for better ones found two promising but unproven candidates, now tracked. | 06, 12 |
| H5 the transition | **The clearing migration is real and timed to the SEC's rule.** What the deadlines and the next stress do to the chain is being tested prospectively. | 07, 10A, 10C |

## The studies

| Study | Kind | Result |
|---|---|---|
| [01](results/event-study-01/result.md) calendar spillover | test (H3) | **Not supported** at daily closes: calendar repo pressure does not move yields, VIX, credit, equities or the dollar more when reserves are scarce. |
| [02](results/study-02/result.md) then and now | descriptive (H1, H4 context) | Today does not resemble the run-up to 2000 or 2007 on the indicators that flashed then. Three things have never been at today's levels: hedge-fund repo (10.4% of GDP), public debt (97% of GDP), credit spreads as tight as only in 1994–97. |
| [03](results/study-03/result.md) map of the chain | test (H1) | **Not supported** as specified: hedge-fund repo is at a record relative to private Treasuries (12.7%), and FICC's share of money funds' repo rose from 16% to 42%. But the basis-trade proxy is below 2019, and lending is less concentrated across counterparty types. |
| [04](results/study-04/result.md) amplification | test (H2) | **Supported for 2025–26 only** by its rule (+1.1 bp [0.0, 2.2]), but weak: the main test repeats the probe, a +10-day placebo is 84% as large, the 2018–19 replication has the opposite sign, there is no dose–response, and the effect is larger after rallies than sell-offs. |
| [05](results/study-05/result.md) spillback beyond the calendar | test (H3) | **Not supported**: after 2025–26's non-calendar repo shocks the OFR stress index eased (−0.11 [−0.36, +0.05]); 10-year swap spreads (built from DTCC trades) show no pass-through from repo (−0.04 bp/bp [−0.14, +0.06]). Only hint: Baa +1.3 bp. |
| [06](results/study-06/result.md) would the chain have warned? | test (H4) | **Cannot tell**: the best chain indicator (leveraged funds' futures short, AUROC 0.63) edges out the yield curve (0.58) by +0.05 [−0.14, +0.24]; no indicator warned reliably over eight episodes since 2017. |
| [07](results/study-07/result.md) clearing migration and the watch | test (H5) and monitor | **Clearing migration supported**: FICC's share of money-fund repo sped up by +19.8 pp a year [+13.3, +27.0] at the SEC's adoption of the rule and slowed after the extension (also on private repo alone, post hoc). The monthly public watch is live. |
| [08](SYNTHESIS.md) synthesis | report | Published as [`SYNTHESIS.md`](SYNTHESIS.md) and the site's findings page; updated as later studies landed. |
| [09](results/study-09/result.md) debt and the safe haven | test (added by Eleonora) | **Not supported**: Treasuries' weaker haven role since 2020 tracks inflation (+5.9 pp per point), not federal debt (−0.07 pp per point [−0.43, +0.24]); repo moves less after panic sell-offs; household debt fell from 98% to 66% of GDP. |
| [10](docs/design-study-10-prospective.md) three prospective tests | test, pending | Set with frozen code before their data exists: (A) relief or disruption at the clearing deadlines; (B) the Baa lead on new repo shocks (10 needed); (C) whether the chain gives way in the next stress event. Scored each month; [status](results/study-10/status.json). |
| [11](results/study-11/result.md) what hedge-fund repo funds | descriptive | Still Treasuries (repo +21%, long Treasuries +20%); the hedge moved from futures (−16%) to rate derivatives (+47%); growth with multi-strategy and relative-value funds, not macro. The DTCC package proxy did not confirm swap-spread trades. |
| [12](results/study-12/result.md) better indicators? | test (H4) | **Promising, not proven**: the composite is no better than the curve (−0.02 [−0.23, +0.16]); top-10 hedge-fund leverage scores 0.74 (2016–25 only); low long-run VIX 0.78 at 12 months on 2013–25 but 0.44 before. Both are tracked on the watch. |
| [13](results/study-13/result.md) pre-publication checks | checks before the article | One claim withdrawn (the hedge-fund clearing share's dip is seasonal); the basis-trade decline is 17% by risk, not 30%; the swap shift is already published by the Fed; the move to clearing began with the 2022 proposal, not the 2023 adoption (study 07 erratum). |
| [14](results/study-14/result.md) what keeps repo outside clearing | descriptive | The uncleared segment held (dealers' uncleared reverse repo $0.9tn → $1.6tn; share 60% → 57%) while sponsored clearing grew; uncleared repo and reverse repo are 80–84% matched (netted packages; mostly zero haircut per the OFR); trades enter clearing at each year-end (G-SIB) and leave again. |
| [15](results/study-15/result.md) corporate bonds in repo and in panics | descriptive | Corporate collateral is small (dealers' repo $70bn → $167bn, 4.7% of corporate plus Treasury) but grew faster than Treasury repo; no visible pullback in March 2020 (+12%, as the Fed opened its dealer facility); when Treasuries fail as a haven in a panic, Baa yields rise too on 89% of days [83, 94], and on 46% of all panic days since 2020 against 18% in 2008–19. Two design amendments, the second after a data artefact was seen. **2008 extension:** in the old report format, dealers' financing against corporate securities fell 42% from mid-2007 to after Lehman, against −17% for Treasuries: a run on private collateral, visible. |
| [16](results/study-16/result.md) data-centre debt and swaps | descriptive + test | Six data-centre builders' debt $239bn → $334bn in a year (capital spending $233bn → $389bn); Microsoft leases rather than borrows. Long-dated swap volume around their 14 bond deals: +6% [−16%, +30%], not heavier, so the Dallas Fed's suggested AI-swap channel is not visible in public trade volume. One amendment, after results, fixing how two companies' figures were read. |
| [17](results/study-17/result.md) milder spikes and the creep | test | Ordinary month-ends no milder in 2025–26 than 2018–19 (−0.6 bp [−3.9, +2.8]; equal at equal tightness). Post hoc: the gap is in quarter-ends, mainly year-end 2018 (+62 bp); the worst turn since the standing repo facility is 22 bp above its rate vs 65 bp before, a leaky ceiling. Addendum: since full allotment (Dec 2025) SOFR has not closed above the facility's line in 2026 (0 of 203 days) but SOFR99 has on 12% of days. The 2022–25 creep: 82% accounted for by the ON RRP drain, then reserves. B2 uninformative (design flaw, stated). |
| [18](docs/design-study-18-year-end-2026.md) year-end 2026, set down in advance | test, pending | Frozen code and forecasts (benchmark held, top 1% breached, milder than 2025) for the turn that combines full allotment, the cash-clearing deadline and the G-SIB snapshot. Scored after the fifth business day of 2027. |
| [19](results/study-19/result.md) who pays above the line | test | Since full allotment, SOFR99's breaches of the facility's rate sit outside tri-party (TGCR also above on 22.9% of breach days); facility take-up median $0 on breach days. Post hoc: two kinds of day, pressure days with heavy take-up, and quiet 1–5 bp DVP premia with none (all breaches since April 2026). |
| [20](results/study-20/result.md) full allotment vs bill purchases; the threshold | test | Since full allotment, month-end jumps roughly halved (9.5 → 4.9 bp) while ordinary days got tighter, not looser; at equal tightness −6.7 bp [−12.3, +1.3], no detectable difference. The scarcity threshold disappears when reserves are measured against federal debt held by the public: about 10% in both scarce regimes (10.1% vs 9.6%), against +21–25% on bank assets or GDP. |
| [21](results/study-21/result.md) the reserves-to-debt gauge, prospective | test, pending | Frozen code: from Nov 2026 to Dec 2027, scarce-zone months (gauge < 10%) should show ordinary-day repo above −15 bp and month-end jumps above +3 bp; ample months (≥ 11%) neither. Gauge on the watch: 9.3% (scarce) in the week of 21 Oct 2026. |
| [22](results/study-22/result.md) which denominator | test | It is the debt, however counted: debt held by the public, total public debt and reserves + TGA over debt all match the two scarce regimes (95–104%); GDP, bank assets and repo volume do not. Debt held by the public not beaten. |
| [23](results/study-23/result.md) the dealer markup | test | SOFR99 − TGCR99 widens at quarter-ends (+11.6 bp [5.3, 20.8]; year-ends ~31 bp); unchanged by full allotment; ~0 on the floor, ~7 bp when scarce; no narrowing as sponsored clearing grew. A balance-sheet price. |

Every study keeps to the rules below. The watch ([`scripts/watch.py`](scripts/watch.py), run every Monday
by [`.github/workflows/watch.yml`](.github/workflows/watch.yml)) shows the eight flags fixed in study 07's design,
study 10's tests and study 12's candidates. It scores nothing itself.

## Next steps

In order of value:

1. **Read the deadline results as they come.** Study 10A scores the cash-clearing deadline once data runs to the end
   of January 2027, and the repo deadline after September 2027. Nothing to build; the weekly run does it.
2. **Study 13 (when the data is public): uncleared bilateral repo.** The OFR's new collection on non-centrally cleared
   bilateral repo would show where leverage sits outside clearing, and its haircuts. The New York Fed reports that 75%
   of these Treasury trades carry a zero haircut, and that only about 30% of hedge-fund repo with dealers was cleared
   by late 2025. The collection is not yet in the OFR's public data feed. Check it quarterly; write the design before
   the first download.
3. **Done (26 Oct 2026): the migration still to come is on the watch.** Study 07 measured money funds' side of
   clearing. The larger move is the dealer-to-hedge-fund side. The watch now shows, each quarter, FICC sponsored repo
   (the hedge-fund borrowing leg) over hedge funds' Form PF repo borrowing: about 8% in 2021 and 31% in Q2 2026, 6
   points above a year earlier (it jumps each fourth quarter; study 13), close to the New York Fed's figure from non-public data (about 30% in late 2025). It is a proxy;
   its trend toward the June 2027 deadline is what to read. Building it showed that study 10's descriptive A5 used
   the money-fund leg instead; that is recorded as an erratum in its design, and A5 decides nothing.
   **Added (26 Oct 2026):** a weekly reading from study 14, the share of primary dealers' Treasury reverse repo left
   uncleared, compared with the same weeks a year earlier. First reading: 55.4% in the four weeks to 14 October 2026,
   against 54.2% a year earlier. Eight months before the repo deadline, the uncleared share is no lower than a year ago.
4. **Keep the two candidate indicators honest.** Top-10 hedge-fund leverage and low long-run VIX are scored on future
   stress only. Re-score them once three new stress events, by study 12's mechanical definition, have occurred. Do not
   re-tune them in between.
5. **Reconcile the size of the repo market in the record.** Our "repo liabilities, all collateral" (Financial
   Accounts, 22% of GDP) is a narrower measure than the OFR's $13.5 trillion outstanding across all segments (about 40%
   of GDP). Study 02's
   comparisons with 2007 stand, since both dates use the same measure, but readers should see both figures. Done in
   [`SYNTHESIS.md`](SYNTHESIS.md); nothing else to change.

Out of scope unless someone pays for the data: intraday Treasury liquidity, the MOVE index, futures prices and
cross-currency basis.

## Data

| Source | Gives | Status |
|---|---|---|
| repo-market-model panel | the daily repo spread and calendar, pinned and digest-checked | in use |
| FRED | rates, spreads, yields, Financial Accounts, NFCI, GDP, VIX, equities | in use |
| OFR (stress index, Hedge Fund Monitor / Form PF, Short-term Funding Monitor) | hedge-fund repo, Treasury and derivative exposure, leverage and liquidity by strategy and size; money-fund repo by counterparty; cleared repo volumes; sponsored repo | in use |
| CFTC Traders in Financial Futures | leveraged funds' Treasury futures positions: the basis-trade proxy | in use |
| DTCC public swap reports | SOFR swap trades: daily swap rates and spreads, package shares; rolling two-year window, so derived series are committed | in use |
| US Treasury (Monthly Statement of the Public Debt, Fiscal Data) | marketable debt held by the public | in use |
| TIC Table 5 (`ticdata.treasury.gov`) | Cayman Islands Treasury holdings, last 13 months only | in use |
| Federal Reserve Board excess bond premium | credit risk appetite | supplied by hand: the site refuses automated downloads from this environment |
| SEC N-MFP, FINRA TRACE aggregates | fund-level money-fund detail; Treasury trading volumes | reachable, not used |
| OFR non-centrally cleared bilateral repo collection | uncleared repo: volumes, haircuts, counterparties | not yet public |
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

1. **Scope:** all five claims, H1–H5.
2. **Network:** the CFTC, DTCC, FINRA, SEC and TIC hosts were added to the environment's network policy.
3. **Study 06 stress events:** widened beyond the NFCI onsets to named episodes since 2010. Claude fixes the list in
   study 06's design, before any indicator is scored against it.
4. **The watch:** study 07 runs on a schedule, and its page is public. Changed from monthly to weekly on 26 October
   2026 at her request; the flags still score complete months only.
5. **Audience:** the synthesis is written to be published.
6. **Review:** Claude merges each study's pull request itself once its checks pass; she does not review each one.
7. **Additions:** study 09 (debt and the safe haven, with household debt), study 11 (what hedge-fund repo funds) and
   study 12 (better indicators, including hedge funds' quarterly reports) were added at her request.
