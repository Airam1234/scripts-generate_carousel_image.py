"""Time helpers and the provider's delivery calendar rules.

All datetimes are stored as naive UK local time (Europe/London by default),
because every session is delivered and inspected in UK time.

Delivery calendar:
  * First day of learning for new starts: week 3 or week 4 of the month
    (days 15-28).
  * Monthly sessions: first week of the month (days 1-7).
  * Additional sessions: any time in the month.
"""
import calendar
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from flask import current_app, has_app_context


def now():
    tz = current_app.config["TIMEZONE"] if has_app_context() else "Europe/London"
    return datetime.now(ZoneInfo(tz)).replace(tzinfo=None, microsecond=0)


def today():
    return now().date()


def week_of_month(d):
    return (d.day - 1) // 7 + 1


def is_first_day_window(d):
    """Weeks 3 and 4 of the month."""
    return 15 <= d.day <= 28


def is_monthly_window(d):
    """First week of the month."""
    return 1 <= d.day <= 7


def weekday_in_first_week(year, month, weekday):
    """The date of `weekday` (0=Mon) that falls in days 1-7 of the month."""
    for day in range(1, 8):
        d = date(year, month, day)
        if d.weekday() == weekday:
            return d
    raise ValueError("unreachable")


def add_months(year, month, n):
    total = year * 12 + (month - 1) + n
    return total // 12, total % 12 + 1


def month_bounds(year, month):
    start = datetime(year, month, 1)
    y, m = add_months(year, month, 1)
    return start, datetime(y, m, 1)


def parse_month(value, default=None):
    """Parse 'YYYY-MM' into (year, month)."""
    try:
        y, m = value.split("-")
        y, m = int(y), int(m)
        if 1 <= m <= 12 and 2000 <= y <= 2100:
            return y, m
    except (AttributeError, ValueError):
        pass
    if default is not None:
        return default
    d = today()
    return d.year, d.month


def month_label(year, month):
    return f"{calendar.month_name[month]} {year}"


def minutes_between(a, b):
    return int((b - a) / timedelta(minutes=1))
