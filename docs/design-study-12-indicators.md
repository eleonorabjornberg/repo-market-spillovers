# Study 12: looking for better warning indicators, without fooling ourselves

Written on 26 October 2026, before any candidate below was scored against any stress event. Follows Eleonora's
conclusion from study 06 ("if all our indicators were a coin flip, we need to find better indicators") and her question
about hedge funds' quarterly reports.

## The trap, and how this avoids it

With only eight episodes since 2017, trying indicators until one fits would find a "winner" by chance. So:

1. **Candidates are chosen in advance, each for a stated mechanism** from the research literature, not from the data.
   Their warning direction is fixed here.
2. **Longer history:** stress events from 1990 (22, listed below) instead of 8.
3. **A development period and a test period.** Everything is reported for both, but the verdict comes from the test
   period alone.
4. **No fitting.** The combined indicator is the plain average of the candidates' percentile scores: no weights, so
   nothing to overfit.
5. **Indicators that survive go into the monthly watch**, to be judged on events that have not happened yet.

**Already seen** (studies 02 and 06): the yield curve, the Baa − 10y spread and the NFCI against the 2017–2025 events.
Those three are the **benchmarks** here, not candidates. None of the candidates below has been scored against any
event.

## Candidates

All are monthly. Each reading uses only what was public at the time, with the publication lag stated.

| | Candidate | Mechanism | Series | Lag | Warning when |
|---|---|---|---|---|---|
| L1 | **Calm before the storm:** VIX's 12-month average | Long calm encourages leverage; low volatility precedes crises (the "volatility paradox": Danielsson, Valenzuela & Zer, 2018) | FRED `VIXCLS`, 1990– | none | low |
| L2 | **Excess bond premium** | The price of credit risk beyond expected default: investors' risk appetite (Gilchrist & Zakrajšek, 2012) | Federal Reserve, 1973– | 1 month | high |
| L3 | **Credit gap:** private credit/GDP minus its 40-quarter trailing mean | Fast credit growth precedes financial crises: the BIS's standard early-warning indicator, simplified to a trailing mean | FRED `CRDQUSAPABIS` / `GDP` | 1 quarter | high |
| L4 | **Dealer balance-sheet growth:** broker-dealer financial assets, 4-quarter growth | Dealer leverage is procyclical and compresses risk premia (Adrian & Shin, 2010) | FRED `BOGZ1FL664090005Q` | 1 quarter | high |
| L5 | **Bonds stop hedging stocks:** 60-day correlation of Nasdaq returns with Treasury returns (−Δ10y) | When bonds fall with stocks, the safe haven fails and balance sheets lose their hedge (study 09) | FRED `NASDAQCOM`, `DGS10` | none | high |

**Hedge funds' quarterly reports (Form PF via the OFR, from 2013):**

| | Candidate | Mechanism | Lag | Warning when |
|---|---|---|---|---|
| F1 | Share of hedge-fund repo borrowed by the 10 largest funds | Concentration: a few funds' distress moves the market | 2 quarters | high |
| F2 | Leverage of the 10 largest funds | Leverage at the top | 2 quarters | high |
| F3 | Relative-value funds' leverage, weighted by fund size | The Treasury relative-value trades of study 11 | 2 quarters | high |
| F4 | Liquidity mismatch: % of financing that can be pulled within 7 days minus % of portfolio sellable within 7 days | Runs happen when funding can leave faster than assets can be sold | 2 quarters | high |

**Benchmarks:** the 10y − 3m curve (low = warning), Baa − 10y (high) and the NFCI (high), as in study 06.

## Stress events, 1990–2025 (fixed here)

| # | Onset | Episode |
|---|---|---|
| 1 | 1990-08-02 | Gulf war and credit crunch |
| 2 | 1994-02-04 | Bond-market sell-off |
| 3 | 1997-10-27 | Asian crisis |
| 4 | 1998-08-17 | Russia default and LTCM |
| 5 | 2000-04-03 | Dot-com crash |
| 6 | 2001-09-17 | 9/11 |
| 7 | 2002-06-25 | WorldCom and the accounting crisis |
| 8 | 2007-08-09 | Start of the 2007 repo and asset-backed CP run |
| 9 | 2008-09-15 | Lehman |
| 10 | 2010-05-06 | Flash crash and first euro-area crisis |
| 11 | 2011-08-01 | US downgrade and second euro-area crisis |
| 12 | 2013-05-22 | Taper tantrum |
| 13 | 2014-10-15 | Treasury flash rally |
| 14 | 2015-08-20 | China devaluation |
| 15 | 2018-02-02 | Volmageddon |
| 16 | 2018-10-10 | Q4 2018 sell-off |
| 17 | 2019-09-16 | Repo spike |
| 18 | 2020-02-24 | COVID |
| 19 | 2022-09-23 | UK gilt crisis |
| 20 | 2023-03-09 | SVB |
| 21 | 2024-08-01 | Yen carry unwind |
| 22 | 2025-04-03 | Tariff shock |

## Scoring

1. **Label:** a month is positive if an onset falls in the next 6 months. 12 months is a secondary horizon.
2. **Score:** each month, each indicator's percentile in its own history up to that month, with at least 36 months of
   history (12 quarters for Form PF), and the warning direction applied.
3. **Composite:** the plain average of L1–L5's scores, over the months where all five exist.
4. **Periods:** development 1991–2012 (events 1–11); test 2013 to September 2025 (events 12–22).
5. **Main test:** on the test period, at 6 months, the composite's AUROC minus the yield curve's. The curve was the best
   benchmark in study 06, and is chosen here by that earlier evidence, not by this test. The interval is a block
   bootstrap by year: 2,000 draws, seed 20261102.
6. **Also reported:** each candidate's and benchmark's AUROC with its interval, both periods, both horizons. Form PF
   candidates are scored on the test period only (2016–), descriptively.

## What counts

- **A better indicator found:** the composite beats the curve on the test period, with the interval of the difference
  above zero.
- **Promising:** a single candidate whose test-period AUROC interval lies above 0.5. Promising candidates go into the
  watch.
- **Nothing better:** otherwise. That is a real finding, and would be reported as such.

## Limits

- **Timing:** onsets are hard to time by nature. Better indicators may still miss most of them, and the literature's
  successes are mostly at horizons of a year or more.
- **Events overlap:** 2007 and 2008, for instance, sit close together, and a 6-month label makes neighbouring months
  dependent. The yearly block bootstrap allows for some of this.
- **Form PF** history is short (about 10 events), and its two-quarter lag is a conservative guess at when each quarter
  became public.

## Amendment before scoring (26 October 2026)

The excess bond premium (L2) is published only on the Federal Reserve Board's website, which refuses automated
downloads from this environment. It is dropped. The composite is the plain average of L1, L3, L4 and L5. This was
decided before any candidate was scored. If Eleonora supplies the file, L2 can be scored separately and reported beside
the main test, which this amendment fixes.
