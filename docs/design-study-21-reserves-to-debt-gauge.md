# Study 21: the reserves-to-debt gauge, tested on months that have not happened yet

Written on 27 October 2026. The code that scores it, `scripts/study_21_reserves_gauge.py`, is committed with this
design and frozen with it. The weekly watch runs it and shows the gauge.

**The claim under test** comes from study 20. Repo gets tight when reserves fall to about a tenth of federal debt held
by the public: 10.1% in 2018–19 and 9.6% in 2025–26, in equally tight months. That was found on data already seen.
This study tests it on months to come.

**Already known** (from study 20 and a quick look reported in conversation, not in a result file): the ratio has been
about 9.3–9.7% in every month of 2026, and was 12–19% on the floor in 2021–23.

## The gauge

- **Weekly:** reserves (`WRESBAL`, $ millions) over federal debt held by the public (`FYGFDPUN`, $ millions, the latest
  quarter published by the week's date), in %.
- **Monthly:** the mean of the weekly gauge.
- **Zones:**
  - **scarce** below 10%;
  - **ample** at or above 11%;
  - **no call** in between.

## Predictions

For every month from November 2026 to December 2027 whose zone is scarce or ample, the gauge predicts two things.
Each uses study 17's measures: ordinary-day tightness `B` (median of SOFR minus the top of the target range, business
days 6–15) and the month-end jump `J`, both in bp, with every month kept.

- **Scarce month:** `B` above −15 bp, and `J` above +3 bp.
- **Ample month:** `B` at or below −15 bp, and `J` at or below +3 bp.

A month matches if both hold.

These thresholds sit between the regimes study 17 measured:
- `B` averaged −20.5 bp on the floor and −6.5 to −12.9 bp in the scarce years;
- month-end jumps averaged about +1 bp on the floor and +5 to +10 bp when scarce.

## Verdict

Scored once at least 6 zone months are complete, and finally after December 2027:
- **the gauge holds** if at least 75% of zone months match;
- **the gauge fails** if 50% or fewer match;
- **inconclusive** in between, or with fewer than 6 zone months.

The share of months in each zone is reported. If every month is scarce, only half of the claim is tested, and the
result says so.

## Limits

- **The standing repo facility now caps pressure** (study 20), so scarcity may show less in rates than in 2018–19.
  The thresholds allow for this only roughly.
- **Debt held by the public is quarterly** and published with a lag, so the gauge moves in steps.
- **Rate cuts, the clearing deadlines and bill purchases** all fall in the window. A match is consistent with the
  gauge, not proof of it.
