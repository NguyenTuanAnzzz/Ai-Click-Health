"""Shared math helpers for temporal BEFAST analyzers."""


def clamp(v: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, v))


def linear_slope(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean_x = (n - 1) / 2
    mean_y = sum(values) / n
    num = den = 0.0
    for i, y in enumerate(values):
        num += (i - mean_x) * (y - mean_y)
        den += (i - mean_x) ** 2
    return 0.0 if den == 0 else num / den


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5


def detrend(values: list[float]) -> list[float]:
    slope = linear_slope(values)
    return [v - slope * i for i, v in enumerate(values)]


def risk_from_score(score: float) -> str:
    if score < 65:
        return "high"
    if score < 80:
        return "medium"
    return "low"
