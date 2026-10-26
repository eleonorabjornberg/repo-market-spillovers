# Study 15: corporate bonds in repo, and in a stock-market panic

Written on 26 October 2026, before this study's series were fetched or any of its measures computed. Descriptive.
It follows Eleonora's question: if a crisis came from outside repo, say an AI-stock bust, would the repo market cushion
it, and where do corporate bonds fit? Study 09 found that Treasuries now fail as a haven on a third of panic days.
This study asks what corporate bonds do on those days, and how much repo rests on corporate collateral.

**Disclosed beforehand.** While scoping, these were seen:
- **The OFR's metadata for the dealer series below:** names, units and their start date (7 January 2015). No values.
- **From earlier studies:** Baa − 10y at 148 bp in September 2026 (studies 02 and 12); study 09's panic-day rule and
  its era table (yields rose on 59%, 22%, 14% and 33% of panic days by era).
- **General knowledge,** not checked against data: corporate collateral is a small part of repo, and in 2008 the run
  on repo hit private collateral hardest (Gorton and Metrick, 2012; Copeland, Martin and Walker, 2014). This study
  cannot test 2008: its repo data start in 2015.

## Questions

1. **How much repo rests on corporate bonds?** Primary dealers' repo against corporate debt, as a share of their total
   repo, and how it has grown against their Treasury repo.
2. **In March 2020, did cash lenders pull back from corporate collateral** more than from Treasuries? April 2025 is
   reported the same way, as a second case.
3. **On stock-market panic days, do corporate bonds lose value when Treasuries fail as a haven?** If they do, holders
   of corporate bonds have no offset in exactly the case study 09 found more common since 2020.

## Data

- **Dealer financing,** the OFR's weekly mirror of the New York Fed's primary dealer statistics, from 7 January 2015,
  in dollars:
  - `NYPD-PD_RP_CORD_TOT-A`, `NYPD-PD_RRP_CORD_TOT-A`: repo (dealers borrow cash) and reverse repo (dealers lend cash)
    against corporate debt;
  - `NYPD-PD_RP_T_TOT-A`, `NYPD-PD_RRP_T_TOT-A`: the same against Treasuries;
  - `NYPD-PD_RP_TOT-A`, `NYPD-PD_RRP_TOT-A`: all collateral.
