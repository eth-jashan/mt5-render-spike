"""Pure helpers for inferring a broker's server-time rule. Bar times are server time, read as UTC numbers."""
import calendar
from collections import Counter
from datetime import datetime, timezone

GAP_SECONDS = 24 * 3600


def week_open_hours(bar_times: list) -> dict:
    hours = {}
    ordered = sorted(bar_times)
    for previous, current in zip(ordered, ordered[1:]):
        if current - previous >= GAP_SECONDS:
            day = datetime.fromtimestamp(current, tz=timezone.utc)
            year, week, _ = day.isocalendar()
            hours[f"{year}-W{week:02d}"] = day.hour
    return hours


def infer_rule(hours_by_week: dict) -> dict:
    if not hours_by_week:
        return {"rule": "inconsistent", "hours": {}, "outliers": []}
    common_hour, _ = Counter(hours_by_week.values()).most_common(1)[0]
    outliers = sorted(week for week, hour in hours_by_week.items() if hour != common_hour)
    rule = "constant-midnight" if common_hour == 0 and not outliers else "inconsistent"
    return {"rule": rule, "hours": hours_by_week, "outliers": outliers}


def _nth_sunday(year: int, month: int, n: int) -> int:
    first = calendar.weekday(year, month, 1)  # Monday = 0
    return 1 + (6 - first) % 7 + 7 * (n - 1)


def expected_offset_hours(utc_ts: int, rule: str) -> int:
    if rule != "EET+US-DST":
        raise ValueError(f"unknown rule {rule}")
    year = datetime.fromtimestamp(utc_ts, tz=timezone.utc).year
    start = calendar.timegm((year, 3, _nth_sunday(year, 3, 2), 7, 0, 0))   # 02:00 EST = 07:00 UTC
    end = calendar.timegm((year, 11, _nth_sunday(year, 11, 1), 6, 0, 0))   # 02:00 EDT = 06:00 UTC
    return 3 if start <= utc_ts < end else 2
