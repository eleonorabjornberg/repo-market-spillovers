# Study 16: data-centre debt, and whether it reaches the swap market — result

Design: [`docs/design-study-16-data-centre-debt.md`](../../docs/design-study-16-data-centre-debt.md), committed before any
data was fetched, with one amendment. The amendment was written after the first figures were seen, and says so. It
fixed how two companies' debt and spending were read, and did not change the swap test. Every figure is read from
[`result.json`](result.json).

## In one line

The companies building AI data centres are borrowing fast: Alphabet, Amazon, Meta, Microsoft, Oracle and CoreWeave
together owed $334bn at the end of their fiscal years ending in 2025, up $95bn in a year, while spending $389bn on
property and equipment. But the Dallas Fed's suggested channel into the swap market does not show up in public trade
volume. Trading in 20- and 30-year dollar swaps was no heavier around these companies' bond deals than on other days.

## 1. How much have they borrowed? (reported, no verdict)

Debt on the balance sheet, and payments for property and equipment, in $bn, from each company's annual reports. A
year is the calendar year in which the fiscal year ends: Microsoft's ends in June, Oracle's in May.

| | Debt 2019 | Debt, latest | Capital spending 2019 | Capital spending, latest | Finance leases, latest |
|---|---:|---:|---:|---:|---:|
| Alphabet | 4.7 | **49.1** (2025) | 23.5 | 91.4 (2025) | 2.5 |
| Amazon | 24.8 | 68.8 (2025) | 16.9 | 131.8 (2025) | 12.3 |
| Meta | 0 (first bonds 2022: 9.9) | **58.7** (2025) | 15.1 | 69.7 (2025) | 1.2 |
| Microsoft | 72.2 | 40.3 (2026) | 13.9 | 115.9 (2026) | **66.6** |
| Oracle | 56.3 | **130.1** (2026) | 1.7 | 55.7 (2026) | 7.7 |
| CoreWeave | – | 21.4 (2025) | – | 10.3 (2025) | 0.3 |

All six together, for the fiscal years ending in 2024 and 2025 (the years in which every company reports): debt
$239bn → **$334bn** (+40%), capital spending $233bn → **$389bn** (+67%).

What stands out:
- **Alphabet quadrupled its debt in a year,** from $12bn to $49bn. **Meta went from no bonds before 2022 to $59bn.**
- **Oracle** carries the most debt, $130bn, up $37bn in its latest year, while its capital spending rose
  more than thirtyfold from 2019.
- **Microsoft's bond debt has fallen** since 2019. Its finance leases, $67bn, are larger than its debt: it rents much
  of its data-centre capacity instead of borrowing to build it.
- **CoreWeave** borrows through private placements and secured loans. It files no registered bond deals, and
  these figures understate its financing commitments.

## 2. Do long-dated swap volumes rise around their bond deals? No detectable rise (verdict: not heavier)

Fifteen registered bond deals by Alphabet (17 filings), Oracle (10), Meta (7) and Amazon (6), from January 2025;
Microsoft and CoreWeave had none. Fourteen fall inside DTCC's data window (1 November 2024 to 23 October 2026, 494
business days), giving 28 event days: each pricing day and the day after. The model controls for the calendar month
and the weekday.

| New USD SOFR swaps | On event days, against other days | 95% interval |
|---|---:|---|
| 20–30 years, notional | **+6.2%** | [−16.2%, +30.2%] |
| 10 years, notional (placebo) | −3.8% | [−18.5%, +9.3%] |
| Difference, long minus 10-year | +10.4% | [−13.2%, +42.3%] |
| 20–30 years, number of trades | +1.3% | [−15.5%, +17.4%] |

Long-dated volume is no heavier around deals: the interval includes zero. It is also not specifically heavier than
10-year volume.

**What this does and does not say.** It counts against a simple version of the Dallas Fed's mechanism, in which
issuers swap their new bonds on pricing day. It does not rule the mechanism out:
- the interval still allows a rise of up to about 30%;
- swaps can be spread over weeks, or done before pricing;
- public data do not show who paid fixed;
- the largest data-centre financings were done through joint ventures and private placements, which have no
  registered deal date.

## 3. How long-dated is the debt? (reported, no verdict)

Share of debt principal due after five years, from the latest annual report:

| Meta | Microsoft | Alphabet | Oracle | Amazon | CoreWeave |
|---:|---:|---:|---:|---:|---:|
| 82.6% | 74.5% | 73.6% | 69.4% | 65.4% | 20.1% |

Most of the big companies' debt is long-dated, so its price is sensitive to long yields. Study 15 found that corporate
bond yields rose with Treasury yields on 89% of panic days when Treasuries failed as a haven. CoreWeave's debt is
mostly short, so its risk is refinancing rather than price.

## Limits

- **Six companies, registered bonds only.** Joint ventures, project financings, private credit and private placements
  are missing, and some of the largest data-centre financings took those forms.
- **Balance-sheet debt is at fiscal year-ends** that differ by company, so "together" mixes year-ends.
- **Swap direction is not public,** and DTCC caps large notionals, so volumes are lower bounds.
- **Fourteen deals in two years** is a small sample: the test can find a large effect, not a small one.
- **Nothing here says AI spending is a bubble or forecasts a crisis.**
