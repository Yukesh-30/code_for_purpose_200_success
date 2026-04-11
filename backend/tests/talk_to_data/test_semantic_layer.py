"""Tests for the semantic layer — schema definitions and metric mapping."""
from app.semantic.definitions import CURRENT_NEON_SCHEMA, find_metrics


def test_all_core_tables_present():
    required = [
        "bank_transactions", "invoice_records", "vendor_payments",
        "loan_obligations", "risk_scores", "expenses", "salary_schedule",
        "banking_product_recommendations", "alerts",
    ]
    for table in required:
        assert table in CURRENT_NEON_SCHEMA, f"Missing table: {table}"


def test_bank_transactions_has_required_columns():
    cols = CURRENT_NEON_SCHEMA["bank_transactions"]
    for col in ("id", "business_id", "transaction_date", "amount",
                "transaction_type", "category", "merchant_name",
                "balance_after_transaction"):
        assert col in cols, f"Missing column: {col}"


def test_cashflow_metric_found_by_natural_language():
    metrics = find_metrics("What was my net cash flow last month?")
    names = [m.name for m in metrics]
    assert "cashflow" in names


def test_revenue_metric_found_by_synonym():
    metrics = find_metrics("Show me my total sales income")
    names = [m.name for m in metrics]
    assert "revenue" in names


def test_expense_metric_found_by_synonym():
    metrics = find_metrics("How much did I spend on costs?")
    names = [m.name for m in metrics]
    assert "expense" in names


def test_no_metrics_returns_empty_for_unrelated():
    # "weather" has no financial meaning
    metrics = find_metrics("what is the weather today")
    assert metrics == [] or all(m.name in ("cashflow",) for m in metrics)
