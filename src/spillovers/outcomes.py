"""The wider-market outcomes and how their daily change is measured."""
import csv
import math

# FRED id -> (outcome name, how the daily change is measured)
#   "bp":        (x_t - x_s) * 100, for series quoted in percent
#   "level":     x_t - x_s
#   "logpct":    100 * ln(x_t / x_s)
#   "bp_iorb":   change in (x - IORB), in bp; IORB comes from the panel
FRED_SERIES = {
    "DGS10": ("ust10y_bp", "bp"),
    "DGS2": ("ust2y_bp", "bp"),
    "T10Y2Y": ("curve_10s2s_bp", "bp"),
    "VIXCLS": ("vix_pts", "level"),
    "SP500": ("spx_pct", "logpct"),
    "BAA10Y": ("baa_10y_bp", "bp"),
    "DTWEXBGS": ("usd_broad_pct", "logpct"),
    "RIFSPPFAAD01NB": ("cp_on_fin_iorb_bp", "bp_iorb"),
    "RIFSPPFAAD30NB": ("cp30_iorb_bp", "bp_iorb"),
    "DTB4WK": ("bill4w_iorb_bp", "bp_iorb"),
    "BAMLH0A0HYM2": ("hy_oas_bp", "bp"),
    "BAMLC0A0CM": ("ig_oas_bp", "bp"),
}

# cp_on_fin_iorb_bp replaced cp30_iorb_bp after the first run: see "Amendments" in docs/design-event-study-01.md
MAIN_OUTCOMES = ("ust10y_bp", "vix_pts", "baa_10y_bp", "cp_on_fin_iorb_bp")

# outcomes FRED serves only for the last three years: reported for the latest regime only, never contrasted
RECENT_ONLY = ("hy_oas_bp", "ig_oas_bp")


def read_fred(path):
    """date -> float, skipping FRED's missing marker ('.' or empty)."""
    out = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for date, value in reader:
            if value not in ("", "."):
                out[date] = float(value)
    return out


def daily_changes(dates, series, kind, iorb=None):
    """Change from the previous panel date to each panel date; None where either end is missing.

    `dates` are the panel's business days in order. The change on dates[i] is measured against dates[i - 1], never
    against an earlier day, so a market holiday inside the panel gives a missing change rather than a two-day one.
    """
    changes = {}
    for prev, date in zip(dates, dates[1:]):
        a, b = series.get(prev), series.get(date)
        if a is None or b is None:
            changes[date] = None
        elif kind == "bp":
            changes[date] = (b - a) * 100
        elif kind == "level":
            changes[date] = b - a
        elif kind == "logpct":
            changes[date] = 100 * math.log(b / a)
        elif kind == "bp_iorb":
            changes[date] = ((b - iorb[date]) - (a - iorb[prev])) * 100
        else:
            raise ValueError(f"unknown change kind {kind!r}")
    return changes
