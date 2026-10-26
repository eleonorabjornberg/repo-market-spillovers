"""Means, slopes and percentile bootstrap intervals, stdlib only."""
import math
import statistics


def mean(xs):
    return statistics.fmean(xs) if xs else math.nan


def boot_means(xs, draws, rng):
    """`draws` bootstrap means of xs (resampled with replacement, same size); empty when xs is empty."""
    if not xs:
        return []
    n = len(xs)
    return [statistics.fmean(rng.choices(xs, k=n)) for _ in range(draws)]


def percentile(sorted_xs, q):
    k = (len(sorted_xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(sorted_xs) - 1)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (k - lo)


def interval(draws):
    s = sorted(d for d in draws if not math.isnan(d))
    return (percentile(s, 0.025), percentile(s, 0.975)) if s else (math.nan, math.nan)


def ols_slope(xs, ys):
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else math.nan


def slope_with_interval(xs, ys, draws, rng):
    """OLS slope of ys on xs and a percentile interval from resampling (x, y) pairs."""
    pairs = list(zip(xs, ys))
    boot = []
    for _ in range(draws):
        s = rng.choices(pairs, k=len(pairs))
        boot.append(ols_slope([p[0] for p in s], [p[1] for p in s]))
    return ols_slope(xs, ys), interval(boot)
