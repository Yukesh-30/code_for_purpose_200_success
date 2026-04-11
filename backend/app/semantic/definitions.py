from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__NEON_TABLES = {
    "users": {"id", "full_name", "email", "password_hash", "role", "phone_number", "created_at", "updated_at"},
    "business_profiles": {"id", "user_id", "business_name", "business_type", "industry", "gst_number", "annual_revenue", "employee_count", "city", "state", "created_at", "updated_at"},
    "bank_accounts": {"id", "business_id", "bank_name", "account_number", "ifsc_code", "account_type", "current_balance", "created_at"},
    "bank_transactions": {"id", "business_id", "bank_account_id", "transaction_date", "amount", "transaction_type", "category", "merchant_name", "payment_mode", "balance_after_transaction", "description", "created_at"},
    "cashflow_forecasts": {"id", "business_id", "forecast_date", "predicted_inflow", "predicted_outflow", "predicted_closing_balance", "liquidity_gap", "overdraft_probability", "created_at"},
    "invoice_records": {"id", "business_id", "invoice_number", "customer_name", "invoice_amount", "invoice_date", "due_date", "actual_payment_date", "status", "delay_days", "created_at"},
    "invoice_delay_predictions": {"id", "invoice_id", "predicted_delay_days", "delay_probability", "predicted_impact_amount", "created_at"},
    "expenses": {"id", "business_id", "expense_name", "expense_category", "amount", "expense_date", "recurring", "created_at"},
    "salary_schedule": {"id", "business_id", "payroll_date", "total_salary_amount", "employee_count", "created_at"},
    "vendor_payments": {"id", "business_id", "vendor_name", "payment_amount", "due_date", "status", "created_at"},
    "loan_obligations": {"id", "business_id", "loan_type", "lender_name", "emi_amount", "due_date", "outstanding_amount", "interest_rate", "created_at"},
    "risk_scores": {"id", "business_id", "forecast_date", "liquidity_score", "default_risk_score", "overdraft_risk_score", "working_capital_score", "overall_risk_band", "created_at"},
    "banking_product_recommendations": {"id", "business_id", "recommended_product", "reason", "confidence_score", "created_at"},
    "alerts": {"id", "business_id", "alert_type", "alert_message", "severity", "is_read", "created_at"},
    "query_history": {"id", "user_id", "business_id", "user_query", "generated_sql", "response_summary", "result_json", "tags", "created_at"},
    "chat_sessions": {"id", "user_id", "session_name", "created_at"},
    "chat_messages": {"id", "session_id", "sender_type", "message_text", "created_at"},
    "relationship_managers": {"id", "user_id", "employee_code", "region", "branch_name", "created_at"},
    "customer_portfolios": {"id", "relationship_manager_id", "business_id", "assigned_date", "portfolio_status", "created_at"},
    "daily_cashflow_features": {"business_id", "cashflow_date", "inflow", "outflow", "net_cashflow"},
}

# These are legacy canonical names — kept for backward compatibility with retriever
CANONICAL_SCHEMA: dict[str, set[str]] = {}

# The real live schema — used by SQL validator
CURRENT_NEON_SCHEMA: dict[str, set[str]] = __NEON_TABLES


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    description: str
    expression: str
    canonical_table: str
    current_table: str | None = None
    synonyms: tuple[str, ...] = ()


METRICS: dict[str, MetricDefinition] = {
    "revenue": MetricDefinition(
        name="revenue",
        description="Money credited into the business account.",
        expression="SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END)",
        canonical_table="bank_transactions",
        current_table="bank_transactions",
        synonyms=("sales", "income", "inflow", "collections", "receipts", "credits"),
    ),
    "expense": MetricDefinition(
        name="expense",
        description="Money debited from the business account.",
        expression="SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END)",
        canonical_table="bank_transactions",
        current_table="bank_transactions",
        synonyms=("cost", "spend", "outflow", "payments", "debits"),
    ),
    "cashflow": MetricDefinition(
        name="cashflow",
        description="Net movement of cash: inflow minus outflow.",
        expression="SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE -amount END)",
        canonical_table="bank_transactions",
        current_table="bank_transactions",
        synonyms=("net cashflow", "cash flow", "net flow", "liquidity movement"),
    ),
    "profit": MetricDefinition(
        name="profit",
        description="Revenue minus expenses (operating proxy from bank data).",
        expression="SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE -amount END)",
        canonical_table="bank_transactions",
        current_table="bank_transactions",
        synonyms=("net profit", "margin", "surplus"),
    ),
    "closing_balance": MetricDefinition(
        name="closing_balance",
        description="Latest known balance after the latest bank transaction by transaction date and id.",
        expression="balance_after_transaction from the latest ordered transaction",
        canonical_table="bank_transactions",
        current_table="bank_transactions",
        synonyms=("balance", "cash balance", "ending balance", "current balance"),
    ),
    "overdue_invoices": MetricDefinition(
        name="overdue_invoices",
        description="Invoices past their due date.",
        expression="COUNT(*) FILTER (WHERE status = 'overdue')",
        canonical_table="invoice_records",
        current_table="invoice_records",
        synonyms=("late invoices", "unpaid invoices", "outstanding invoices"),
    ),
    "loan_emi": MetricDefinition(
        name="loan_emi",
        description="Monthly EMI payment obligations across all loans.",
        expression="SUM(emi_amount)",
        canonical_table="loan_obligations",
        current_table="loan_obligations",
        synonyms=("emi", "loan payment", "loan instalment"),
    ),
    "vendor_dues": MetricDefinition(
        name="vendor_dues",
        description="Pending vendor payments.",
        expression="SUM(payment_amount) FILTER (WHERE status = 'pending')",
        canonical_table="vendor_payments",
        current_table="vendor_payments",
        synonyms=("payables", "vendor payment", "supplier dues"),
    ),
}


def find_metrics(question: str) -> list[MetricDefinition]:
    normalized = question.lower()
    matches: list[MetricDefinition] = []
    seen: set[str] = set()
    for metric in METRICS.values():
        terms = (metric.name, *metric.synonyms)
        if any(term in normalized for term in terms) and metric.name not in seen:
            matches.append(metric)
            seen.add(metric.name)
    return matches
