from __future__ import annotations

"""
SQLAgent — Dynamic SQL generation driven by SemanticParser output.

No fixed keyword routing. Instead:
1. Reads the ParsedQuery from state (built by SemanticParser)
2. Selects the right SQL template based on concepts + tables
3. Applies the correct aggregation, grouping, and time range
4. Falls back gracefully if schema changes
"""

from app.agents.state import AgentState
from app.core.config import Settings, get_settings


class SQLAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def generate(self, state: AgentState) -> AgentState:
        intent      = state.get("intent", {})
        business_id = int(state["business_id"])
        date_range  = state["date_range"]
        parsed      = state.get("parsed_query")  # from SemanticParser

        if state.get("schema_error"):
            state["sql"] = ""
            state["validation_error"] = state["schema_error"]
            return state

        start = date_range.start.isoformat()
        end   = date_range.end.isoformat()
        intent_type = intent.get("intent", "analytics")

        # ── Use parsed query metadata if available ────────────────────────────
        concepts   = intent.get("concepts", []) or (parsed.concepts if parsed else [])
        tables     = intent.get("tables",   []) or (parsed.tables   if parsed else [])
        group_by   = intent.get("group_by")     or (parsed.group_by if parsed else None)
        entities   = intent.get("entities", {}) or (parsed.entities if parsed else {})

        # ── Forecast: always needs history ────────────────────────────────────
        if intent_type == "forecast":
            state["sql"] = self._cashflow_history_sql(business_id, end, limit=self.settings.max_result_rows)
            return state

        # ── Anomaly: raw transactions ─────────────────────────────────────────
        if intent_type == "anomaly":
            state["sql"] = self._transactions_sql(business_id, start, end, limit=self.settings.max_result_rows)
            return state

        # ── Route by primary concept + table ─────────────────────────────────
        # This replaces all the fixed keyword checks with concept-driven routing

        if not tables:
            state["sql"] = ""
            state["validation_error"] = "No table was selected by the semantic/schema layer."
            return state

        primary_table = tables[0]

        # Invoice / receivables
        if primary_table == "invoice_records" or "invoicing" in concepts:
            if "customer" in concepts or group_by == "customer_name":
                state["sql"] = self._top_customers_sql(business_id)
            else:
                state["sql"] = self._invoice_sql(business_id)
            return state

        # Vendor / payables
        if primary_table == "vendor_payments" or "obligations" in concepts:
            if "loan_obligations" in tables or any(c in concepts for c in ["loan", "emi"]):
                state["sql"] = self._loan_sql(business_id)
            elif "salary_schedule" in tables:
                state["sql"] = self._salary_sql(business_id)
            else:
                state["sql"] = self._vendor_sql(business_id)
            return state

        # Risk scores
        if primary_table == "risk_scores" or "risk_health" in concepts:
            state["sql"] = self._risk_sql(business_id)
            return state

        # Recommendations
        if primary_table == "banking_product_recommendations" or "recommendations" in concepts:
            state["sql"] = self._recommendations_sql(business_id)
            return state

        # Expenses table
        if primary_table == "expenses":
            state["sql"] = self._expense_sql(business_id, start, end)
            return state

        # Alerts
        if primary_table == "alerts":
            state["sql"] = self._alerts_sql(business_id)
            return state

        # ── Bank transactions — most queries land here ────────────────────────
        # Determine the right aggregation based on concepts + group_by

        # Closing balance
        if "closing_balance" in concepts or (
            "net_position" in concepts and not group_by and
            not any(c in concepts for c in ["money_in", "money_out"])
        ):
            state["sql"] = self._balance_sql(business_id)
            return state

        # Category / dimension breakdown
        if group_by in ("category", "merchant_name", "payment_mode"):
            if group_by == "merchant_name":
                state["sql"] = self._vendor_spend_sql(business_id, start, end)
            elif group_by == "category":
                state["sql"] = self._top_categories_sql(business_id, start, end)
            else:
                state["sql"] = self._category_breakdown_sql(business_id, start, end)
            return state

        # Top transactions (superlative queries)
        if any(c in concepts for c in ["money_in"]) and not group_by:
            state["sql"] = self._top_credits_sql(business_id, start, end)
            return state

        if any(c in concepts for c in ["money_out"]) and not group_by:
            state["sql"] = self._top_debits_sql(business_id, start, end)
            return state

        # Customer ranking
        if group_by == "customer_name":
            state["sql"] = self._top_customers_sql(business_id)
            return state

        # Default: cashflow summary (time series)
        state["sql"] = self._cashflow_summary_sql(business_id, start, end)
        return state

    # ── SQL Templates — all use correct aggregation ───────────────────────────

    def _cashflow_summary_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT
  DATE_TRUNC('day', transaction_date)::date AS cashflow_date,
  COALESCE(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END), 0) AS inflow,
  COALESCE(SUM(CASE WHEN transaction_type = 'debit'  THEN amount ELSE 0 END), 0) AS outflow,
  COALESCE(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE -amount END), 0) AS net_cashflow
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
GROUP BY 1 ORDER BY 1 LIMIT {self.settings.max_result_rows}""".strip()

    def _cashflow_history_sql(self, business_id: int, end: str, limit: int) -> str:
        return f"""
SELECT
  transaction_date AS cashflow_date,
  COALESCE(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END), 0) AS inflow,
  COALESCE(SUM(CASE WHEN transaction_type = 'debit'  THEN amount ELSE 0 END), 0) AS outflow,
  COALESCE(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE -amount END), 0) AS net_cashflow,
  (ARRAY_AGG(balance_after_transaction ORDER BY id DESC))[1] AS closing_balance
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_date <= DATE '{end}'
GROUP BY 1 ORDER BY 1 LIMIT {limit}""".strip()

    def _cashflow_daily_sql(self, business_id: int, start: str, end: str, limit: int) -> str:
        return f"""
