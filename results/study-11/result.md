# Study 11: what is hedge-fund repo funding now that the basis trade has shrunk? — result

**Descriptive.** Design: [`docs/design-study-11-what-repo-funds.md`](../../docs/design-study-11-what-repo-funds.md),
committed before the data was fetched. Every figure is read from [`result.json`](result.json).

**Sources:**
- Form PF via the OFR Hedge Fund Monitor (quarterly; latest quarter June 2026);
- the CFTC's leveraged-fund futures positions;
- DTCC's public swap reports (Nov 2024 – Sep 2026; monthly counts in
  [`dtcc_packages_monthly.csv`](dtcc_packages_monthly.csv));
- TIC Table 5.

**Window:** September 2024, just before the basis-trade proxy peaked, to June 2026.

## The answer, as far as public data goes

**The repo still funds Treasuries, and the Treasuries are now hedged less with futures and more with rate
derivatives.** The growth sits mainly with multi-strategy funds, not macro funds.

| Form PF, Sep 2024 → Jun 2026 | Sep 2024 | Jun 2026 | Change |
|---|---:|---:|---:|
| Hedge funds' repo borrowing | $2.80tn | $3.38tn | +20.7% |
| Long Treasury exposure | $1.98tn | $2.36tn | +19.5% |
| Short Treasury exposure | $1.55tn | $1.50tn | −3.2% |
| Interest-rate derivatives, gross notional | $9.49tn | $13.90tn | **+46.5%** |
| CFTC: leveraged funds' net futures short | $1.09tn | $0.92tn | **−15.8%** |

## The four explanations

| | Explanation | Reading | Points to it? |
|---|---|---|---|
| E1 | Swap-spread trades | Rate-derivative exposure +46.5% while the futures short fell (E1b: **yes**). But the share of new SOFR swap notional traded as packages went from 75.2% (Nov 2024 – Jan 2025) to 70.7% (Jul – Sep 2026), −4.4 pp (E1a: **no**). | **Partly**: E1 needed both |
| E2 | Directional bets by macro funds | Macro funds account for 0.7% of the $2.14tn growth in hedge-fund borrowing | **No** |
| E3 | The arbitrage continues (relative value) | Relative-value funds account for 12.7%, more than macro | **Yes**, by the rule |
| E4 | Repo against non-Treasury collateral | Repo grew 1.1 pp faster than long Treasuries, within the 5 pp threshold | **No** |

**Where the borrowing growth went,** by fund type:

| Strategy | Sep 2024 | Jun 2026 | Share of the growth |
|---|---:|---:|---:|
| Equity | $1.19tn | $2.09tn | 42.2% |
| Multi-strategy | $2.32tn | $3.11tn | 36.9% |
| Relative value | $0.92tn | $1.19tn | 12.7% |
| Other | $0.39tn | $0.49tn | 4.6% |
| Credit | $0.14tn | $0.18tn | 1.8% |
| Event-driven | $0.04tn | $0.07tn | 1.0% |
| Macro | $0.81tn | $0.83tn | 0.7% |

Form PF's borrowing by strategy covers all borrowing, not repo alone. Equity funds borrow mostly through prime
brokers, so their growth is unlikely to be repo. Multi-strategy funds run relative-value "pods", including Treasury
trades.

**TIC (decides nothing):** the Cayman Islands' Treasury holdings, the usual proxy for hedge funds, rose from $411bn to
$463bn (+12.8%) between August 2025 and August 2026. Over the same months leveraged funds' futures short fell 24.2%.
Treasury's current table covers only those 13 months.

## Reading it together

- **The repo still funds Treasuries.** Repo and long Treasury holdings grew in step (E4: no), so the gap is not repo
  quietly funding something else.
- **The hedge changed.** Long Treasuries rose about $390bn while the futures short fell about $170bn and
  rate-derivative exposure rose about $4.4tn gross. The simplest fit is long Treasuries hedged with swaps instead of
  futures: the swap-spread trade, or a mix of hedges. DTCC's package flag does not confirm it. It is a blunt proxy: 70–77%
  of SOFR swap notional is packaged in every month, mostly for reasons other than swap spreads, so a shift in one use
  may not show.
- **Still arbitrage, mostly in multi-strategy platforms.** Macro funds' borrowing barely grew (+$16bn). The growth sits
  with multi-strategy and relative-value funds, whose Treasury positions are typically hedged relative-value trades,
  not outright bets on rates.

**What it means for risk:** a hedged Treasury position financed in repo is still leveraged, and still has to be
unwound if funding or margins tighten. A swap hedge brings a different risk from a futures hedge: the swap-spread
widening of April 2025 (−61 bp, study 05) was exactly the move that hurts it. So the exposure Eleonora pointed to is
real. It is just carried in swaps more than futures now, which public data sees less clearly.

## Limits

- **Aggregates:** what kind of trade, not who.
- **Form PF** is quarterly and about two quarters behind.
- **Proxies:** DTCC packages are a weak proxy for swap-spread trades, and borrowing by strategy is not repo alone.
- **TIC** covers 13 months.
- **Not public yet:** the OFR's uncleared bilateral repo collection.
