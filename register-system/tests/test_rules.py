from datetime import date, datetime

from app.models import SessionType
from app.timeutil import is_first_day_window, is_monthly_window, weekday_in_first_week
from app.views.sessions import schedule_problem


def test_first_day_window_is_weeks_three_and_four():
    assert not is_first_day_window(date(2026, 9, 14))
    assert is_first_day_window(date(2026, 9, 15))
    assert is_first_day_window(date(2026, 9, 28))
    assert not is_first_day_window(date(2026, 9, 29))


def test_monthly_window_is_first_week():
    assert is_monthly_window(date(2026, 10, 1))
    assert is_monthly_window(date(2026, 10, 7))
    assert not is_monthly_window(date(2026, 10, 8))


def test_weekday_in_first_week():
    d = weekday_in_first_week(2026, 10, 1)  # Tuesday
    assert d.weekday() == 1 and d.day <= 7


def test_schedule_problem(app):
    assert schedule_problem(SessionType.MONTHLY, date(2026, 10, 12))
    assert schedule_problem(SessionType.FIRST_DAY, date(2026, 10, 2))
    assert schedule_problem(SessionType.ADDITIONAL, date(2026, 10, 12)) is None
    assert schedule_problem(SessionType.FIRST_DAY, date(2026, 10, 20)) is None