SELECT
  transaction_date AS cashflow_date,
  COALESCE(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END), 0) AS inflow,
  COALESCE(SUM(CASE WHEN transaction_type = 'debit'  THEN amount ELSE 0 END), 0) AS outflow,
  COALESCE(SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE -amount END), 0) AS net_cashflow,
  (ARRAY_AGG(balance_after_transaction ORDER BY id DESC))[1] AS closing_balance
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
GROUP BY 1 ORDER BY 1 LIMIT {limit}""".strip()

    def _transactions_sql(self, business_id: int, start: str, end: str, limit: int) -> str:
        return f"""
SELECT id, transaction_date, amount, transaction_type, category,
       merchant_name, payment_mode, balance_after_transaction, description
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
ORDER BY transaction_date DESC, id DESC LIMIT {limit}""".strip()

    def _top_credits_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT transaction_date, amount, category, merchant_name, description
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_type = 'credit'
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
ORDER BY amount DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _top_debits_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT transaction_date, amount, category, merchant_name, description
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_type = 'debit'
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
ORDER BY amount DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _top_categories_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT
  category,
  SUM(CASE WHEN transaction_type = 'debit'  THEN amount ELSE 0 END) AS total_spent,
  SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) AS total_received,
  COUNT(*) AS transaction_count,
  ROUND(100.0 * SUM(CASE WHEN transaction_type='debit' THEN amount ELSE 0 END)
        / NULLIF(SUM(SUM(CASE WHEN transaction_type='debit' THEN amount ELSE 0 END)) OVER (), 0), 1) AS pct_of_spend
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
  AND category IS NOT NULL
GROUP BY category ORDER BY total_spent DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _vendor_spend_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT
  merchant_name AS vendor,
  SUM(amount) AS total_spend,
  COUNT(*) AS txn_count,
  ROUND(100.0 * SUM(amount) / NULLIF(SUM(SUM(amount)) OVER (), 0), 1) AS pct_of_total
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_type = 'debit'
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
  AND merchant_name IS NOT NULL
GROUP BY merchant_name ORDER BY total_spend DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _category_breakdown_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT category, transaction_type,
  SUM(amount) AS total_amount, COUNT(*) AS count
FROM bank_transactions
WHERE business_id = {business_id}
  AND transaction_date BETWEEN DATE '{start}' AND DATE '{end}'
  AND category IS NOT NULL
GROUP BY category, transaction_type ORDER BY total_amount DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _top_customers_sql(self, business_id: int) -> str:
        return f"""
SELECT customer_name,
  COUNT(*) AS invoice_count,
  SUM(invoice_amount) AS total_invoiced,
  SUM(CASE WHEN status = 'paid' THEN invoice_amount ELSE 0 END) AS total_paid,
  SUM(CASE WHEN status != 'paid' THEN invoice_amount ELSE 0 END) AS outstanding,
  AVG(delay_days) AS avg_delay_days
FROM invoice_records
WHERE business_id = {business_id}
GROUP BY customer_name ORDER BY total_invoiced DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _invoice_sql(self, business_id: int) -> str:
        return f"""
SELECT invoice_number, customer_name, invoice_amount, invoice_date,
       due_date, actual_payment_date, status, delay_days
FROM invoice_records
WHERE business_id = {business_id}
ORDER BY due_date DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _vendor_sql(self, business_id: int) -> str:
        return f"""
SELECT vendor_name, payment_amount, due_date, status
FROM vendor_payments
WHERE business_id = {business_id}
ORDER BY due_date LIMIT {self.settings.max_result_rows}""".strip()

    def _loan_sql(self, business_id: int) -> str:
        return f"""
SELECT loan_type, lender_name, emi_amount, due_date, outstanding_amount, interest_rate
FROM loan_obligations
WHERE business_id = {business_id}
ORDER BY due_date LIMIT {self.settings.max_result_rows}""".strip()

    def _risk_sql(self, business_id: int) -> str:
        return f"""
SELECT forecast_date, liquidity_score, default_risk_score,
       overdraft_risk_score, working_capital_score, overall_risk_band
FROM risk_scores
WHERE business_id = {business_id}
ORDER BY forecast_date DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _balance_sql(self, business_id: int) -> str:
        return f"""
SELECT transaction_date, balance_after_transaction AS closing_balance, description
FROM bank_transactions
WHERE business_id = {business_id}
ORDER BY transaction_date DESC, id DESC LIMIT 1""".strip()

    def _expense_sql(self, business_id: int, start: str, end: str) -> str:
        return f"""
SELECT expense_name, expense_category, amount, expense_date, recurring
FROM expenses
WHERE business_id = {business_id}
  AND expense_date BETWEEN DATE '{start}' AND DATE '{end}'
ORDER BY amount DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _recommendations_sql(self, business_id: int) -> str:
        return f"""
SELECT recommended_product, reason, confidence_score
FROM banking_product_recommendations
WHERE business_id = {business_id}
ORDER BY confidence_score DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _salary_sql(self, business_id: int) -> str:
        return f"""
SELECT payroll_date, total_salary_amount, employee_count
FROM salary_schedule
WHERE business_id = {business_id}
ORDER BY payroll_date DESC LIMIT {self.settings.max_result_rows}""".strip()

    def _alerts_sql(self, business_id: int) -> str:
        return f"""
SELECT alert_type, alert_message, severity, is_read, created_at
FROM alerts
WHERE business_id = {business_id}
ORDER BY created_at DESC LIMIT {self.settings.max_result_rows}""".strip()
