# repo-market-spillovers

An exploratory side project: **do US repo-market pressure days leave a mark on wider markets, and has that grown as
reserves fell?**

It reads the published daily panel of [repo-market-model](https://github.com/eleonorabjornberg/repo-market-model)
(pinned commit and digest in [`metadata/parent_pin.json`](metadata/parent_pin.json)) and adds wider-market series
from FRED. It never writes to, scores for, or changes anything in repo-market-model. Nothing found here enters that
project except through its own directive and scoring process.

**Start here: [`SYNTHESIS.md`](SYNTHESIS.md), "Is the repo market signalling a crisis?"**, the findings written for publication (also on the site as [findings](https://eleonorabjornberg.github.io/repo-market-spillovers/findings.html)).

The research plan, hypotheses H1–H5 and the studies that test them, is [`PLAN.md`](PLAN.md).

The **[Repo Market Watch](https://eleonorabjornberg.github.io/repo-market-spillovers/)** is rebuilt on the 3rd of each month by [`.github/workflows/watch.yml`](.github/workflows/watch.yml) (`python3 scripts/watch.py` builds it locally).

## Results

| Study | Question | Finding |
|---|---|---|
| [Event study 01](results/event-study-01/result.md) | Do calendar repo-pressure days move yields, VIX, credit, equities, the dollar and CP more when reserves are scarce? | No, at daily closes in public data. Weak signs only in bills and overnight CP. |
| [Study 02: then and now](results/study-02/result.md) | Does today's repo and bond market look like the run-up to 2000 or 2007, and would those signs have warned? | Not on the measures that flashed then. New this time: record hedge-fund repo, record public debt, very tight credit spreads, with no history to score them against. |
| [Study 03: map of the chain](results/study-03/result.md) | H1: does a record, concentrated repo chain sit under the Treasury market? | Not supported as specified. Hedge-fund repo is at a record relative to the market and money funds' cash runs increasingly through FICC, but the basis-trade proxy is below 2019 and shrinking, and lending is spread across more counterparty types. |
| [Study 04: amplification](results/study-04/result.md) | H2: do Treasury-market shocks spread into repo? | Nominally "supported for 2025–26 only" (+1.1 bp next day), but weak: a placebo is 84% as large, no replication, no dose–response. April 2025 moved repo 7 bp. |
| [Study 05: spillback beyond the calendar](results/study-05/result.md) | H3: do non-calendar repo shocks move wider markets, and do swap spreads follow repo? | Not supported. Broad stress eased slightly after 2025–26 repo shocks; swap-spread pass-through about zero. Only hint: Baa +1.3 bp. |
| [Study 06: would the chain have warned?](results/study-06/result.md) | H4: do repo-chain indicators warn of stress better than the standard signs? | Cannot tell. Best chain indicator (basis-trade proxy) AUROC 0.63 against the yield curve's 0.58; difference +0.05 [−0.14, +0.24]. Nothing warned reliably. |
| [Study 07: clearing migration and the watch](results/study-07/result.md) | H5: is the growth of cleared repo a move ahead of the SEC mandate? Plus the monthly public watch. | Supported: FICC's share of money-fund repo was flat for four years, then rose 21 points a year after the rule's adoption (Dec 2023) and slowed after the extension (Feb 2025). The watch: 1 of 8 flags on (complacency). |
| [Study 09: Treasuries in a panic](results/study-09/result.md) | Does more federal debt make Treasuries a worse safe haven, and does that hit repo? With household debt. | Not supported: the weaker haven since 2020 tracks inflation, not debt; repo moves less after panic sell-offs; household debt is down from 98% to 66% of GDP. |
| [Study 10: three prospective tests](docs/design-study-10-prospective.md) | Set before their data exists: the clearing deadlines (31 Dec 2026, 30 Jun 2027), the credit lead on new repo shocks, and whether the repo chain holds in the next stress event. | Pending; scored automatically each month ([status](results/study-10/status.json)). April 2025, as a reference, scores "held". |
| [Study 11: what hedge-fund repo funds](results/study-11/result.md) | Descriptive: now that the basis trade has shrunk, what is hedge-fund repo funding? | Still Treasuries (repo +21%, long Treasuries +20%), hedged less with futures (−16%) and more with rate derivatives (+47%); growth with multi-strategy and relative-value funds, not macro. |
| [Study 12: better indicators?](results/study-12/result.md) | Can better warning indicators be found without overfitting? 9 candidates fixed in advance, 22 events since 1990, development/test split. | No reliable one. Composite = yield curve (−0.02). Two "promising": largest hedge funds' leverage (0.74, but only from 2013) and low long-run VIX (0.78 at 12m, but below chance before 2013). Both now tracked in the watch. |

## Reproduce

Python 3.11, stdlib only. Needs a checkout of repo-market-model next to this one, and network access to FRED.

```
scripts/build_panel.sh            # builds the parent panel at the pin and checks its digest
python3 scripts/fetch_fred.py     # writes data/raw/ and metadata/fred_manifest.json
python3 scripts/event_study_01.py # writes results/event-study-01/result.json and chart.svg
python3 scripts/fetch_long.py     # study 02: long histories into data/raw/long/, manifest in metadata/
python3 scripts/study_02_then_and_now.py
python3 scripts/fetch_chain.py      # study 03: OFR, CFTC, Treasury, FRED into data/raw/chain/
python3 scripts/study_03_chain.py
python3 scripts/study_04_amplification.py
python3 scripts/fetch_dtcc.py && python3 scripts/study_05_spillback.py
python3 scripts/study_06_warning.py
python3 scripts/study_07_clearing.py
python3 scripts/study_10_prospective.py   # after scripts/watch.py
python3 scripts/fetch_study11.py && python3 scripts/fetch_dtcc_packages.py && python3 scripts/study_11_what_repo_funds.py
python3 scripts/fetch_study12.py && python3 scripts/study_12_indicators.py   # ebp.csv supplied by hand
python3 scripts/fetch_study09.py && python3 scripts/study_09_debt_volatility.py
python3 -m unittest discover -s tests
```

FRED serves only its latest vintage, so a later fetch can move figures slightly. `event_study_01.py` refuses to run if
`data/raw/` does not match the manifest. `data/` is not committed.

## Layout

- `docs/`: each study's design, written before its first run
- `src/spillovers/`: panel, calendar and regime logic (`events.py`), outcome changes (`outcomes.py`), statistics
  (`stats.py`)
- `scripts/`: build, fetch, and one script per study
- `results/<study>/`: `result.json` (every figure), `result.md` (written from it), and charts
