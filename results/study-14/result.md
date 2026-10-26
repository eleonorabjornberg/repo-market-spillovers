# Study 14: what keeps Treasury repo outside central clearing? — result

**Descriptive.** Design: [`docs/design-study-14-haircuts-netting.md`](../../docs/design-study-14-haircuts-netting.md),
committed before the data was fetched. It has one amendment, made after the first fetch and before any measure was
computed: confidentiality suppression meant early weeks were incomplete. Every figure is read from
[`result.json`](result.json); the weekly series is in [`weekly.csv`](weekly.csv).

- **Data:** the New York Fed's primary dealer statistics, weekly, January 2022 – October 2026, Treasury collateral
  excluding TIPS.
- **Haircut evidence:** cited from the OFR, not recomputed.

## In one line

Central clearing grew, but **the uncleared market grew with it**. What stays outside is a matched book of repo and
reverse repo that dealers already net among themselves, mostly at zero haircut. Clearing would add margin to those
trades without adding much netting, so they leave clearing again after each year-end.

## 1. The uncleared segment is holding, not shrinking

| Dealers' Treasury repo, 13-week averages | Early (first complete weeks) | Latest (Jul–Oct 2026) |
|---|---:|---:|
| Uncleared share of bilateral reverse repo (cash lent to clients) | 63.5% | 57.2% |
| Uncleared share of bilateral repo (cash borrowed) | 59.4% | 60.4% |
| Uncleared bilateral reverse repo | $1,133bn | $1,563bn |
| Sponsored (cleared) reverse repo | $203bn | $507bn |

**The two windows:**
- The main version's early window is the first 13 *complete* weeks, scattered between October 2022 and May 2024,
  because sponsored term buckets were suppressed for confidentiality.
- The sensitivity version treats suppressed values as zero and starts cleanly in January–March 2022. It gives an
  uncleared share of 60.0% → 57.2% and uncleared reverse repo of **$884bn → $1,563bn**, while sponsored reverse repo
  rose from $32bn to $507bn.

Both versions say "holding" (−6.3 and −2.8 points, against the design's 10-point bar). The growth of cleared repo has
been mostly *new* business, not trades moving out of the uncleared market.

## 2. A large matched book sits outside clearing

Dealers' uncleared repo and reverse repo against *specified* Treasuries are of similar size. The smaller is 84% of the
larger on average, 80% in the latest 13 weeks, against 71% in cleared specified and sponsored repo. That is the shape
of **netted packages**: a dealer finances a client's long bond and lends it a different bond to short, so the two
trades offset on the dealer's balance sheet without a clearinghouse.

- **Trend:** the matched share has not shrunk since 2023–24 (81% → 80%). In the sensitivity version it fell from 96%
  in early 2022, when cleared volumes were small.
- **What it can't show:** the data do not identify counterparties, so this bounds netted packages from above; it
  cannot count them.
- **Corroboration:** the OFR, using trade-level data, estimates that about 68% of hedge funds' reverse repo is netted
  this way.

## 3. Trades move into clearing at each year-end, then leave

| Year-end | Four weeks before | Last two weeks of December | Four weeks after |
|---|---:|---:|---:|
| 2023 | 65.2% | 58.4% | 62.2% |
| 2024 | 59.0% | 55.0% | 57.5% |
| 2025 | 51.7% | 47.2% | 55.9% |

Uncleared share of dealers' bilateral reverse repo. Year-end 2022 shows the same dip in the sensitivity version.

The uncleared share dips at every year-end, when banks' G-SIB capital surcharge is measured and netting through the
clearinghouse pays. It rebounds within weeks. This matches the OFR's account of the 2026 plateau. **Clearing is used
when it lowers dealers' capital charges, and abandoned when it doesn't.**

## Putting it together with the haircut evidence

The OFR's trade-level data for January–May 2025
([OFR, Aug 2025](https://www.financialresearch.gov/the-ofr-blog/2025/08/12/are-zero-haircut-repos-as-common-as-advertised/)):

| Finding | Figure |
|---|---:|
| Uncleared bilateral repo at zero haircut | 56% |
| Uncleared bilateral repo at a positive haircut | 34% |
| Uncleared bilateral repo at a negative haircut | 10% |
| Zero-haircut repo that is between affiliates | about half |
| Hedge-fund repo at zero haircut | 65% |

The OFR's [2026 analysis](https://www.financialresearch.gov/the-ofr-blog/2026/08/20/central-clearing-treasury-repos-plateaued/)
adds that hedge funds' reverse repos often carry negative haircuts, which FICC's margining struggles to accommodate.

**Answering the questions:**
- **Is it the haircuts?** In large part. The trades that stay outside clearing are the ones where clearing costs the
  most and adds the least: matched packages at zero or negative haircuts, which dealers already net.
- **Does it remove the risk?** Zero haircuts on offsetting trades are low-risk for the *dealer*. But if a client fails
  in a fast market, the dealer holds no cushion on either leg.
- **Avoiding reporting:** no sign of it. These trades are reported to the OFR by the dealers.
- **"Trust-me" (hold-in-custody) repo:** no sign of it. The pattern is netting, not custody.

**What it means for the June 2027 deadline:** the trades with the least incentive to move are the netted, zero-haircut
packages, and the trades between affiliates whose exemption the industry is contesting. The year-end pattern shows
these trades *can* be cleared when the economics say so. The question for the deadline is the margin they will carry
once they must.

## Limits

- **Primary dealers only.** Counterparties are not identified.
- **Matched-book ratio:** it bounds netted packages from above; it cannot count them.
- **Confidentiality suppression:** it affects the early weeks; both versions are reported.
- **Haircuts:** the levels are the OFR's (January–May 2025), not measured here.
