# Study 14: what keeps Treasury repo outside central clearing? Haircuts and netted packages

Written on 26 October 2026, before this study's series were fetched together or any of its measures computed.
Descriptive. It follows Eleonora's questions on why hedge funds resist central clearing.

**Disclosed beforehand.** While scoping, these were seen:
- **Two dealer series' endpoints:** reverse repo against specific Treasuries, uncleared bilateral: $344bn (5 Jan
  2022) and $802bn (14 Oct 2026); the same, sponsored: $27bn and $375bn.
- **The OFR's published findings,** which this study cites and does not recompute:
  - [Aug 2025](https://www.financialresearch.gov/the-ofr-blog/2025/08/12/are-zero-haircut-repos-as-common-as-advertised/):
    56% of uncleared bilateral repo at zero haircut, 34% positive, 10% negative; over 60% of Treasury repo; about half
    of zero-haircut repo between affiliates; 65% of hedge-fund repo at zero haircut; data Jan–May 2025.
  - [Aug 2026](https://www.financialresearch.gov/the-ofr-blog/2026/08/20/central-clearing-treasury-repos-plateaued/):
    the clearing plateau; about 68% of hedge funds' reverse repo netted.
  - [Brief 26-01](https://www.financialresearch.gov/briefs/files/OFRBrief-26-01-hedge-fund-participation-cleared-repo.pdf):
    the cost of clearing lies in margin and tenor, not rates.

## Questions

1. **Is the uncleared segment shrinking as clearing grows,** or growing alongside it?
2. **Is there a matched book outside clearing** (repo and reverse repo against the same kind of collateral, at the same
   dealers) large enough to be netted packages? Has it shrunk as clearing grew?
3. **Does the uncleared share dip at year-ends,** when banks' G-SIB surcharge rewards netting through the clearinghouse?

## Data

The New York Fed's primary dealer statistics (FR 2004), weekly from 5 January 2022, Treasury securities excluding TIPS.
Repo is dealers borrowing cash; reverse repo is dealers lending cash. Each is split into the same set of venues, and
each venue is the sum of overnight, under-30-day and 30-day-or-more terms:

| Venue | Series (repo `PDSORA-`, reverse repo `PDSIRRA-`) |
|---|---|
| Uncleared bilateral, general collateral | `UBGUTSET`, `UBGUTSETTAL30`, `UBGUTSETTAG30` |
| Uncleared bilateral, specified collateral | `UBSUTSET`, `UBSUTSETTAL30`, `UBSUTSETTAG30` |
| Cleared bilateral, general | `CBGUTSET`, `CBGUTSETTAL30`, `CBGUTSETTAG30` |
| Cleared bilateral, specified | `CBSUTSET`, `CBSUTSETTAL30`, `CBSUTSETTAG30` |
| Cleared bilateral, sponsored | `CBSPUTSET`, `CBSPUTSETTAL30`, `CBSPUTSETTAG30` |
| Tri-party, general | `TRIGUTSET`, `TRIGUTSETTAL30`, `TRIGUTSETTAG30` |
| Tri-party, sponsored general | `TRISPUTSET`, `TRISPUTSETTAL30`, `TRISPUTSETTAG30` |
| GCF | `GCFUTSET`, `GCFUTSETTAL30`, `GCFUTSETTAG30` |

A value reported as "*" (suppressed for confidentiality) is treated as missing, and a week with any component missing
is dropped from the measure that needs it.

## Measures

- **M1, uncleared share of dealers' bilateral Treasury repo:** uncleared bilateral (general and specified) over all
  bilateral (uncleared plus cleared bilateral, including sponsored). Computed for reverse repo (lending to clients,
  mostly hedge funds) and for repo separately, as 13-week averages.
- **M2, the matched book outside clearing:** for uncleared bilateral specified collateral, min(repo, reverse repo)
  over max(repo, reverse repo), 13-week averages. The same for cleared bilateral (specified plus sponsored), for
  comparison. A high M2 means dealers both borrow and lend against specific Treasuries outside clearing on a similar
  scale, the shape of netted packages. It is a bound, not a count: the data cannot show that the two sides face the
  same counterparty.
- **M3, year-end:** M1 for reverse repo in the last two weeks of December, against the four weeks before and the four
  after, each year 2022–2025.

## What would count

- **Q1:** the uncleared segment is **shrinking** if M1 for reverse repo in the last 13 weeks is at least 10 points
  below the first 13 weeks of 2022. It is **holding** if within 10 points either way. Its level in dollars is reported
  beside it.
- **Q2:** a **large matched book** if uncleared specified M2 averages above 0.7 over the sample. It **shrank** if the
  last 13 weeks are at least 0.1 below the first 13.
- **Q3:** a **year-end dip** if M1 at year-end is below both neighbouring windows in at least three of the four years.

## Limits

- **Dealers only.** The data cover primary dealers, not all repo, and say nothing about haircuts. The haircut evidence
  is the OFR's, cited.
- **Counterparties are not identified.** "Mostly hedge funds" for dealers' reverse repo is the OFR's and the New York
  Fed's characterisation, not something this data shows.
- **M2 bounds netted packages from above.** It cannot confirm them.

## Amendment (26 October 2026, after the first fetch, before any measure was computed)

Sponsored term buckets (under 30 days and 30 days or more) are suppressed for confidentiality in many weeks of 2022–23,
so no week in early 2022 is complete. Changes:

- **"First 13 weeks"** means the first 13 weeks in which the measure is complete.
- **A sensitivity version** treats every suppressed value as zero, over all weeks, and is reported beside the main one.
  It decides nothing.

The rest of the design is unchanged.
