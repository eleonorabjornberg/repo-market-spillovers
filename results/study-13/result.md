# Study 13: pre-publication checks — result

Design: [`docs/design-study-13-prepublication.md`](../../docs/design-study-13-prepublication.md), committed before the
checks were run. C6 was added after reading the New York Fed's account of sponsored repo's growth, and is marked post
hoc. Every figure is read from [`result.json`](result.json). Checked on 26 October 2026, ahead of a newspaper article.

## Summary

| Claim | Check | Outcome |
|---|---|---|
| The hedge-fund side of clearing has slipped (35% → 31%) | C1, year on year | **Withdrawn.** The dip is seasonal; year on year the share is still rising |
| The basis trade peaked in October 2024 and is down about 30% | C2, duration-weighted | **Survives, much smaller.** By risk, it peaked in November 2025 and is down 17% |
| The hedge has moved from futures to swaps | C3 and C5 | **Supported, but not new.** The Fed has published it |
| Repo stayed calm through October | C4, SOFR's 99th percentile | **Survives** |
| The move to clearing is timed to the SEC's rule | C6, post hoc | **Corrected.** It began with the 2022 proposal, not the December 2023 adoption |

## C1: the hedge-fund clearing share is seasonal, and still rising

FICC sponsored repo over hedge funds' Form PF repo borrowing jumps in every fourth quarter: 28.9% (Q4 2024) and
35.2% (Q4 2025). December's sponsored repo volume ran 34%, 12% and 7% above October–November in 2023, 2024 and 2025.

Against the same quarter a year earlier, the share has risen in every quarter since 2024: +5.8 points in Q2 2026
(25.5% → 31.3%) and +8.2 in Q1 2026. **"The hedge-fund side has slipped" is withdrawn.**

The fair reading: about a third of hedge funds' repo goes through FICC's sponsored service, rising by 6–8 points a year,
with eight months to the June 2027 deadline.

## C2: by risk, the basis-trade proxy is down 17%, not 30%

| Measure | Peak | Latest (Sep 2026) | From peak |
|---|---|---|---|
| Face value of leveraged funds' net futures short | Oct 2024, $1,146bn | $801bn | −30.1% |
| Weighted by approximate duration ($bn-years) | Nov 2025, 5,692 | 4,704 | −17.4% |

The positions moved to longer contracts: average duration rose from 4.8 years (Oct 2024) to 5.9 (Sep 2026). That matches
Morgan Stanley's reported finding that the decline sits in 2- and 5-year contracts while the longest grew.

Over study 11's window (Sep 2024 – Jun 2026), the duration-weighted short fell only 4.4%, against 15.8% by face value.
"The basis trade peaked two years ago" overstates it; "by face value" or "since late 2025" is accurate.

## C3: the futures cover fell, and derivatives grew a little faster

- **Futures cover:** the futures short (face value) as a share of hedge funds' long Treasuries was 41.7% (Dec 2022),
  55.2% (Sep 2024) and 38.9% (Jun 2026).
- **Derivative growth:** hedge funds' interest-rate derivative exposure grew 40.7% over the seven quarters before
  September 2024, and 46.5% over the seven after.

The reading is strengthened by the design's rule, but modestly: derivatives were already growing fast before.

## C4: the upper tail of repo stayed within its usual range

SOFR's 99th percentile minus IORB peaked at 10 bp in October 2026 (23 October, not a month-end), and averaged 6.6 bp.
That is ordinary for 2026: January averaged 10.0 bp, with a high of 22. The claim survives, on data to 23 October.

## C5: is the angle fresh? Partly

