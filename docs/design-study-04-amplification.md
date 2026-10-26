# Study 04: do Treasury-market shocks spread into repo? (H2)

Written on 26 October 2026, before this study was run. Plan: [`PLAN.md`](../PLAN.md), H2.

**Disclosed beforehand.** An exploratory probe (not committed) was run while scoping. Its definition: top 5% of |Δ10y|
on day t−1 within each regime, non-calendar day t, next-day change in SOFR − IORB. Its results were:

| Regime | Extra next-day Δspread (bp) | 95% interval |
|---|---:|---|
| 2025–26 | +1.11 | [0.16, 2.12] |
| floor 2021–23 | 0.00 | |
| transition 2024 | −0.57 | |
| 2018–19 | −2.17 | [−5.48, 0.27] |

Top-5% rises in the OFR stress index gave nothing in any regime. This design is written knowing those numbers. It keeps
the probe's definition as the main test, and so cannot claim the main test as independent confirmation; the placebo,
the replication and the dose–response check are what can add evidence.

The case days were also seen in the probe: 2025-04-08 (+7 bp after the 10-year rose 14 bp on 2025-04-07), and
March 2020.

## Claim

**H2:** shocks in the Treasury market now spread into repo the next day, more so as the leveraged repo chain behind
Treasuries has grown (study 03: hedge-fund repo from 9.4% to 12.7% of private Treasuries, 2019–2026).

## Data

- **Repo:** repo-market-model's panel at the pinned commit and digest (`metadata/parent_pin.json`), 3 Apr 2018 – 3 Sep
  2026.
- **Treasury market:** 10-year yield, FRED `DGS10`; the volatility category of the OFR financial stress index.
- **Leverage:** hedge-fund repo as a share of private Treasuries, from study 03 (quarterly, Form PF).

## Definitions

**Days:** panel business days.
- **Outcome day t:** not a calendar day (no `month_end`, `month_start`, `quarter_end`, `coupon_settle` or `tax` label,
  as in study 01), and not an FOMC or IORB-change day.
- **Shock day:** the panel business day before t.

**Shocks:**
- **S1 (main):** day t−1 is in the top 5% of |Δ10y| within its regime.
- **S2:** day t−1 is in the top 5% of rises in the OFR stress index's volatility category within its regime.

**Outcomes:**
- **Y1 (main):** the next-day change in SOFR − IORB, spread(t) − spread(t−1), in bp.
- **Y2:** the three-day change, spread(t+2) − spread(t−1). Days t, t+1 and t+2 must all be non-calendar and
  non-excluded.
- **Y3:** the next-day change in the 75th percentile of SOFR minus IORB (`sofr_p75`), the upper part of the repo rate
  distribution.

**Regimes:** as in study 01: `scarce_2018_19`, `floor_2021_23`, `transition_2024`, `scarce_2025_26`, plus
`covid_2020`, which is reported but not compared.

**Effect:** mean outcome after shock days − mean outcome on other eligible days, in each regime. Intervals are 95%
percentile bootstrap: 5,000 draws, seed 20261027, shock and other days resampled separately.

## Tests

1. **Main:** S1, Y1, `scarce_2025_26` − `floor_2021_23`, a difference in differences.
2. **Replication:** the same contrast for `scarce_2018_19` − `floor_2021_23`.
3. **Placebo:** the main test with each shock date moved 10 business days later, and again 10 earlier. Shock days
   that land on excluded or calendar days are dropped.
4. **Dose–response:** over all eligible days from 2018 to 2026, excluding `covid_2020`, regress Y1 on:
   - |Δ10y(t−1)|;
   - hedge-fund repo % of private Treasuries in t's quarter (study 03's M2, demeaned);
   - the product of the two.

   A positive coefficient on the product means bond moves feed repo more when hedge-fund repo is larger. Its
   interval comes from 2,000 day-level bootstrap draws.
5. **Direction:** S1 split by the sign of Δ10y (sell-off versus rally), for 2025–26.
6. **Cases:** day by day from three days before to three days after, around 2020-03-12 to 2020-03-18 and
   2025-04-03 to 2025-04-11.

## What counts

- **H2 supported:** the main test is positive with its interval excluding zero; both placebos have intervals that
  include zero; the replication has the same sign; and the dose–response product coefficient is positive with its
  interval excluding zero.
- **Supported for 2025–26 only:** as above, but the replication has the other sign or the dose–response interval
  includes zero.
- **Not supported:** the main test's interval includes zero, or a placebo is as large as the main effect.

## Limits

- **Few shock days:** about 20 per regime, so only large effects show, and the main test is not independent of the
  probe.
- **Common drivers:** large yield moves and repo pressure can share a cause (a Treasury refunding, a data surprise,
  a policy signal). Next-day timing helps but does not settle direction.
- **Daily closes:** whatever happens within a day is invisible.
