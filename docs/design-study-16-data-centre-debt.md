# Study 16: data-centre debt, and whether it reaches the swap market

Written on 26 October 2026, before any of this study's data was fetched. Requested by Eleonora after the Dallas Fed
piece of 16 October 2026 (McCormick, Ramaswamy and De Vere). They suggest that issuers of long-dated AI and
data-centre debt pay fixed in swaps, and that asset managers take the other side, getting the interest-rate exposure
they once got from Treasury futures. The authors call the evidence "limited to a plausible mechanism and market
commentary". This study measures what public data can show.

**Disclosed beforehand.**
- **Seen:** the six companies' names, identifiers and fiscal year-ends from the SEC's submissions service, and that
  DTCC's daily swap files are available from November 2024 (study 05). No values.
- **General knowledge, not checked:** the large cloud companies borrowed heavily in 2025–26 to fund data centres,
  including some very large bond deals. Some of the largest financings were done off balance sheet, through joint
  ventures and private placements, which this study cannot see.

## Questions

1. **How much have the companies building AI data centres borrowed,** against how much they spend on them?
2. **Do long-dated dollar swap volumes rise around their bond deals?** If issuers swap their new fixed-rate bonds, or
   dealers hedge them, long-dated swap trading should be heavier on and just after pricing days than on other days.
3. **How long-dated is the debt?** Long-dated fixed-rate debt is what falls most when long yields rise, which is the
   case study 15 found corporate bonds have no offset against.

## Companies

Alphabet, Amazon, Meta, Microsoft, Oracle and CoreWeave: the four largest cloud spenders, plus the two most indebted
data-centre builders among listed companies.

## Data

- **SEC XBRL company facts** (`data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`), from annual reports (10-K):
  - **Debt:** `LongTermDebt`. Where it is absent, `LongTermDebtNoncurrent` plus `LongTermDebtCurrent`. Where both
    are absent, `DebtInstrumentCarryingAmount`. Finance-lease liabilities are reported beside it, not added.
  - **Capital spending:** `PaymentsToAcquirePropertyPlantAndEquipment`. Where it is absent,
    `PaymentsToAcquireProductiveAssets`.
  - **Maturities:** `LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive` over the sum of the year-one to
    year-five and after-year-five buckets.
  - Fiscal years 2019 to the latest. Values are taken from each fiscal year's own 10-K (`form` = 10-K, `fp` = FY);
    where restated, the latest filing wins.
- **SEC submissions** (`data.sec.gov/submissions/CIK{cik}.json`): the dates of each company's free-writing
  prospectuses (`FWP`) and prospectus supplements (`424B2`), which mark registered bond deals.
- **DTCC's public swap reports** (the daily cumulative rates files used in studies 05 and 07), from 1 November 2024:
  new, spot-starting USD SOFR OIS trades that are not part of a package, executed on the file's date. Two series per
  day: tenor 19.5 years or more (20- and 30-year swaps), and, as a placebo, 9.5–10.5 years. For each, the summed
  notional (DTCC caps large notionals, so this is a lower bound) and the number of trades.

The contact the SEC asks automated requests to carry is read from the environment variable `SEC_USER_AGENT` at run
time. It is not stored in the repository.

## Measures and what would count

**Q1, size.** For each company and for the six together: debt and capital spending in fiscal 2019 and in the latest
fiscal year, and debt's growth against capital spending's. Reported, no verdict.

**Q2, the swap test.**
- **Deal days.** A deal's pricing day is the date of an `FWP`. A `424B2` with no `FWP` from the same company in the
  three business days before it is dated one business day before its filing. Deal days of any of the six companies
  within five business days of each other are merged into one deal, dated at the first.
- **Event days.** Each deal's pricing day and the business day after.
- **Model.** Over every business day with DTCC data from 1 November 2024: the log of long-dated notional regressed on
  an event-day indicator, with a dummy for each calendar month and each weekday. The coefficient is the average
  log difference on event days.
- **Interval.** A 95% interval from a block bootstrap that resamples calendar months (2,000 draws, seed 20261027).
- **Verdict.** Long-dated swap volume is **heavier around deals** if the interval's lower bound is above zero. As a
  placebo, the same model on 10-year volume is reported. If 10-year volume rises as much as long-dated volume, the
  jump is busy-market days rather than the deals, and the result is reported as **not specific to long tenors**.
  The test for that: the long-dated coefficient minus the 10-year coefficient, with its own bootstrap interval, must
  have a lower bound above zero.
- The same model on trade counts is reported, without a verdict.

**Q3, maturity.** For each company, the share of debt principal due after five years in the latest 10-K. Reported,
no verdict.

## Limits

- **Direction is invisible.** Public swap reports do not show who paid fixed. A volume jump around deals fits the
  Dallas Fed's mechanism, but also fits dealers hedging new-issue inventory or anyone trading around a busy day. The
  test can count against the mechanism, by finding no jump; it cannot prove it.
- **Off-balance-sheet and private deals are missing.** Joint ventures, project financings and 144A private placements
  file no FWP or 424B2 with these companies, and some of the largest data-centre financings took that form.
- **Floating-rate private credit,** the other half of the Dallas Fed's mechanism, is not in public data.
- **DTCC's window** starts in November 2024, so the test covers about two years of deals.
- **Nothing here forecasts a crisis,** or says AI spending is a bubble.

## Amendment (26 October 2026, after the first results were seen)

**Written after seeing the first run's figures.** The swap test (Q2) does not depend on it, and its result is
unchanged. Q1 and Q3 have no verdicts, but two of their figures were wrong:
- **Oracle's debt read as zero.** Its `LongTermDebt` tag has a single value, for 2022.
- **Amazon's capital spending was missing.** Its `PaymentsToAcquirePropertyPlantAndEquipment` tag ends in 2016,
  after which it reports `PaymentsToAcquireProductiveAssets`.

The rule "the first option that is present" picked a tag the company had stopped using. Change: an option is used
only if it has a value for the company's latest fiscal year, the latest year any of that measure's options reports.
Otherwise the next option is tried. The order of options is unchanged. The six companies together are summed only
over years in which every company with any debt or spending reports a value.
