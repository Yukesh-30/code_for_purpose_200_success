from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.core.config import Settings, get_settings
from app.schemas.api import ChartData
from app.services.time_context import DateRange


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    reason: str | None = None
    confidence_penalty: float = 0.0


def fail_closed(state: dict[str, Any], status: str, reason: str) -> dict[str, Any]:
    state["status"] = status
    state["analysis"] = {"reason": reason, "method": "production_guard"}
    state["validation_error"] = reason
    state["chart"] = ChartData(type="none")
    state["rows"] = []
    state["columns"] = []
    state["confidence"] = 0.0
    state.setdefault("warnings", []).append(reason)
    return state


class RequestGuard:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def validate_date_range(self, state: dict[str, Any]) -> GuardResult:
        date_range = state.get("date_range")
        as_of = state.get("as_of_date")
        today = datetime.now(ZoneInfo(self.settings.timezone)).date()
        if as_of and as_of > today:
            return GuardResult(False, "as_of_date cannot be in the future.")
        if not isinstance(date_range, DateRange):
            return GuardResult(False, "No validated time range is available.")
        if date_range.start > date_range.end:
            return GuardResult(False, "Invalid time range: start date is after end date.")
        reference_date = as_of or today
        if date_range.end > reference_date:
            return GuardResult(False, "Time range exceeds the allowed as_of_date.")
        return GuardResult(True)


class DataContractValidator:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def validate(self, intent: str, rows: list[dict[str, Any]], columns: list[str], state: dict[str, Any]) -> GuardResult:
        if intent == "forecast":
            return self._validate_forecast(rows, columns, state)
        if intent == "anomaly":
            return self._validate_anomaly(rows, columns, state)
        return self._validate_analytics(rows, columns)

    def _validate_analytics(self, rows: list[dict[str, Any]], columns: list[str]) -> GuardResult:
        if len(rows) < self.settings.min_analysis_rows:
            return GuardResult(False, f"Insufficient data: found {len(rows)} row(s), need at least {self.settings.min_analysis_rows}.")
        if not columns:
            return GuardResult(False, "Query returned no columns.")
        return GuardResult(True)

    def _validate_forecast(self, rows: list[dict[str, Any]], columns: list[str], state: dict[str, Any]) -> GuardResult:
        required = {"cashflow_date", "inflow", "outflow", "net_cashflow", "closing_balance"}
        missing = required - set(columns)
        if missing:
            return GuardResult(False, f"Forecast data missing required column(s): {', '.join(sorted(missing))}.")
        if len(rows) < self.settings.min_forecast_history_days:
            return GuardResult(False, f"Insufficient forecast history: found {len(rows)} day(s), need at least {self.settings.min_forecast_history_days}.")
        return self._validate_dates_and_numbers(rows, ("cashflow_date",), ("inflow", "outflow", "net_cashflow"), state)

    def _validate_anomaly(self, rows: list[dict[str, Any]], columns: list[str], state: dict[str, Any]) -> GuardResult:
        required = {"transaction_date", "amount", "transaction_type"}
        missing = required - set(columns)
        if missing:
            return GuardResult(False, f"Anomaly data missing required column(s): {', '.join(sorted(missing))}.")
        if len(rows) < self.settings.min_anomaly_transactions:
            return GuardResult(False, f"Insufficient anomaly data: found {len(rows)} transaction(s), need at least {self.settings.min_anomaly_transactions}.")
        return self._validate_dates_and_numbers(rows, ("transaction_date",), ("amount",), state)

    def _validate_dates_and_numbers(
        self,
        rows: list[dict[str, Any]],
        date_columns: tuple[str, ...],
        numeric_columns: tuple[str, ...],
        state: dict[str, Any],
    ) -> GuardResult:
        as_of = state.get("as_of_date") or datetime.now(ZoneInfo(self.settings.timezone)).date()
        for index, row in enumerate(rows, start=1):
            for column in date_columns:
                try:
                    parsed = date.fromisoformat(str(row.get(column, ""))[:10])
                except ValueError:
                    return GuardResult(False, f"Invalid date in row {index}, column {column}.")
                if parsed > as_of:
                    return GuardResult(False, f"Future date found in row {index}, column {column}.")
            for column in numeric_columns:
                try:
                    float(row.get(column))
                except (TypeError, ValueError):
                    return GuardResult(False, f"Invalid numeric value in row {index}, column {column}.")

            if {"inflow", "outflow", "net_cashflow"}.issubset(row):
                inflow = float(row.get("inflow") or 0)
                outflow = float(row.get("outflow") or 0)
                net = float(row.get("net_cashflow") or 0)
                if abs((inflow - outflow) - net) > 0.01:
                    return GuardResult(False, f"Cashflow arithmetic mismatch in row {index}.")
        return GuardResult(True)


class ConfidenceScorer:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def score(self, *, base: float, rows_count: int, validation_ok: bool, schema_tables: int, warnings: list[str]) -> float:
        score = max(0.0, min(1.0, base))
        if not validation_ok:
            return 0.0
        if rows_count < self.settings.min_analysis_rows:
            score *= 0.4
        if schema_tables <= 0:
            score *= 0.5
        if warnings:
            score -= min(0.25, 0.05 * len(warnings))
        return round(max(0.0, min(1.0, score)), 2)


class ResponseConsistencyGuard:
    def validate(self, state: dict[str, Any]) -> GuardResult:
        status = state.get("status")
        if status != "success":
            return GuardResult(True)
        rows = state.get("rows", [])
        chart = state.get("chart")
        analysis = state.get("analysis", {})
        if not rows and state.get("intent", {}).get("intent") != "anomaly":
            return GuardResult(False, "Success response has no supporting data.")
        if chart and getattr(chart, "type", "none") != "none" and getattr(chart, "series", None) is None:
            return GuardResult(False, "Chart is missing series data.")
        if {"totals"}.issubset(analysis) and not {"inflow", "outflow", "net_cashflow"}.issubset(rows[0].keys() if rows else set()):
            return GuardResult(False, "Cashflow analysis totals do not match supporting row shape.")
        return GuardResult(True)