**Already published:**
- The Federal Reserve's FEDS Note "[Decomposing Hedge Funds' U.S. Treasury Exposures](https://www.federalreserve.gov/econres/notes/feds-notes/decomposing-hedge-funds-u-s-treasury-exposures-20260622.html)"
  (Phillip J. Monin, 22 June 2026, Form PF):
  - the basis trade at about $830bn, and swap-spread arbitrage at about $305bn (September 2025);
  - swap-spread positions growing about $175bn between January 2024 and March 2025;
  - about $60bn of swap-spread positions unwinding in April 2025.
- **Press, not opened here:** Bloomberg (22 Sep 2026) and others report hedge funds cutting basis positions; Morgan
  Stanley's estimate is quoted there.
- **Dallas Fed (16 Oct 2026):** reported to argue that swap-spread trades are an alternative to the basis trade. The
  page could not be reached from here, so verify it before citing.

**Not found published:**
- a measurement of how the clearing rule's proposal, adoption and extension changed the pace of the move to central
  clearing;
- a systematic test, across calendar and non-calendar days, of whether repo stress spreads into wider markets;
- a scored test of warning indicators, including tight credit spreads, across 22 episodes.

The New York Fed (Copeland and Kahn,
"[The Rise of Sponsored Service for Clearing Repo](https://libertystreeteconomics.newyorkfed.org/2025/10/the-rise-of-sponsored-service-for-clearing-repo)",
8 Oct 2025) dates the surge in sponsored membership to August 2022 but does not test the rule's timing.

## C6 (post hoc): the move to clearing began with the rule's proposal

Study 07 fixed its first break at the rule's adoption (December 2023) and passed its test. But a first break in mid- to
late 2022 fits all three series better:

| Series | Best first break | Fit at best (SSE) | Fit at Dec 2023 (SSE) | Slope change at the Feb 2025 extension |
|---|---|---:|---:|---|
| FICC share of money-fund repo | Sep 2022 | 371.5 | 1,364.6 | −9.7 pp/yr |
| FICC share of money-fund private repo | Jun 2022 | 551.4 | 945.5 | −6.3 pp/yr |
| Sponsored reverse repo, % of DVP | Jun 2022 | 258.4 | 832.1 | −7.2 pp/yr |

FICC's share of money-fund repo was 2–4% through 2022, when most of their cash sat at the Fed's reverse repo facility,
and rose from there: 10.4% (Jun 2023), 16.2% (Nov 2023), 35.9% (Jan 2025). Study 07's "flat at about 16% from 2019 to
November 2023" compared two endpoints and hid the dip and the rise between.

- **The corrected reading:** the move to clearing tracks the rulemaking from its proposal (14 September 2022), not
  only its adoption.
- **What holds:** the slowdown after the February 2025 extension holds under every start date, at −6 to −10 points a
  year.
- **What is not ruled out:** the slowdown may also reflect saturation, as the easy migration was done.

## What changes in the article

- **Remove** the claim that the hedge-fund side has slipped. Replace it with: about a third, rising 6–8 points a year.
- **Qualify** "the basis trade peaked two years ago": by face value; by risk, it peaked in late 2025 and is down 17%.
- **Do not present the swap shift as new.** Credit the Fed's June 2026 note and treat our data as extending it to
  mid-2026.
- **Re-date the clearing story** to the 2022 proposal; keep the extension slowdown, with saturation as the alternative.

## Note added 26 October 2026: the Dallas Fed piece, now read

Eleonora supplied the page. McCormick, Ramaswamy and De Vere, ["Contract design, higher yields make basis trade
alternatives attractive"](https://www.dallasfed.org/research/economics/2026/1016) (Dallas Fed, 16 October 2026):

- **The basis trade plateaued mainly for mechanical reasons.** As long-end yields near the 6% reference yield used
  for futures conversion factors, the delivery option in the basis shrinks.
- **Front-end swap-spread wideners now offer leveraged funds risk-adjusted carry "close to" a long basis position.**
  A swap-spread position carries more dollar risk per unit of notional, so "even modest reallocation" cuts futures,
  cash Treasury and repo positions by more.
- **The two-year contract accounts for a large share of the dollar decline,** while much of the duration-weighted
  decline is in longer contracts. That fits C2: −30% by face value, −17% weighted by duration.
- **Asset managers may be receiving fixed on swaps tied to AI and data-centre financing.** The authors call this
  "limited to a plausible mechanism and market commentary".

This confirms that the swap shift is published, now by two Fed sources, so the instruction above to credit it stands.
The article cites the piece for the swap alternative and, as a hypothesis, for the AI channel.
