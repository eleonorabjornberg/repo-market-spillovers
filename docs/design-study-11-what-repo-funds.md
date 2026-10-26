# Study 11: what is hedge-fund repo funding now that the basis trade has shrunk?

Written on 26 October 2026, before this study's data was fetched (the DTCC package counts, the OFR strategy, derivative
and holdings series). Descriptive: it narrows down explanations and tests no prediction. Plan:
[`PLAN.md`](../PLAN.md). It follows Eleonora's question about the co-moving charts on the watch.

**Known beforehand (studies 03 and 07):**
- hedge-fund repo borrowing held near a record (12.7% of private Treasuries in June 2026);
- leveraged funds' net Treasury futures short fell from $1.15tn (October 2024) to $0.80tn (September 2026);
- hedge funds' long and short Treasury exposure (Form PF) were seen through June 2026: long 8.9%, short 5.6% of
  private Treasuries.

## The question

Since late 2024, hedge funds' repo borrowing has stayed near its record while the classic cash–futures basis trade has
shrunk. What is the repo funding instead? Four candidate explanations, each with what would point to it:

| | Explanation | Points to it if, from 2024 Q3 to the latest quarter |
|---|---|---|
| E1 | **Swap-spread trades:** long Treasuries in repo, hedged by paying fixed on SOFR swaps instead of selling futures | (a) the share of new SOFR swap notional traded as packages rose, *and* (b) hedge funds' interest-rate derivative exposure grew while the futures short fell |
| E2 | **Directional bets by macro funds** | macro funds' share of the growth in hedge-fund borrowing exceeds relative-value funds' |
| E3 | **The arbitrage continues in another form** (relative-value funds) | relative-value funds' share of the growth in borrowing exceeds macro funds' |
| E4 | **Not Treasuries at all:** repo against other collateral | hedge-fund repo borrowing grew faster than their long Treasury exposure |

More than one can hold. The study reports which do; it does not pick one.

## Data

- **DTCC public swap reports (E1a),** November 2024 onwards: new USD SOFR OIS trades (`Action type` NEWT, `Event
  type` TRAD), spot-starting (effective at most 5 days after execution), tenor 2 to 31 years. They are counted by month,
  by tenor bucket (2–5, 5–12 and 12–31 years) and by `Package indicator`, with total notional.

  **E1a's measure:** the monthly share of notional traded as a package, its first three months against its last three.
  "Rose" means up by at least 5 percentage points. A package bundles the swap with another trade, typically a Treasury
  for a swap-spread trade, but also curve trades and other swaps, so the share is a proxy.
- **OFR Hedge Fund Monitor (Form PF, quarterly).**
  - **E1b:** interest-rate derivative gross notional exposure (`FPF-ASSETCLASS_IRD_GNE_SUM`, long and short). It
    counts as grown if its latest quarter exceeds 2024 Q3 by at least 10%. Leveraged funds' futures short is from the
    CFTC (study 03).
  - **E2 and E3:** borrowing by strategy (`FPF-STRATEGY_{RV,MACRO,MULTI,...}_BORROWING_SUM`) and gross notional
    exposure by strategy. The measure is each strategy's share of the change in total borrowing from 2024 Q3 to the
    latest quarter. Form PF's borrowing by strategy is total borrowing, not repo alone, so this is a proxy.
  - **E4:** repo borrowing (`FPF-BORROW_REPO_SUM`) against long Treasury exposure (`FPF-ASSETCLASS_LTREASURY_SUM`),
    each as a growth ratio, latest quarter over 2024 Q3. It points to E4 if repo grew by at least 5 percentage points
    more.
- **TIC, Cayman Islands holdings of Treasuries (monthly):** the usual proxy for hedge funds' holdings. It needs
  `ticdata.treasury.gov`, which this environment blocks. It is reported if that host becomes reachable, and decides
  nothing.

## Limits

- **Granularity:** aggregate data shows what kind of trade, not who.
- **Lags:** Form PF is quarterly and about two quarters behind.
- **Proxies:** DTCC packages are a proxy for swap-spread trades. Borrowing by strategy covers all borrowing, not repo
  alone.
- **The best source is missing:** the OFR's new collection on uncleared bilateral repo is not yet in its public data
  feed.
