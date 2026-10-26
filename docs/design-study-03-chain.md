# Study 03: map of the chain (H1)

Written on 26 October 2026, before this study's series were fetched together or any of its ratios computed. Plan:
[`PLAN.md`](../PLAN.md), H1.

**Disclosed beforehand.** While scoping, a few levels were seen:
- hedge-fund repo borrowing: $1.15tn at end 2021, $3.38tn mid-2026;
- money-fund repo through FICC: $1.14tn of $2.87tn in Sep 2026;
- FICC sponsored repo volume: about $90bn in 2021, about $1.1tn in 2026;
- dealer Treasury positions: about $131bn in 2022, about $496bn in 2026;
- one CFTC row (Sep 2022, Treasury bond futures).

## Claim

**H1:** a larger share of the Treasury market than before rests on short-term repo funding, and the chain is
concentrated: leveraged funds borrow, money funds lend through FICC, and Treasuries are the collateral.

## Yardstick

**Privately held marketable Treasuries (PHMT)** = marketable Treasury debt held by the public (Treasury's Monthly
Statement of the Public Debt, table 1, monthly from 2001) − the Fed's Treasury holdings (FRED `TREAST`, weekly from
2002, monthly average). It is the stock the private market has to finance. Every size measure is divided by it.

## Measures

| | Measure | Source | From |
|---|---|---|---|
| M1 | Repo liabilities, all sectors and all collateral / PHMT | Financial Accounts `BOGZ1FL892150005Q` | 2002 |
| M2 | Hedge-fund repo borrowing / PHMT | OFR Hedge Fund Monitor `FPF-BORROW_REPO_SUM` (Form PF, qualifying hedge funds) | 2013 |
| M3 | Hedge funds' long and short Treasury exposure / PHMT | OFR `FPF-ASSETCLASS_LTREASURY_SUM`, `..._STREASURY_SUM` | 2013 |
| M4 | Leveraged funds' net short in Treasury futures, face value / PHMT | CFTC Traders in Financial Futures, futures only: 2Y ($200k face), 5Y, 10Y, Ultra 10Y, Bond, Ultra Bond ($100k face) | 2006 |
| M5 | Money-fund repo lending / PHMT, and its split by counterparty: FICC, Fed RRP, domestic and foreign financial institutions, other | OFR Short-term Funding Monitor `MMF-MMF_RP_*` | 2010 (FICC 2014) |
| M6 | FICC sponsored repo and sponsored reverse repo volume (FICC's labels), and both as a share of cleared DVP repo volume | OFR `FICC-SPONSORED_*`, `REPO-DVP_TV_TOT-P` | 2018–20 |
| M7 | Primary dealers' net Treasury positions / PHMT | repo-market-model panel (`dealer_treasury_position`), pinned | 2018 |

M4 is the standard public proxy for the cash–futures basis trade. A leveraged fund short futures is typically long
cash Treasuries financed in repo. It is a proxy: not every short is a basis position.

**Concentration:**
- **C1:** FICC's share of money-fund repo lending.
- **C2:** the Herfindahl index of money-fund repo across private counterparty types (FICC, domestic, foreign, other).
  The Fed's RRP is excluded, because its swings in 2021–23 reflect policy, not market structure.

**Monthly conversion:** daily and weekly series are averaged within the month; quarterly series are carried to the
three months of their quarter.

## Snapshots

June of 2007 (where a series exists), 2014, 2019 and 2026 (the latest month common to the quarterly series), plus each
series' latest complete month and its value at its own peak.

## What counts

- **H1 supported** if both hold:
  - **(a) size:** M2 and M4 in June 2026 are in the top decile of their own history and above June 2019;
  - **(b) concentration:** C1 and C2 in June 2026 are above June 2019.
- **Partly supported** if one of (a) and (b) holds.
- **Not supported** if neither holds.

M1, M3, M5, M6 and M7 are reported as context and do not decide the verdict.

## Limits

- **Comparison with 2007:** M1 counts repo against every kind of collateral, so its 2007 level includes private
  mortgage-backed collateral, and it is not a Treasury-only figure. The Treasury-specific measures (M2, M3, M6) start
  in 2013–20, so the record cannot say how this compares with 2007.
- **Form PF** covers qualifying hedge funds only, reported quarterly with a lag.
- **M4** counts futures face value, not risk: durations differ across contracts.
- **FICC's sponsored labels** are FICC's own; which side is cash lending is described as FICC states it, not
  inferred.