- **Daily, from FRED:** `DBAA` (Moody's Baa corporate bond yield), `DGS10`, `VIXCLS`.

Fetched into `data/raw/s15/` with checksums in `metadata/s15_manifest.json`. A missing value drops that week or day from
the measure that needs it.

## Measures and what would count

**Q1, size.** C1 = corporate-debt repo over all repo, for each leg, as 13-week averages over the first and the last 13
weeks. The dollar levels are reported beside them.
- Corporate collateral is **small** if C1 for repo in the last 13 weeks is below 10%.
- It **grew faster than Treasury repo** if its percentage growth from the first to the last 13 weeks exceeds that of
  Treasury repo.

**Q2, March 2020.** For each leg and collateral, the percentage change from window A (the four weekly observations up
to and including 26 February 2020) to window B (the four from 18 March 2020).
- Lenders **pulled back from corporate collateral** if dealers' corporate repo fell and fell by at least 10 percentage
  points more than their Treasury repo.
- April 2025: window A is the four observations up to and including 2 April 2025, window B the four from 9 April
  2025. Reported, no verdict.

**Q3, panic days.** Panic days use study 09's rule: VIX closes at least 15% above its previous close, from 1990, with
DGS10 and DBAA observed on both days. On each, ΔBaa = the change in the Baa yield and ΔT = the change in the 10-year
yield, in bp. A haven failure is ΔT > 0, as in study 09.
- **Main:** the share of haven-failure panic days on which the Baa yield also rose, with a 95% interval from a block
  bootstrap by year (2,000 draws, seed 20261026). Corporate bonds give **no offset** when Treasuries fail if the lower
  bound is above 50%.
- **Reported:** the share of all panic days on which the Baa yield rose, by study 09's eras; and the mean ΔBaa and
  mean ΔT on haven-failure days and on haven days.

## Limits

- **Dealers only,** and dealers' repo is partly their own choice: a fall can be dealers shrinking inventories, not
  lenders pulling back. The data cannot tell the two apart.
- **One stress episode** (March 2020) in the repo data, and one second case. Neither is a pattern.
- **Moody's Baa is an index of long, seasoned bonds.** Its yield moves slowly, which makes its spread over Treasuries
  widen mechanically when Treasury yields fall. Q3 uses its level for that reason, not its spread.
- **Nothing here forecasts a crisis or says an AI bust is coming.** It says what corporate bonds and repo did in past
  panics.

## Amendment (26 October 2026, after the first fetch, before any measure was computed)

The first run stopped before computing any measure. Seen in doing so: each OFR series' coverage, and its first and last
values. Two problems:
- **The OFR's mirror ends on 29 December 2021,** when the New York Fed changed the report's format.
- **Its all-collateral totals are mostly missing:** they are blank whenever any component is.

Changes:
- **Two segments.** 2015–2021 from the OFR series above. From 5 January 2022, from the New York Fed's API in the new
  format, as in study 14: for each leg, each collateral is summed over the eight venues and three terms. Corporate debt
  is `CD`, and Treasuries are `UTSET` plus `UTST` (TIPS), matching the OFR's Treasury total, which includes TIPS. The
  two formats are not spliced: growth is measured within each segment.
- **Denominator.** C1 is corporate over corporate plus Treasury, in both segments. It leaves out agency, mortgage,
  equity and other collateral, so it overstates corporate's share of all repo. That makes "small" a conservative call.
- **Q1's tests** use the 2022 segment: "small" on its last 13 weeks, and "grew faster" from its first 13 weeks to its
  last 13. The 2015–2021 segment is reported the same way, without a verdict.
- **Suppressed values** ("*") in the new format count as zero, so totals are lower bounds. The number of weeks with
  any suppressed corporate cell is reported.
- Q2 and Q3 are unchanged. March 2020 falls in the first segment and April 2025 in the second.

## Second amendment (26 October 2026, after the first results were seen)

**This amendment was written after seeing results,** and says so. The first complete run summed the new-format venue
series. Its 2022 segment showed dealers' corporate repo rising from $19.5bn to $168.4bn. That is an artefact: in the
new format, the tri-party venue series (`TRIG`, `TRISP`), where most corporate collateral sits, begin only on 3 July
2024. Before then the venue sum leaves tri-party out. It also showed a break at the turn of 2022 ($82.7bn in the last
weeks of 2021, $19.5bn in the first weeks of 2022).

The New York Fed also publishes continuous totals by collateral, weekly from 3 April 2013:
- `PDSORA-CDTOT` and `PDSIRRA-CDTOT` for corporate debt;
- `PDSORA-UTSETTOT`, `PDSORA-UTSTTOT`, `PDSIRRA-UTSETTOT` and `PDSIRRA-UTSTTOT` for Treasuries.

Two of their published descriptions are wrong. `PDSORA-CDTOT` says "Triparty", yet it matches the venue sum across
all venues in 2026. `PDSIRRA-CDTOT` is described as mortgage securities borrowed, yet its values are of the size of
corporate reverse repo. So before use, each corporate total is checked against the OFR's corporate series for
2015–2021. The total is used only if the two agree within 1% in at least 95% of overlapping weeks.

Changes:
- **Q1** uses these totals, as one series from 2013: C1 on the first and last 13 weeks with all four components of a
  leg reported. A "*" is missing, and drops that week for that leg. The tests are unchanged ("small" below 10%;
  "grew faster" than Treasury repo). The two-segment construction is dropped.
- **Q2** keeps the OFR series for March 2020 as specified. The same windows from the totals are reported beside it, and
  April 2025 now comes from the totals.
- **Q3** is unchanged; its result was seen before this amendment and does not depend on it.

## Extension to 2008 (26 October 2026, Eleonora's request, before the 2001–2013 values were fetched)

Q1–Q3 cannot reach 2008: their repo data start in 2013. The New York Fed's API also serves the dealer statistics'
2001–2013 format (series break `SBP2013`, 1 July 2001 to 31 March 2013). Seen beforehand: the series names, and that
each has 613 weekly observations. No values.

**Q4. In 2007–08, did dealers' financing against private collateral shrink while their Treasury financing held?**

**Data.** Weekly, in $ millions, from `https://markets.newyorkfed.org/api/pd/get/SBP2013/timeseries/{key}.json`:

| | Securities out (dealers borrow cash: repo and securities lent) | Securities in (dealers lend cash: reverse repo and securities borrowed) |
|---|---|---|
| Corporate securities | `PDFSOCT` | `PDFSICT` |
| Mortgage-backed securities | `PDFSOMBT` | `PDFSIMBT` |
| Federal agency | `PDFSOFAT` | `PDFSIFAT` |
| Treasuries | `PDFSOUSTT` | `PDFSIUSTT` |

The names are read as follows: `FSO` and `FSI` are financing securities out and in, `C`, `MB`, `FA` and `UST` are
the collateral, and the suffix `T` is the total of `OC` (overnight and continuing) and `TA` (term agreements). The API
gives no descriptions for this format, so the reading is checked first. If `T` is not within 1% of `OC` + `TA` in at
least 95% of weeks for every series used, the study stops and reports that.

**Windows.**
- **Baseline:** the 13 weeks up to and including 1 August 2007, before BNP Paribas froze its funds on 9 August.
- **W1:** the 13 weeks from 17 March 2008, the week of Bear Stearns.
- **W2:** the 13 weeks from 15 September 2008, Lehman.

Each window's value is its mean.

**What would count.** A **run on private collateral is visible** if dealers' securities out against corporate
securities fell by at least 20% from baseline to W2, and by at least 20 percentage points more than against
Treasuries. The same comparison is reported for mortgage-backed securities, for securities in, and for W1, without
verdicts.

**Limits of the extension.**
- **"Securities out" includes securities lending as well as repo,** and "corporate securities" in this format is not
  defined as today's "corporate debt". It may include private-label mortgage and asset-backed securities. Levels are
  therefore not compared with 2013 onward, only changes within 2007–08.
- **The Fed lent to dealers in 2008 too:** its Primary Dealer Credit Facility opened on 17 March 2008, and its Term
  Securities Lending Facility shortly before. As in March 2020, dealers' totals may include that support.
- **Dealers' financing also falls when dealers shrink,** so a fall is a run by lenders or a retreat by dealers. The
  data cannot tell which.
