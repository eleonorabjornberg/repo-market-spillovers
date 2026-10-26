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
