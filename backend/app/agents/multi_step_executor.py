from __future__ import annotations

from typing import Any

from app.agents.forecast import ForecastAgent
from app.agents.sql_validator import SQLValidator
from app.agents.state import AgentState
from app.core.config import Settings, get_settings
from app.services.production_guard import DataContractValidator, fail_closed
from app.services.query_executor import QueryExecutor


ACTION_TABLES: dict[str, list[str]] = {
    "cashflow_summary": ["bank_transactions"],
    "vendor_breakdown": ["bank_transactions"],
    "category_breakdown": ["bank_transactions"],
    "forecast": ["bank_transactions"],
}


def _where_date_range(start: str | None, end: str) -> str:
    if start:
        return f"transaction_date BETWEEN DATE '{start}' AND DATE '{end}'"
    return f"transaction_date <= DATE '{end}'"


class MultiStepExecutor:
    """Validate and execute each planned step independently."""

    def __init__(
        self,
        executor: QueryExecutor,
        settings: Settings | None = None,
        validator: SQLValidator | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._db = executor
        self._forecast = ForecastAgent(self.settings)
        self._validator = validator or SQLValidator(self.settings)
        self._data_validator = DataContractValidator(self.settings)

    def execute(self, state: AgentState) -> AgentState:
        plan = state.get("plan", {})
        steps = plan.get("steps", [])
        business_id = int(state["business_id"])
        live_context = state.get("schema_context", {})
        results: dict[str, Any] = {}
        validations: list[dict[str, Any]] = []

        if not steps:
            return fail_closed(state, "blocked", "Planner produced no executable steps.")

        for step in steps:
            action = step["action"]
            result_key = step["result_key"]
            if action == "recommendations":
                validations.append({"step": result_key, "ok": True, "skipped_execution": True})
                continue

            schema_context = self._schema_context_for_step(action, live_context)
            if not schema_context:
                return fail_closed(state, "blocked", f"No schema context selected for step {result_key}.")

            sql = self._sql_for_step(action, business_id, step)
            validation = self._validator.validate(sql, business_id=business_id, schema_context=schema_context)
            validations.append({"step": result_key, "ok": validation.ok, "error": validation.error, "sql": validation.sql})
            if not validation.ok:
                state["step_validations"] = validations
                return fail_closed(state, "blocked", f"SQL validation failed for step {result_key}: {validation.error}")

            try:
                columns, rows, truncated = self._db._fetch_sync(validation.sql, validated=True)
            except Exception as exc:
                state["step_validations"] = validations
                return fail_closed(state, "error", f"Execution failed for step {result_key}: {exc}")

            if truncated:
                state.setdefault("warnings", []).append(f"Step {result_key} was truncated to {self.settings.max_result_rows} rows.")

            if action == "forecast":
                tmp_state: AgentState = dict(state)  # type: ignore[assignment]
                tmp_state["rows"] = rows
                tmp_state["columns"] = columns
                tmp_state["horizon_days"] = step.get("horizon_days")
                contract = self._data_validator.validate("forecast", rows, columns, tmp_state)
                if not contract.ok:
                    state["step_validations"] = validations
                    return fail_closed(state, "insufficient_data", f"Forecast step invalid: {contract.reason}")
                tmp_state = self._forecast.forecast(tmp_state)
                if tmp_state.get("status") != "success":
                    state["step_validations"] = validations
                    return fail_closed(state, tmp_state.get("status", "error"), tmp_state.get("analysis", {}).get("reason", "Forecast step failed."))
                results[result_key] = tmp_state.get("forecast", {})
                if tmp_state.get("chart"):
                    state["forecast_chart"] = tmp_state["chart"]
            elif action == "cashflow_summary":
                if not rows:
                    state["step_validations"] = validations
                    return fail_closed(state, "insufficient_data", f"No cashflow data for step {result_key}.")
                results[result_key] = self._summarise_cashflow(rows)
                results[f"{result_key}_rows"] = rows
            else:
                results[result_key] = rows

        state["step_results"] = results
        state["step_validations"] = validations
        return state

    def _schema_context_for_step(self, action: str, live_context: dict[str, list[str]]) -> dict[str, list[str]]:
        selected: dict[str, list[str]] = {}
        for table in ACTION_TABLES.get(action, []):
            if table in live_context:
                selected[table] = live_context[table]
        return selected

    def _sql_for_step(self, action: str, business_id: int, step: dict[str, Any]) -> str:
        start = step.get("start")
        end = step.get("end")
        if not end:
            raise ValueError(f"Step {step.get('result_key')} is missing an end date.")

        if action == "cashflow_summary":
            return self._sql_cashflow(business_id, start, end)
        if action == "vendor_breakdown":
            return self._sql_vendor_breakdown(business_id, start, end)
        if action == "category_breakdown":
            return self._sql_category_breakdown(business_id, start, end)
        if action == "forecast":
            return self._sql_cashflow(business_id, None, end)
        raise ValueError(f"Unsupported plan action: {action}")

    def _sql_cashflow(self, business_id: int, start: str | None, end: str) -> str:
        return f"""
SELECT
  transaction_date AS cashflow_date,
  COALESCE(SUM(CASE WHEN transaction_type='credit' THEN amount ELSE 0 END),0) AS inflow,
  COALESCE(SUM(CASE WHEN transaction_type='debit'  THEN amount ELSE 0 END),0) AS outflow,
  COALESCE(SUM(CASE WHEN transaction_type='credit' THEN amount ELSE -amount END),0) AS net_cashflow,
  (ARRAY_AGG(balance_after_transaction ORDER BY id DESC))[1] AS closing_balance
FROM bank_transactions
WHERE business_id = {business_id}
  AND {_where_date_range(start, end)}
GROUP BY 1
ORDER BY 1
LIMIT {self.settings.max_result_rows}""".strip()

    def _sql_vendor_breakdown(self, business_id: int, start: str | None, end: str) -> str:
        return f"""
SELECT
  merchant_name AS vendor,
  SUM(amount) AS total_spend,
  COUNT(*) AS txn_count,
  ROUND(100.0 * SUM(amount) / NULLIF(SUM(SUM(amount)) OVER (), 0), 1) AS pct_of_total
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_type = 'debit'
  AND {_where_date_range(start, end)}
  AND merchant_name IS NOT NULL
GROUP BY merchant_name
ORDER BY total_spend DESC
LIMIT {self.settings.max_result_rows}""".strip()

    def _sql_category_breakdown(self, business_id: int, start: str | None, end: str) -> str:
        return f"""
SELECT
  category,
  SUM(CASE WHEN transaction_type='debit' THEN amount ELSE 0 END) AS total_spent,
  SUM(CASE WHEN transaction_type='credit' THEN amount ELSE 0 END) AS total_received,
  COUNT(*) AS txn_count,
  ROUND(100.0 * SUM(CASE WHEN transaction_type='debit' THEN amount ELSE 0 END)
        / NULLIF(SUM(SUM(CASE WHEN transaction_type='debit' THEN amount ELSE 0 END)) OVER (), 0), 1) AS pct_of_spend
FROM bank_transactions
WHERE business_id = {business_id}
  AND {_where_date_range(start, end)}
  AND category IS NOT NULL
GROUP BY category
ORDER BY total_spent DESC
LIMIT {self.settings.max_result_rows}""".strip()

    def _summarise_cashflow(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "inflow": round(sum(float(row.get("inflow") or 0) for row in rows), 2),
            "outflow": round(sum(float(row.get("outflow") or 0) for row in rows), 2),
            "net": round(sum(float(row.get("net_cashflow") or 0) for row in rows), 2),
            "days": len(rows),
        }
