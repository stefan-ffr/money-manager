"""Unit tests for recurring-transaction date advancement.

These import the service module, which transitively imports SQLAlchemy models;
they run in CI where backend dependencies are installed.
"""

from datetime import date

import pytest

pytest.importorskip("sqlalchemy")

from app.services.recurring_service import advance_date  # noqa: E402


def test_daily():
    assert advance_date(date(2026, 1, 31), "daily") == date(2026, 2, 1)


def test_weekly():
    assert advance_date(date(2026, 1, 31), "weekly") == date(2026, 2, 7)


def test_monthly_clamps_to_month_end():
    # Jan 31 -> Feb 28 (2026 is not a leap year)
    assert advance_date(date(2026, 1, 31), "monthly") == date(2026, 2, 28)


def test_monthly_rolls_over_year():
    assert advance_date(date(2026, 12, 15), "monthly") == date(2027, 1, 15)


def test_yearly_handles_leap_day():
    assert advance_date(date(2024, 2, 29), "yearly") == date(2025, 2, 28)


def test_yearly_regular():
    assert advance_date(date(2026, 6, 2), "yearly") == date(2027, 6, 2)
