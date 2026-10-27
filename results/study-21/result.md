# Study 21: the reserves-to-debt gauge

Design: [`docs/design-study-21-reserves-to-debt-gauge.md`](../../docs/design-study-21-reserves-to-debt-gauge.md), committed with the scoring code on 27 October 2026. This page is rewritten by the weekly watch. Status as of 2026-10-27.

## In one line

Reserves were **9.3%** of federal debt held by the public in the week of 2026-10-21: the **scarce** zone (below 10% scarce, 11% or more ample). Verdict so far: **pending** (0 zone months scored from November 2026).

## What is being tested

Study 20 found that repo got tight when reserves fell to about a tenth of the debt, in 2018–19 and in 2025–26. This tests it on months that had not happened when the design was written. In a scarce month, ordinary-day repo should trade above −15 bp against the top of the Fed's range and month-ends should jump more than 3 bp. In an ample month, neither. The gauge holds if at least 75% of zone months match.

No month has been scored yet: November 2026 is scored once December's first business day has data.
