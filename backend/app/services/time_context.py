from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import Settings, get_settings

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date
    label: str
    is_explicit: bool = True


def _subtract_months(d: date, n: int) -> date:
    """Subtract n calendar months from date d, clamping to valid day."""
    month = d.month - n
    year  = d.year
    while month <= 0:
        month += 12
        year  -= 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last_day))


def _month_start(d: date) -> date:
    return d.replace(day=1)


def _month_end(d: date) -> date:
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


class TimeContextResolver:
    """
    Calendar-aware time parser.
    - "last N months"     → exact calendar months, NOT N*30 days
    - "previous N months" → the N months before the current window
    - Never produces future dates
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def today(self) -> date:
        return datetime.now(self.tzinfo()).date()

    def resolve(self, text: str, as_of: date | None = None) -> DateRange:
        normalized = text.lower()
        today      = as_of or self.today()

        # ── "last N days" ─────────────────────────────────────────────────────
        m = re.search(r"last\s+(\d{1,4})\s+days?", normalized)
        if m:
            n = max(int(m.group(1)), 1)
            return DateRange(start=today - timedelta(days=n), end=today, label=f"last {n} days")

        # ── "last N weeks" ────────────────────────────────────────────────────
        m = re.search(r"last\s+(\d{1,2})\s+weeks?", normalized)
        if m:
            n = int(m.group(1))
            return DateRange(start=today - timedelta(weeks=n), end=today, label=f"last {n} weeks")

        # ── "last N months" — CALENDAR AWARE ─────────────────────────────────
        m = re.search(r"last\s+(\d{1,2})\s+months?", normalized)
        if m:
            n     = int(m.group(1))
            start = _month_start(_subtract_months(today, n))
            end   = min(today, _month_end(_subtract_months(today, 1)))
            return DateRange(start=start, end=end, label=f"last {n} months")

        # ── "previous N months" — window BEFORE last N months ─────────────────
        m = re.search(r"previous\s+(\d{1,2})\s+months?", normalized)
        if m:
            n          = int(m.group(1))
            curr_start = _month_start(_subtract_months(today, n))
            prev_end   = curr_start - timedelta(days=1)
            prev_start = _month_start(_subtract_months(prev_end, n - 1))
            return DateRange(start=prev_start, end=prev_end, label=f"previous {n} months")

        # ── Specific month name ───────────────────────────────────────────────
        for month_name, month_num in MONTH_NAMES.items():
            if re.search(rf"\b{month_name}\b", normalized):
                year = today.year
                if month_num > today.month:
                    year -= 1
                end_day = calendar.monthrange(year, month_num)[1]
                return DateRange(
                    start=date(year, month_num, 1),
                    end=min(today, date(year, month_num, end_day)),
                    label=f"{month_name.capitalize()} {year}",
                )

        # ── "last month" / "previous month" ──────────────────────────────────
        if "last month" in normalized or "previous month" in normalized:
            end   = _month_end(_subtract_months(today, 1))
            start = _month_start(end)
            return DateRange(start=start, end=end, label="last month")

        # ── "this month" / "current month" ───────────────────────────────────
        if "this month" in normalized or "current month" in normalized:
            return DateRange(
                start=_month_start(today),
                end=today,
                label="this month",
            )

        # ── "last quarter" / "previous quarter" ──────────────────────────────
        if "previous quarter" in normalized or "last quarter" in normalized:
            q          = (today.month - 1) // 3 + 1
            end_month  = (q - 1) * 3
            year       = today.year
            if end_month == 0:
                end_month = 12
                year     -= 1
            start_month = end_month - 2
            return DateRange(
                start=date(year, start_month, 1),
                end=date(year, end_month, calendar.monthrange(year, end_month)[1]),
                label="last quarter",
            )

        # ── "this quarter" / "current quarter" ───────────────────────────────
        if "this quarter" in normalized or "current quarter" in normalized:
            q           = (today.month - 1) // 3 + 1
            start_month = (q - 1) * 3 + 1
            end_month   = start_month + 2
            return DateRange(
                start=date(today.year, start_month, 1),
                end=min(today, date(today.year, end_month, calendar.monthrange(today.year, end_month)[1])),
                label="this quarter",
            )

        # ── "yesterday" ───────────────────────────────────────────────────────
        if "yesterday" in normalized:
            d = today - timedelta(days=1)
            return DateRange(start=d, end=d, label="yesterday")

        # ── "today" ───────────────────────────────────────────────────────────
        if "today" in normalized:
            return DateRange(start=today, end=today, label="today")

        # ── "this year" / "current year" ──────────────────────────────────────
        if "this year" in normalized or "current year" in normalized:
            return DateRange(start=date(today.year, 1, 1), end=today, label="this year")

        # ── "last year" / "previous year" ─────────────────────────────────────
        if "last year" in normalized or "previous year" in normalized:
            y = today.year - 1
            return DateRange(start=date(y, 1, 1), end=date(y, 12, 31), label=f"year {y}")

        # ── No implicit window. Caller must clarify if selected metric needs time.
        return DateRange(start=today, end=today, label="unspecified", is_explicit=False)

    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.settings.timezone)


# ── Exported helper for PlannerAgent ─────────────────────────────────────────
def parse_period_months(question: str, today: date) -> tuple[date, date, date, date, int]:
    """
    Parse "last N months vs previous N months" from a question.
    Returns: (curr_start, curr_end, prev_start, prev_end, n_months)
    Uses calendar-aware month arithmetic — never fixed 30-day approximations.
    """
    m = re.search(r"(\d{1,2})\s+months?", question.lower())
    n = int(m.group(1)) if m else 1

    # Current window: last N complete calendar months
    curr_end   = _month_end(_subtract_months(today, 1))
    curr_start = _month_start(_subtract_months(today, n))

    # Previous window: N months immediately before current window
    prev_end   = curr_start - timedelta(days=1)
    prev_start = _month_start(_subtract_months(prev_end, n - 1))

    return curr_start, curr_end, prev_start, prev_end, n
