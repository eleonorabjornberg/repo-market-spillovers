# Study 15: corporate bonds in repo, and in a stock-market panic — result

Design: [`docs/design-study-15-corporate-bonds.md`](../../docs/design-study-15-corporate-bonds.md), committed before the
data was fetched, with two amendments. The second was written **after** a first result was seen, which turned out to be
a data artefact; the amendment says so. Every figure is read from [`result.json`](result.json).

## In one line

Corporate bonds are a small part of repo: about 5% of dealers' repo against corporate bonds and Treasuries. They are
not where the leverage is. They matter for a different reason. On stock-market panic days when Treasuries fail as a
haven, corporate bond yields rose too on 89% of days [83, 94]. Since 2020 that case has become common, so holders of
corporate bonds have had no offset just when they would need one.

## 1. How much repo rests on corporate bonds? Not much (verdict: small; grew faster than Treasury repo)

Primary dealers' repo against corporate debt and against Treasuries, from the New York Fed's weekly totals. The
corporate totals agree with the OFR's copy of the same data within 1% in 99.7% of the weeks of 2015–2021.

| | First 13 weeks (Apr–Jun 2013) | Last 13 weeks (2026) |
|---|---:|---:|
| Dealers borrow cash against corporate bonds (repo) | $70bn, 3.9% | **$167bn, 4.7%** |
| … against Treasuries | $1,733bn | $3,365bn |
| Dealers lend cash against corporate bonds (reverse repo) | $19bn, 1.3% | $48bn, 1.6% |
| … against Treasuries | $1,460bn | $3,020bn |

Shares are of corporate plus Treasury. Corporate repo grew 138% against Treasury repo's 94%, so it grew faster, from a
small base. Most of it is dealers borrowing cash against their own corporate bond holdings: in the latest weeks about
70% of that sat in tri-party repo (the venue split exists only from July 2024). Dealers lend little cash against
corporate bonds: 1.6% of their reverse repo, the rest against Treasuries.

## 2. Did lenders pull back from corporate collateral in March 2020? No (verdict: not supported)

Change from the four weeks to 26 February 2020 to the four weeks from 18 March 2020:

| | Corporate | Treasury |
|---|---:|---:|
| Dealers' repo (borrowing cash) | **+11.9%** | +11.6% |
| Dealers' reverse repo (lending cash) | +18.7% | +16.5% |

Dealers' corporate repo **rose** in March 2020, in step with their Treasury repo. But the second window opens the day
after the Fed announced its Primary Dealer Credit Facility (17 March 2020). It lent to dealers against collateral that
included investment-grade corporate bonds, and dealers' repo totals may include it. The data cannot separate private
lenders from the Fed. So the honest reading is that lenders did not visibly run, and the Fed was standing behind the
dealers when they might have.

**April 2025** (four weeks to 2 April against four from 9 April, reported without a verdict): corporate repo was flat
(−0.3%), while Treasury repo grew 9.3%.

## 3. On panic days, do corporate bonds fall when Treasuries do? Yes (verdict: no offset)

Panic days follow study 09's rule (VIX up at least 15% in a day), from 1990: 260 days with both yields observed.

| | Days | Baa yield rose | Mean change, 10-year | Mean change, Baa |
|---|---:|---:|---:|---:|
| Treasuries failed as a haven (10-year yield rose) | 71 | **88.7%** [83.3, 94.2] | +7.6 bp | +6.7 bp |
| Treasuries worked as a haven | 189 | | −7.3 bp | −3.8 bp |

**By era:**

| Era | Panic days | 10-year yield rose | Baa yield rose |
|---|---:|---:|---:|
| 1990–1999 | 41 | 58.5% | 63.4% |
| 2000–2007 | 32 | 21.9% | 31.2% |
| 2008–2019 | 115 | 13.9% | 18.3% |
| 2020–2026 | 72 | 33.3% | **45.8%** |

Corporate bond yields are anchored to Treasury yields. When Treasuries rally in a panic, corporate yields fall too,
though by about half as much, so even a rally leaves corporate bonds behind. When Treasuries sell off, corporate bonds
sell off with them in nine panics out of ten. On 12 March 2020 the 10-year yield rose 6 bp and the Baa yield 27 bp.
Since 2020, corporate bond yields have risen on nearly half of panic days, against fewer than one in five in 2008–19.

## What this means for the question asked

If a crisis started outside repo, in a stock-market bust:
- **Repo's own exposure to corporate bonds is small.** About $167bn of dealers' repo rests on corporate collateral,
  against about $3.4 trillion on Treasuries. A run on corporate collateral like the one on private collateral in 2008
  would hit a small corner, not the core.
- **Corporate bonds would not cushion a bust.** Their yields go where Treasury yields go. When Treasuries are a haven,
  corporate bonds gain a little; when they are not, corporate bonds lose too. Study 09 found the second case has become
  more common since 2020, with inflation.
- **So the repo market's ability to cushion depends on Treasuries,** as in studies 04 and 09. In March 2020 the Fed
  stood behind both Treasuries and dealers' corporate financing.

## Limits

- **Dealers only,** and their repo is partly their own choice: a rise can be dealers financing inventories they could
  not sell.
- **One stress episode** in the repo data, and it overlaps the Fed's emergency lending.
- **Moody's Baa is an index of long, seasoned bonds,** priced slowly. Q3 uses its yield level. Its spread over
  Treasuries widens mechanically when Treasury yields fall, which is why the spread is not the test.
- **Nothing here forecasts a crisis or says an AI bust is coming.** It describes what happened in past panics.
- **2008 is out of reach:** the repo data start in 2013. Published research (Gorton and Metrick, 2012; Copeland,
  Martin and Walker, 2014) found the run on repo in 2008 hit private collateral hardest.
