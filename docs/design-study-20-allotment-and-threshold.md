# Study 20: full allotment or bill purchases? And why repo now gets tight with more reserves

Written on 26 October 2026, before this study's new data was fetched and before any of its measures were computed. It
follows two loose ends in study 17:
- **The confound.** Since January 2026 the benchmark repo rate has not closed above the standing repo facility's
  rate. But full allotment and the Fed's bill purchases began in the same week of December 2025.
- **The threshold.** Repo reached the same tightness in 2025–26 with reserves of 11.4–14.4% of bank assets as it did
  in 2018–19 with 8.6–12.3%.

**Disclosed beforehand.**
- **Seen:** all of study 17, including its month-end jumps for every month to September 2026, and its yearly reserve
  ratios. Also study 19's breach-day counts.
- **Not computed before this design:** any comparison of months before and after full allotment, and any ratio of
  reserves to GDP or to Treasury debt.

## Part A: full allotment or the bill purchases?

**The idea.** Bill purchases add reserves, so they should loosen repo on ordinary days. That shows up as a lower
ordinary-day tightness `B`, study 17's median of SOFR minus the top of the range on business days 6–15. Full allotment
works at the moments of pressure, so it should shrink month-end jumps `J` at a given `B`.

Comparing jumps at equal ordinary-day tightness therefore nets out the reserves channel, as far as `B` captures it,
and leaves the facility's.

**Months.**
- **Before:** every month of `scarce_2025_26` up to November 2025.
- **After:** December 2025 to the latest month whose turn has data.

December 2025 counts as after because its turn days fall after 11 December. All months are kept, including those with
a rate change. That is safe for this measure because SOFR moves with the range, as study 17's post hoc check showed.

**A1, did ordinary days loosen?** The mean of `B` after, minus before, with a bootstrap interval that resamples months
within each group (2,000 draws, seed 20261029). Reported, no verdict. A fall is consistent with the bill purchases.

**A2, are jumps smaller at equal tightness?**
- **Model.** `J = a + b·B + c·quarter-end + d·after`, fitted on the before and after months.
- **Verdicts on `d`:**
  - **smaller after full allotment** if the upper bound of its interval is below zero. That points to the facility.
  - **no detectable difference** if the interval includes zero. Any calm then is not shown to be the facility's; the
    bill purchases, through `B`, remain the simpler account.
  - **larger** if the lower bound is above zero.

**A3, the turn days (descriptive).** The largest SOFR minus the top of the range on any turn day, before and after.

## Part B: why repo now gets tight with more reserves

**The idea.** "Scarce" depends on what reserves are measured against. If reserves measured against the size of the
Treasury market, or the economy, look the same in the two scarce regimes, the threshold has not moved. Reserves have
only failed to keep pace with what they back.

**Ratios** of reserves (`WRESBAL`, monthly mean) to:
- (i) commercial-bank total assets (`TLAACBW027SBOG`), as in study 17;
- (ii) nominal GDP (`GDP`, quarterly, the latest quarter at or before the month);
- (iii) federal debt held by the public (`FYGFDPUN`, quarterly, the same way).

**Comparable months.** The months of each scarce regime whose ordinary-day tightness `B` lies in the range both
regimes cover. Study 17's rule applies: at least 5 months of each, or the comparison is reported as not possible.

**B1.** For each ratio, the median in comparable 2018–19 months and in comparable 2025–26 months, and the 2025–26
median as a percentage of the 2018–19 one.
- **The shift disappears under a ratio** if its 2025–26 median is within ±10% of the 2018–19 median.
- **The threshold has risen under every measure** if no ratio does.

If more than one ratio qualifies, all are reported. The one closest to 100% is named, without being treated as proven.

## Limits

- **About ten months after full allotment** with a turn in the data. Only a large effect on jumps could show.
- **`B` captures the reserves channel only partly.** If the bill purchases also calmed month-ends directly, A2 would
  credit the facility with part of that.
- **Other changes over the same months** include rate cuts and the clearing transition. They are not separated.
- **Ordinary-day tightness in 2019** was moved by the Fed's adjustments of the rate on reserves (study 17's limits).
  That makes B1's comparable months less clean for 2019.
- **Ratios are not causes.** A ratio under which the two regimes match is a description of the threshold, not an
  explanation of it.
