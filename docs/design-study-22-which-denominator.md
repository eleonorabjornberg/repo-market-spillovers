# Study 22: what should reserves be measured against?

Written on 27 October 2026, before this study's new data was fetched. Study 20 found the threshold at which repo gets
tight matches across 2018–19 and 2025–26 when reserves are measured against federal debt held by the public, but not
against bank assets or GDP. Three ratios were tried and one matched, which could be chance. This study fixes a longer
list in advance and asks which fits best.

**Already known:** study 20's three ratios, and a quick look across all months. The debt ratio and repo tightness are
correlated −0.57 over 2018–2026, with 2020's emergency months left out.

## Denominators, fixed now

1. federal debt held by the public (`FYGFDPUN`), study 20's match;
2. total public debt (`GFDEBTN`);
3. SOFR volume, the size of the repo market itself (New York Fed, daily, monthly mean);
4. GDP (`GDP`);
5. commercial-bank total assets (`TLAACBW027SBOG`);
6. reserves plus the Treasury's cash account at the Fed (`WRESBAL` + `WTREGEN`) over debt held by the public. The
   Treasury's account swings with tax dates and drains reserves when it rises, so this asks whether the cash both sides
   hold is what matters.

All quarterly series use the latest quarter at or before the month. Daily and weekly series use monthly means.

## Tests

Months as in study 17: all months, emergency months March–December 2020 left out. `S` is the monthly mean of SOFR minus
the top of the target range.

- **T1, the match (study 20's test, repeated).** For each ratio, the 2025–26 median as a percentage of the 2018–19
  median in comparable months, those whose ordinary-day tightness lies in the range both regimes covered. A ratio
  **matches** within ±10%.
- **T2, the fit.** For each ratio, the correlation between the monthly ratio and `S` over all months, with a block
  bootstrap interval by year (2,000 draws, seed 20261030).
- **Verdict.** The **best denominator** is the one that matches in T1 and has the most negative correlation in T2.
  If no ratio matches, or the best correlation's interval overlaps that of debt held by the public, the verdict is
  **debt held by the public is not beaten**. Each result is reported, and six tries are counted as six.

## Limits

- **Six candidates** raise the chance that one fits by luck. Reporting all six is the guard.
- **Correlation over time** is mostly shared trends, so T2 shows fit, not cause.
- **SOFR volume** grows partly because repo moved into the measured segments, especially sponsored clearing. It is
  not a clean measure of need.
