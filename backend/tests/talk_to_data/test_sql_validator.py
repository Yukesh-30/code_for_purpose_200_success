"""Tests for the SQL validator — safety and schema enforcement."""
from app.agents.sql_validator import SQLValidator


def test_blocks_delete():
    v = SQLValidator()
    r = v.validate("DELETE FROM bank_transactions WHERE business_id = 1", business_id=1)
    assert r.ok is False
    assert "read-only" in r.error.lower()


def test_blocks_drop_table():
    v = SQLValidator()
    r = v.validate("DROP TABLE bank_transactions", business_id=1)
    assert r.ok is False


def test_blocks_cross_business_query():
    v = SQLValidator()
    r = v.validate(
        "SELECT * FROM bank_transactions WHERE business_id = 2 LIMIT 10",
        business_id=1,
    )
    assert r.ok is False
    assert "business_id" in r.error.lower()


def test_allows_valid_cashflow_query():
    v = SQLValidator()
    sql = """
SELECT transaction_date, amount, transaction_type
FROM bank_transactions
WHERE business_id = 1
LIMIT 10
"""
    r = v.validate(sql, business_id=1)
    assert r.ok is True
    assert "bank_transactions" in r.sql


def test_allows_valid_invoice_query():
    v = SQLValidator()
    sql = """
SELECT invoice_number, customer_name, invoice_amount, status
FROM invoice_records
WHERE business_id = 1
ORDER BY due_date DESC
LIMIT 50
"""
    r = v.validate(sql, business_id=1)
    assert r.ok is True


def test_enforces_limit_cap():
    v = SQLValidator()
    sql = """
SELECT * FROM bank_transactions
WHERE business_id = 1
LIMIT 99999
"""
    r = v.validate(sql, business_id=1)
    assert r.ok is True
    assert "LIMIT 500" in r.sql or "LIMIT 99999" not in r.sql


def test_blocks_unknown_table():
    v = SQLValidator()
    sql = """
SELECT * FROM secret_table
WHERE business_id = 1
LIMIT 10
"""
    r = v.validate(sql, business_id=1)
    assert r.ok is False
