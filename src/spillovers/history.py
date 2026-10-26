"""Long-history indicators for study 02: monthly series, percentiles, stress onsets and the warning check."""
import statistics

# name -> spec. "num"/"den": source ids; "scale": multiply the ratio (or the value) by this; "warn": "high", "low"
# or None. Sources: FRED ids, or "OFR:<column>" (financial stress index) and "OFRHF:<mnemonic>" (hedge fund monitor).
INDICATORS = {
    "repo_gdp": {"label": "Repo liabilities, all sectors (% GDP)", "group": "Repo and funding",
                 "num": "BOGZ1FL892150005Q", "den": "GDP", "scale": 100 / 1000, "warn": "high"},
    "hf_repo_gdp": {"label": "Hedge-fund repo borrowing (% GDP)", "group": "Repo and funding",
                    "num": "OFRHF:FPF-BORROW_REPO_SUM", "den": "GDP", "scale": 100 / 1e9, "warn": "high"},
    "reserves_gdp": {"label": "Reserves (% GDP)", "group": "Repo and funding",
                     "num": "TOTRESNS", "den": "GDP", "scale": 100, "warn": "low"},
    "cp_bill_bp": {"label": "3m financial CP − 3m bill (bp)", "group": "Repo and funding",
                   "num": "DCPF3M", "minus": "DTB3", "scale": 100, "warn": "high"},
    "ted_bp": {"label": "TED spread (bp, ended 2022)", "group": "Repo and funding",
               "num": "TEDRATE", "scale": 100, "warn": "high"},
    "ofr_funding": {"label": "OFR stress index: funding", "group": "Repo and funding",
                    "num": "OFR:Funding", "scale": 1, "warn": "high"},
    "nfci_leverage": {"label": "NFCI leverage subindex", "group": "Leverage and conditions",
                      "num": "NFCILEVERAGE", "scale": 1, "warn": "high"},
    "nfci": {"label": "NFCI (financial conditions)", "group": "Leverage and conditions",
             "num": "NFCI", "scale": 1, "warn": None},
    "term_premium": {"label": "10y term premium, Kim–Wright (%)", "group": "Bond market",
                     "num": "THREEFYTP10", "scale": 1, "warn": None},
    "curve_10y3m_bp": {"label": "10y − 3m curve (bp)", "group": "Bond market",
                       "num": "T10Y3M", "scale": 100, "warn": "low"},
    "baa_10y_bp": {"label": "Baa − 10y (bp)", "group": "Bond market",
                   "num": "BAA10Y", "scale": 100, "warn": "high"},
    "debt_gdp": {"label": "Federal debt held by public (% GDP)", "group": "Bond market",
                 "num": "FYGFDPUN", "den": "GDP", "scale": 100 / 1000, "warn": "high"},
    "ust10y": {"label": "10-year Treasury yield (%)", "group": "Bond market",
               "num": "DGS10", "scale": 1, "warn": None},
}

QUARTERLY = {"BOGZ1FL892150005Q", "GDP", "FYGFDPUN", "OFRHF:FPF-BORROW_REPO_SUM"}


def month_add(month, n):
    y, m = int(month[:4]), int(month[5:7]) - 1 + n
    return f"{y + m // 12:04d}-{m % 12 + 1:02d}"


def to_monthly(daily, quarterly=False):
    """date -> value  becomes  YYYY-MM -> value.

    Daily and weekly observations are averaged within their month. A quarterly observation, dated on its quarter's
    first day (FRED's and OFR's convention once mapped), is carried to the three months of its quarter. A quarterly
    value dated at quarter end (OFR) is moved to its quarter's first month first.
    """
    out = {}
    if quarterly:
        for date, v in daily.items():
            m = int(date[5:7])
            first = f"{date[:4]}-{(m - 1) // 3 * 3 + 1:02d}"
            for k in range(3):
                out[month_add(first, k)] = v
        return out
    buckets = {}
    for date, v in daily.items():
        buckets.setdefault(date[:7], []).append(v)
    return {m: statistics.fmean(vs) for m, vs in buckets.items()}


def build_indicator(spec, sources):
    """Monthly series for one indicator from monthly source series (dict of id -> YYYY-MM -> value)."""
    num = sources[spec["num"]]
    out = {}
    for month, v in num.items():
        if "den" in spec:
            d = sources[spec["den"]].get(month)
            if d is None:
                continue
            v = v / d
        if "minus" in spec:
            w = sources[spec["minus"]].get(month)
            if w is None:
                continue
            v = v - w
        out[month] = v * spec["scale"]
    return out


def percentile_of(series, value):
    """Share of the series' months at or below value, in percent."""
    xs = list(series.values())
    return 100 * sum(x <= value for x in xs) / len(xs)


def stress_onsets(weekly_nfci, quiet_weeks=26):
    """Dates of the first week NFCI rises above 0 after at least `quiet_weeks` weeks at or below 0."""
    onsets, below = [], 0
    for date in sorted(weekly_nfci):
        if weekly_nfci[date] > 0:
            if below >= quiet_weeks:
                onsets.append(date)
            below = 0
        else:
            below += 1
    return onsets


def warning_check(series, today_value, direction, onset_months, start="1990-01", horizon=24, last_month=None,
                  min_months=12):
    """How often months at least as extreme as today were followed by a stress onset within `horizon` months.

    Only months whose whole horizon is observed (month + horizon <= last_month) count. Returns None for the shares
    when fewer than `min_months` months were as extreme as today: the series has no history at today's level.
    """
    months = sorted(m for m in series if m >= start and month_add(m, horizon) <= last_month)
    followed = lambda m: any(m < o <= month_add(m, horizon) for o in onset_months)  # noqa: E731
    extreme = (lambda v: v >= today_value) if direction == "high" else (lambda v: v <= today_value)
    warn = [m for m in months if extreme(series[m])]
    base = sum(followed(m) for m in months) / len(months) if months else None
    if len(warn) < min_months:
        return {"warning_months": len(warn), "share_followed": None, "base_share": base, "months": len(months)}
    return {"warning_months": len(warn), "share_followed": sum(followed(m) for m in warn) / len(warn),
            "base_share": base, "months": len(months)}


def complete_months(observations, kind):
    """Monthly series from dated observations, without a partial last month.

    kind: "daily" (daily or weekly; the latest month is dropped as possibly partial), "monthly" (one observation per
    month, dated within it; kept whole) or "quarterly" (carried to the three months of its quarter).
    """
    if kind not in ("daily", "monthly", "quarterly"):
        raise ValueError(f"unknown kind {kind!r}")
    monthly = to_monthly(observations, quarterly=kind == "quarterly")
    if kind == "daily" and monthly:
        monthly.pop(max(monthly))
    return monthly
