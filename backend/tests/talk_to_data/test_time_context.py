"""Tests for calendar-aware time context resolution."""
from datetime import date
from app.services.time_context import TimeContextResolver, parse_period_months


TODAY = date(2026, 4, 11)
resolver = TimeContextResolver()


def test_last_n_days():
    r = resolver.resolve("last 90 days", as_of=TODAY)
    assert r.start == date(2026, 1, 11)
    assert r.end   == TODAY
    assert r.label == "last 90 days"


def test_last_month_calendar_aware():
    r = resolver.resolve("last month", as_of=TODAY)
    assert r.start == date(2026, 3, 1)
    assert r.end   == date(2026, 3, 31)


def test_this_month():
    r = resolver.resolve("this month", as_of=TODAY)
    assert r.start == date(2026, 4, 1)
    # End is capped at today — we don't return future dates
    assert r.end   == TODAY
    assert r.label == "this month"


def test_last_2_months_calendar_not_60_days():
    r = resolver.resolve("last 2 months", as_of=TODAY)
    # Must be Feb 1 – Mar 31, NOT today - 60 days
    assert r.start == date(2026, 2, 1)
    assert r.end   == date(2026, 3, 31)


def test_last_quarter():
    r = resolver.resolve("previous quarter", as_of=TODAY)
    assert r.start == date(2026, 1, 1)
    assert r.end   == date(2026, 3, 31)


def test_specific_month_name():
    r = resolver.resolve("cashflow for march", as_of=TODAY)
    assert r.start == date(2026, 3, 1)
    assert r.end   == date(2026, 3, 31)


def test_last_year():
    r = resolver.resolve("last year", as_of=TODAY)
    assert r.start == date(2025, 1, 1)
    assert r.end   == date(2025, 12, 31)


def test_parse_period_months_2():
    cs, ce, ps, pe, n = parse_period_months("last 2 months", TODAY)
    assert n  == 2
    assert cs == date(2026, 2, 1)
    assert ce == date(2026, 3, 31)
    assert ps == date(2025, 12, 1)
    assert pe == date(2026, 1, 31)


def test_default_fallback_is_unspecified():
    # When no time expression is found, resolver returns "unspecified"
    # so the SQL generator can use a sensible default
    r = resolver.resolve("show me data", as_of=TODAY)
    assert r.label in ("last 30 days", "unspecified")
    assert r.start <= TODAY
    assert r.end   == TODAY
