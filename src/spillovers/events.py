"""Panel days, reserve regimes, calendar events and the days excluded from the study."""
import csv
import json

REGIMES = {
    "scarce_2018_19": ("2018-01-01", "2019-12-31"),
    "covid_2020": ("2020-01-01", "2020-12-31"),
    "floor_2021_23": ("2021-01-01", "2023-12-31"),
    "transition_2024": ("2024-01-01", "2024-12-31"),
    "scarce_2025_26": ("2025-01-01", "2099-12-31"),
}
COMPARED_REGIMES = ("scarce_2018_19", "floor_2021_23", "scarce_2025_26")
EVENTS = ("month_end", "month_start", "quarter_end", "coupon_settle", "tax")


def regime_of(date):
    for name, (start, end) in REGIMES.items():
        if start <= date <= end:
            return name
    raise ValueError(f"{date} is in no regime")


def read_panel(path):
    """Panel rows in date order, with the fields this study uses as floats (None when empty)."""
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            num = lambda k: float(r[k]) if r[k] not in ("", None) else None  # noqa: E731
            rows.append({
                "date": r["date"],
                "sofr": num("sofr"),
                "iorb": num("iorb"),
                "coupons": num("treasury_settlement_coupons"),
                "tax_date": r["tax_date"] == "1",
            })
    dates = [r["date"] for r in rows]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("panel dates are not strictly increasing")
    return rows


def fomc_decision_dates(path):
    """Meeting end dates from every schedule announcement (cancelled meetings left out), unscheduled meetings and
    notation votes. A meeting a later schedule moved leaves its old date in the set; excluding one extra day is harmless.
    """
    with open(path) as f:
        cal = json.load(f)
    cancelled = {c["meeting_start"] for c in cal["cancellations"]}
    dates = {m["end"] for a in cal["schedule_announcements"] for m in a["meetings"] if m["start"] not in cancelled}
    dates |= {m["date"] for m in cal["unscheduled_meetings"]}
    dates |= {v["date"] for v in cal["notation_votes"]}
    return dates


def classify(rows, fomc_dates):
    """date -> set of event labels, and the set of excluded dates.

    A date is excluded when it is an FOMC decision day or IORB differs from the previous panel day. Month boundaries
    are read from the panel's own business days, so the last business day is the last panel date in the month.
    """
    dates = [r["date"] for r in rows]
    labels = {d: set() for d in dates}
    excluded = set()
    for prev, row in zip(rows, rows[1:]):
        if row["iorb"] != prev["iorb"]:
            excluded.add(row["date"])
    excluded |= fomc_dates & set(dates)

    for i, d in enumerate(dates):
        nxt = dates[i + 1] if i + 1 < len(dates) else None
        prv = dates[i - 1] if i > 0 else None
        if nxt is not None and nxt[:7] != d[:7]:
            labels[d].add("month_end")
            if d[5:7] in ("03", "06", "09", "12"):
                labels[d].add("quarter_end")
        if prv is not None and prv[:7] != d[:7]:
            labels[d].add("month_start")
    for row in rows:
        d = row["date"]
        turn = labels[d] & {"month_end", "month_start"}
        if not turn and 13 <= int(d[8:10]) <= 17 and (row["coupons"] or 0) > 0:
            labels[d].add("coupon_settle")
        if not turn and row["tax_date"]:
            labels[d].add("tax")
    # the panel's last date has no successor, so whether it is a month-end is unknown: drop it
    excluded.add(dates[-1])
    return labels, excluded
