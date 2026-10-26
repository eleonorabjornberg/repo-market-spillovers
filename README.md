# repo-market-spillovers

An exploratory side project: **do US repo-market pressure days leave a mark on wider markets, and has that grown as
reserves fell?**

It reads the published daily panel of [repo-market-model](https://github.com/eleonorabjornberg/repo-market-model)
(pinned commit and digest in [`metadata/parent_pin.json`](metadata/parent_pin.json)) and adds wider-market series
from FRED. It never writes to, scores for, or changes anything in repo-market-model. Nothing found here enters that
project except through its own directive and scoring process.

The research plan, hypotheses H1–H5 and the studies that test them, is [`PLAN.md`](PLAN.md).

## Results

| Study | Question | Finding |
|---|---|---|
| [Event study 01](results/event-study-01/result.md) | Do calendar repo-pressure days move yields, VIX, credit, equities, the dollar and CP more when reserves are scarce? | No, at daily closes in public data. Weak signs only in bills and overnight CP. |
| [Study 02: then and now](results/study-02/result.md) | Does today's repo and bond market look like the run-up to 2000 or 2007, and would those signs have warned? | Not on the measures that flashed then. New this time: record hedge-fund repo, record public debt, very tight credit spreads, with no history to score them against. |
| [Study 03: map of the chain](results/study-03/result.md) | H1: does a record, concentrated repo chain sit under the Treasury market? | Not supported as specified. Hedge-fund repo is at a record relative to the market and money funds' cash runs increasingly through FICC, but the basis-trade proxy is below 2019 and shrinking, and lending is spread across more counterparty types. |
| [Study 04: amplification](results/study-04/result.md) | H2: do Treasury-market shocks spread into repo? | Nominally "supported for 2025–26 only" (+1.1 bp next day), but weak: a placebo is 84% as large, no replication, no dose–response. April 2025 moved repo 7 bp. |
| [Study 06: would the chain have warned?](results/study-06/result.md) | H4: do repo-chain indicators warn of stress better than the standard signs? | Cannot tell. Best chain indicator (basis-trade proxy) AUROC 0.63 against the yield curve's 0.58; difference +0.05 [−0.14, +0.24]. Nothing warned reliably. |
| [Study 09: Treasuries in a panic](results/study-09/result.md) | Does more federal debt make Treasuries a worse safe haven, and does that hit repo? With household debt. | Not supported: the weaker haven since 2020 tracks inflation, not debt; repo moves less after panic sell-offs; household debt is down from 98% to 66% of GDP. |

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
python3 scripts/study_06_warning.py
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
