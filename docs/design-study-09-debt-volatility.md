# Study 09: Treasuries in a panic — safe haven or source of stress?

Written on 26 October 2026, before this study's data was examined. Added to the plan at Eleonora's request, after study
02 found federal debt held by the public at 97% of GDP.

**Disclosed beforehand:**
- In March 2020 and April 2025, Treasuries sold off while equities fell. This is common knowledge and motivates the
  study.
- Study 04 found next-day repo pressure in 2025–26 larger after big *rallies* than after sell-offs.
- It is widely documented that stocks and bonds moved together (a positive correlation) in the higher-inflation
  1990s, and in opposite directions from about 2000 to 2021.

## Questions

1. **Haven:** as federal debt held by the public has risen relative to GDP, have Treasuries become less likely to
   rally when equity markets panic?
2. **Repo:** when Treasuries sell off in a panic instead of rallying, does repo come under more pressure than when
   they rally?
3. **Household debt** (added at Eleonora's request, 26 Oct 2026, before any of its data was examined): where does
   household debt stand against federal debt, and in panics does the mortgage–Treasury spread widen more when
   household debt is higher? Mortgages reach repo as agency mortgage-backed securities, the second-largest repo
   collateral after Treasuries.

## Data

- **Panic days:** VIX (FRED `VIXCLS`, 1990–).
- **Treasuries:** 10-year yield (`DGS10`).
- **Debt:** federal debt held by the public / GDP (`FYGFDPUN` / `GDP`, as in study 02).
- **Inflation:** CPI (`CPIAUCSL`), year-on-year, the control.
- **Repo:** SOFR − IORB from repo-market-model's pinned panel (2018–2026).
- **Household debt:** household credit-market debt (`CMDEBT`) / GDP, quarterly from 1945.
- **Mortgages:** the 30-year mortgage rate (`MORTGAGE30US`, Freddie Mac's weekly survey, Thursdays, from 1971). The
  mortgage–Treasury spread is that rate minus the 10-year yield on the same day, in bp.

## Definitions

- **Panic day:** VIX closes at least 15% above its previous close. The threshold is fixed, so the count varies over
  time.
- **Haven failure:** on a panic day, the 10-year yield rises (Δ10y > 0). Δ10y = 0 counts as not a failure.
- **Debt and inflation on a panic day:** the latest available month or quarter at that date.

## Tests

1. **Haven, main:** a linear probability model across panic days, 1990–2026:
   1{Δ10y > 0} = a + b·(debt/GDP, pp) + c·(CPI inflation, pp).

   The intervals come from a block bootstrap by calendar year (2,000 draws, seed 20261029), because panic days
   cluster.
   - **Supported** if b > 0 with its interval excluding zero.
   - **Not supported** if b's interval includes zero or b < 0.
2. **Haven, by era:**
   - for 1990–1999, 2000–2007, 2008–2019 and 2020–2026: the share of haven failures, and the mean Δ10y on panic days;
   - percentile intervals from day-level bootstrap.
3. **Repo, secondary:** in the panel period (2018-04 to 2026-09), on non-calendar days t following a panic day,
   excluding FOMC and IORB-change days:
   - the next-day change in SOFR − IORB after haven failures, against after haven rallies;
   - a difference with a bootstrap interval;
   - reported with its n, likely too small to decide anything.

4. **Household debt, part C:**
   - **Description:** household debt/GDP and federal debt/GDP at 2000, 2007, 2019 and today.
   - **Test:** weekly from 1990, on survey weeks. Δ mortgage–Treasury spread (this survey week minus the last) =
     a + b·panic + c·panic × (household debt/GDP, demeaned). "Panic" means a panic day fell between the two surveys.
     The interval is a block bootstrap by year (2,000 draws).
   - **Supported** if c > 0 with its interval excluding zero. The same model without 2007–2009 is reported beside
     it, because the housing crisis may drive any result alone.
   - **Repo:** agency MBS repo rates are not public daily, so the repo side of household debt is described, not
     tested.

## Limits

- **Confounding:** debt/GDP trends upward almost monotonically, so it is confounded with anything else that trended:
  globalisation, central-bank balance sheets, the term premium. Inflation is the one control the design fixes. A
  positive b is consistent with the debt story, not proof of it.
- **A narrow test:** VIX spikes are equity-market panics. Bond-market-led stress (2022's sell-off, the 2023 term-premium
  rise) is outside this test.
