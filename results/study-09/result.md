# Study 09: Treasuries in a panic, and household debt — result

Design: [`docs/design-study-09-debt-volatility.md`](../../docs/design-study-09-debt-volatility.md), committed before the
run. It was added at Eleonora's request after study 02 found federal debt held by the public at 97% of GDP, and she
then asked for household debt to be added. Every figure is read from [`result.json`](result.json).
- **Panic day:** VIX closes at least 15% above its previous close. There were 260 since 1990 with the 10-year yield
  observed on both days.
- **Haven failure:** the 10-year yield rises on a panic day.

## First, which debt

The 97% is **federal government debt held by the public** (the Treasury securities investors own), not consumer debt.
The two have moved in opposite directions:

| % of GDP | Mar 2000 | Jun 2007 | Jun 2019 | Jun 2026 | Peak |
|---|---:|---:|---:|---:|---|
| Federal debt held by the public | 36.9 | 34.3 | 75.7 | **97.4** | 103.0 (Apr 2020) |
| Household debt (mortgages, consumer credit) | 68.4 | 96.2 | 72.9 | **65.7** | 98.0 (Jan 2008) |

Households have spent 18 years deleveraging; the government took the borrowing on. In 2007 the leverage that broke
was households' (through mortgages and the repo funding of mortgage securities). Today it is the government's.

## Does more federal debt make Treasuries a worse safe haven? Not detectably

**Main test, not supported.** The model is a linear probability of a haven failure on federal debt/GDP and CPI
inflation (block bootstrap by year).

| | Effect on the chance Treasuries sell off in a panic | 95% interval |
|---|---:|---|
| per point of federal debt/GDP | −0.07 pp | [−0.43, +0.24] |
| per point of CPI inflation | **+5.9 pp** | [+2.5, +9.9] |

**By era:**

| Era | Panic days | Yields rose | Mean Δ10y (bp) | Debt/GDP (mean) |
|---|---:|---:|---:|---:|
| 1990–1999 | 41 | **59%** [44, 73] | +4.7 | 44% |
| 2000–2007 | 32 | 22% [9, 38] | −5.1 | 34% |
| 2008–2019 | 115 | 14% [8, 21] | −6.2 | 66% |
| 2020–2026 | 72 | 33% [22, 44] | −2.3 | 93% |

Treasuries *have* become a less reliable haven since 2020: yields rose on a third of panic days, against one in seven
in 2008–19. But the 1990s, with the least debt, had the least reliable haven of all, and inflation explains the pattern
where debt does not. When inflation is the worry, a panic can push yields up (fear of inflation) as easily as down
(flight to safety).

The interval for debt is not zero, though. At its upper bound, the rise from 34% to 97% of GDP would add up to about 15
points to the chance of a haven failure. The test rules out a large debt effect, not a moderate one, and debt and
inflation both rose after 2020, which the model can only partly separate.

## When Treasuries sell off in a panic, does repo feel it more? No

On the next eligible day (2018–2026), repo moved **−1.3 bp** [−3.1, +0.1] after panics where Treasuries sold off,
relative to panics where they rallied (24 and 56 days). That is the opposite of the stress story, as in study 04, where
repo pressure was larger after rallies. A plausible reading, not tested here: in a flight to safety, cash rushes into
Treasuries and repo, and the demand for financing long positions rises.

## Household debt and mortgages in a panic

The mortgage–Treasury spread (30-year mortgage rate − 10-year yield) widens by **+2.2 bp** [+0.3, +4.0] in weeks with
a panic day (230 of 1,895 weeks since 1990). It does **not** widen more when household debt is higher:
- all weeks: +0.03 bp per point of household debt/GDP [−0.16, +0.18];
- excluding 2007–09: +0.13 [−0.06, +0.27].

That part is not supported. Mortgages reach repo as agency mortgage-backed securities, but their repo rates are not
public daily, so that link is described, not tested.

## What this means for the question

The "97%" is real and it matters, but it did not show up where the crisis story puts it:
- Treasuries' weaker haven role since 2020 tracks inflation, not the debt level;
- when Treasuries sold off in a panic, repo got *less* pressure, not more;
- household leverage, the fuel of 2008, is below where it stood in March 2000 relative to GDP (65.7% against 68.4%).

The debt's risk is better described as slow (a rising term premium, study 02) than as a trigger in a panic. That is a
limit of what daily public data can see, not a guarantee.

## Limits

- **Confounding:** debt/GDP rises almost monotonically, so it is confounded with everything that trended. Inflation is
  the one control.
- **A narrow panic measure:** VIX panics are equity panics. Bond-led stress (2022, the 2023 term-premium rise) is not
  in this test.
- **Few repo days:** the repo comparison has 24 sell-off days.
