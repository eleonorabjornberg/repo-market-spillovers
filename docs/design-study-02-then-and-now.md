# Study 02: then and now — does today's repo and bond market look like the run-up to 2000 or 2007?

Written on 26 October 2026, before the indicators below were computed. Disclosed beforehand: while checking which
series exist, the latest values of two of them were seen (the NFCI leverage subindex, +0.215, and the NFCI, −0.496,
on 16 Oct 2026), and the news around the 10-year yield (about 5.34% in early October 2026, its highest since 2002).

## The question

Is there a broader context, like the run-up to the dot-com bust or to 2008, in which today's repo and bond market
shows warning signs? And would those signs have told us anything in the past?

The study does two things and keeps them apart:

1. **Then and now (descriptive).** Where each indicator stands today in its own history, set beside where it stood
   before past crises.
2. **Would it have warned (a check).** For each indicator with a warning direction: when it was as extreme as it is
   today, how often did stress follow? This is the part that can say "no". With a handful of crises in the record,
   it is a sanity check, not a forecast.

## Indicators

All public, from FRED unless marked. Monthly: daily and weekly series averaged within the month; quarterly series
carried to each month of their quarter.

| Group | Indicator | Series | From | Warning direction |
|---|---|---|---|---|
| Repo and funding | Repo liabilities, all sectors, % of GDP | BOGZ1FL892150005Q / GDP | 1945 | high |
| | Hedge-fund repo borrowing, % of GDP | OFR Hedge Fund Monitor FPF-BORROW_REPO_SUM / GDP | 2013 | high |
| | Reserves, % of GDP | TOTRESNS / GDP | 1959 | low |
| | 3-month financial CP − 3-month bill (bp) | DCPF3M − DTB3 | 1997 | high |
| | TED spread (bp; ended Jan 2022) | TEDRATE | 1986 | high |
| | OFR FSI, funding category | OFR | 2000 | high |
| Leverage and conditions | NFCI leverage subindex | NFCILEVERAGE | 1971 | high |
| | NFCI | NFCI | 1971 | (the stress definition) |
| Bond market | 10-year term premium (Kim–Wright) | THREEFYTP10 | 1990 | none (both ends have been read as warnings) |
| | 10-year − 3-month curve (bp) | T10Y3M | 1982 | low (inversion) |
| | Baa − 10-year (bp) | BAA10Y | 1986 | high |
| | Federal debt held by the public, % of GDP | FYGFDPUN / GDP | 1970 | high |
| | 10-year yield (%) | DGS10 | 1962 | none |

## Reference dates

- **Dot-com:** March 2000 (Nasdaq peak).
- **GFC, repo run:** July 2007, the month before BNP Paribas froze its funds (9 Aug 2007) and asset-backed commercial
  paper and repo began to run.
- **GFC, peak:** August 2008, the month before Lehman.
- **Repo spike:** August 2019. **COVID:** February 2020.
- **Today:** the latest complete month common to the series.

## The check: would it have warned?

**Stress onset** is the first week the NFCI rises above 0 (tighter than average) after at least 26 weeks below 0.
It is defined on the NFCI alone, and fixed here before it is computed.

**Warning window.** For each indicator with a warning direction, take the months from 1990 on (or from the series'
start, if later) in which it was at least as extreme, in its warning direction, as it is today. Report:

- how many such months there were;
- the share followed by a stress onset within 24 months;
- the same share for all months.

If the share after warning months is not clearly above the share for all months, the indicator has not been a warning
sign at today's level. A trending series (repo/GDP, debt/GDP, hedge-fund repo) can be at its most extreme today with
no history behind that level. Its check then has nothing to say, and the table says so instead of reporting a ratio.

## What this cannot do

- **There are few crises.** The record since 1990 holds perhaps five or six stress onsets, so no indicator's track
  record is statistically established. The check can show an indicator *failed* to warn; it cannot show one works.
- **Crises differ.** 2000 was an equity bubble in which repo played little part. 2008 ran through repo, via
  asset-backed collateral and dealer balance sheets. Today's exposure sits in Treasuries financed in repo by leveraged
  funds. A then-and-now comparison shows resemblance, not mechanism.
- **Hindsight in the choice of indicators.** These were chosen knowing how 2008 went. The check is honest about each
  indicator's own history, not about the choice of indicators.
- **Data the public record lacks.** Bilateral uncleared repo haircuts, the cash–futures basis and swap spreads are
  missing here, and they matter. The basis trade proxy (CFTC positioning) is blocked in this environment until its
  hosts are allowed.
