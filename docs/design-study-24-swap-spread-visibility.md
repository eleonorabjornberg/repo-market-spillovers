# Study 24: can public data see the swap-spread trade?

Written on 9 November 2026, before this study's data was fetched, at Eleonora's request. Studies 03, 11 and 13 found
that the basis trade has shrunk (by 30% in face value since October 2024, by 17% in risk since November 2025) while
hedge funds' long Treasuries, repo borrowing and rate-derivative exposure kept growing. The simplest reading is that
the hedge moved from Treasury futures to swaps. The Fed has published that shift from confidential Form PF data
(Monin, FEDS Note, 22 June 2026). The futures side is public every week; the swap side is not. This study asks how
much of the swap side public data can see, and builds the best public measure of it that the data allows.

**Disclosed beforehand.**
- **Seen:** one DTCC file (6 November 2026), to learn its fields: of 4,920 new USD SOFR OIS trades, 3,025 carried the
  package flag and 942 a package spread; the prime-brokerage flag was FALSE on all but one; some notionals were
  capped (shown as, for example, "650,000,000+"). The OFR's Form PF series of hedge funds' interest-rate derivative
  gross notional exposure for 2024 Q1 – 2026 Q2 was printed while checking access. The OFR's mnemonic list was read.
- **Known from earlier studies:** study 11's finding that the package share of SOFR swap notional fell (75.2% to
  70.7%), and study 13's figures above.
- **Known from the Fed's note:** swap-spread arbitrage of about $305bn (September 2025); growth of about $175bn
  between January 2024 and March 2025; about $60bn unwound in April 2025.
- **Not reachable from this environment:** the CFTC's weekly swaps report (cftc.gov answers 403). It is left out.

## What public data can and cannot show

DTCC publishes every reportable US swap under the CFTC's real-time reporting rule (17 CFR Part 43), without the
parties' names. Three features of that rule limit what can be seen, and the study measures each:

- **No direction.** A trade does not say who paid fixed. A swap-spread position (long Treasuries, pay fixed) and its
  unwind look the same.
- **Capped notionals.** Trades above a size cap are shown at the cap with a "+". Large trades are understated.
- **Packages are flagged, not described.** A package can be a swap against a Treasury (a swap spread), against a
  Treasury future (an invoice spread), or against other swaps (curve trades and butterflies).

## The measure: single-swap spread packages

A swap-spread trade puts one swap in a package with a security that is not a swap, so DTCC reports one swap leg. A
curve trade or butterfly reports two or three. So:

- **Sample:** new USD SOFR OIS trades (`Action type` NEWT, `Event type` TRAD), effective at most 5 days after
  execution, tenor 1.5 to 31 years, notional currency USD.
- **Package groups:** package trades with a package spread, grouped by execution timestamp (to the second), platform
  and package spread. A group of **one** swap is a **single-swap spread package**: the candidate swap-spread or
  invoice-spread trade. A group of two or more is a swap-curve package.
- **Risk:** each trade's DV01 is notional × the annuity factor at its fixed rate (4% where missing) × 1 bp, in
  $ millions per bp. Capped notionals enter at the cap and are counted separately.

**Known weaknesses.** Legs of one curve package executed at different seconds would be counted as single-swap
packages. Packages reported without a spread are not classified. Neither direction nor counterparty type is known.

## Questions and what would count

All windows run from 1 November 2024 (the first DTCC file) to the last file fetched.

- **Q1, does the measure track hedge funds' swaps?** The quarterly single-swap spread-package DV01, against the
  quarterly change in hedge funds' interest-rate derivative gross notional exposure (OFR `FPF-ASSETCLASS_IRD_GNE_SUM`),
  over the full quarters 2025 Q1 – 2026 Q2. Spearman rank correlation. **It tracks** if the correlation is at least
  0.6. With six quarters this is a weak test, and the result says so.
- **Q2, does it see the April 2025 unwind?** The single-swap spread packages' share of all SOFR swap DV01 in the weeks
  of April 2025, against January – March 2025. A share is used because all swap trading rose in April 2025. **It sees
  the unwind** if April's share is above the 90% bootstrap interval of January – March's weekly shares (2,000 draws,
  seed 20261109).
- **Q3, the migration.** Monthly single-swap spread-package DV01 against the monthly change in leveraged funds' net
  Treasury futures DV01 (OFR `TFF-LF_TREAS_NET_DV01`, from the CFTC). Reported with its correlation and interval
  (moving-block bootstrap, block 3 months); no verdict.
- **Q4, prices.** The weekly change in the 10-year swap spread (the median fixed rate of outright, unpackaged
  spot-starting 9.5 to 10.5 year SOFR OIS trades, minus FRED `DGS10`), against weekly single-swap spread-package DV01.
  Reported with its correlation and interval (block 4 weeks); no verdict.
- **Q5, what is hidden.** The share of SOFR swap DV01 that is capped, the share of package trades without a package
  spread, and the share of single-swap spread-package DV01 that is capped. Descriptive.

**Against the idea that public data can see the trade:** Q1 below 0.6, or Q2 not seeing the April unwind. If both
fail, the finding is that the swap-spread trade cannot be tracked from public data with this method, and the result
says so as its headline.

## Comparisons

Two verdict tests (Q1, Q2) and two reported correlations (Q3, Q4). With four intervals, about 0.4 would exclude zero
by chance at the 90% level.

## Data

| Source | Series | Access |
|---|---|---|
| DTCC public CFTC cumulative rates files | daily, from 1 November 2024 | aggregated per day; trade files not stored; SHA-256 of each zip in `metadata/s24_manifest.json` |
| OFR Hedge Fund Monitor | `FPF-ASSETCLASS_IRD_GNE_SUM`, `FPF-ASSETCLASS_IRD_LGNE_SUM`, `FPF-ASSETCLASS_IRD_SGNE_SUM`, `TFF-LF_TREAS_NET_DV01` | JSON, hashed in the manifest |
| FRED | `DGS10` | CSV, hashed in the manifest |

Every figure on the result page is read from `results/study-24/result.json`.
