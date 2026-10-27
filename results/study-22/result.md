# Study 22: what should reserves be measured against? — result

Design: [`docs/design-study-22-which-denominator.md`](../../docs/design-study-22-which-denominator.md), committed
before this study's new data was fetched. Six denominators were fixed in advance. Every figure is read from
[`result.json`](result.json). Months April 2018 – October 2026, with March–December 2020 left out (93 months).
Comparable months, those equally tight on ordinary days, are 15 in 2018–19 and 20 in 2025–26.

## In one line

It is the debt, however it is counted. All three debt-based measures put the two scarce periods at the same level:
debt held by the public, total public debt, and reserves plus the Treasury's cash over the debt. None of the three
others does: GDP, bank assets, and the size of the repo market. Over time all six track repo tightness about equally
well, so the fit cannot choose between them. The match can.

## The six denominators

| Reserves as % of… | 2018–19 | 2025–26 | 2025–26 as % of 2018–19 | Match (±10%) | Correlation with repo tightness | 95% interval |
|---|---:|---:|---:|---|---:|---|
| Federal debt held by the public | 10.09 | 9.62 | 95.3% | **yes** | −0.57 | [−0.75, −0.22] |
| Total public debt | 7.43 | 7.73 | 104.1% | **yes** | −0.62 | [−0.75, −0.36] |
| Reserves + Treasury's cash, over debt held by the public | 11.97 | 12.32 | 102.9% | **yes** | −0.56 | [−0.72, −0.18] |
| GDP | 7.75 | 9.41 | 121.3% | no | −0.67 | [−0.77, −0.46] |
| Commercial-bank assets | 9.62 | 12.03 | 125.1% | no | −0.67 | [−0.79, −0.44] |
| SOFR volume (the repo market's size) | 163.7 | 99.6 | 60.9% | no | −0.53 | [−0.77, +0.12] |

**Verdict (pre-set): debt held by the public is not beaten.** Total public debt fits as well within the intervals,
and the three debt measures are within a few points of each other on the match.

## What it means

- **Every way of counting the government's debt gives the same threshold;** the economy and the banking system do not.
  That is the stronger version of study 20's finding, and less likely to be luck: three related measures agree, and
  three unrelated ones fail together.
- **Reserves now fall well short against the repo market's own size,** at 61% of 2018–19's ratio. Repo volume has
  grown faster than the debt, largely because trading moved into the measured, cleared segments. That is why the
  design warned it was not a clean measure of need.
- **Adding the Treasury's cash account changes nothing,** at 103%. The threshold is not an artefact of tax-date swings
  in that account.
- **Correlations over time do not discriminate,** because everything trended together over these years. The
  comparison of two equally tight periods does.

## Limits

- **Six tries.** Three matched, all from one family, which is reassuring rather than suspicious. Each was still tried
  on data already seen in part.
- **Two scarce periods** remain the whole basis of the match. Study 21 tests the gauge on months to come.
- **Description, not cause.** Why reserves must keep pace with the debt is a reading (Treasury settlement, financing
  and the Treasury's cash flows all scale with it), not something this study measures.
