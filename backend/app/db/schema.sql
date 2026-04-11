CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS business (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    gst_number VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    bank_name VARCHAR(150) NOT NULL,
    account_number VARCHAR(100) NOT NULL,
    account_type VARCHAR(50),
    current_balance NUMERIC(18, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    txn_date DATE NOT NULL,
    debit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    credit_amount NUMERIC(18, 2) NOT NULL DEFAULT 0,
    narration TEXT,
    balance_after_txn NUMERIC(18, 2),
    category VARCHAR(100),
    counterparty VARCHAR(200),
    payment_mode VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (debit_amount >= 0),
    CHECK (credit_amount >= 0),
    CHECK (debit_amount = 0 OR credit_amount = 0)
);

CREATE INDEX IF NOT EXISTS idx_transactions_business_date ON transactions (business_id, txn_date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_narration_trgm ON transactions USING gin (narration gin_trgm_ops);

CREATE TABLE IF NOT EXISTS invoices (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    invoice_number VARCHAR(100) NOT NULL,
    customer_name VARCHAR(200),
    amount NUMERIC(18, 2) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('paid', 'pending', 'overdue', 'cancelled')),
    delay_days INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vendor_payments (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    vendor_name VARCHAR(200) NOT NULL,
    amount NUMERIC(18, 2),
    payment_amount NUMERIC(18, 2),
    due_date DATE NOT NULL,
    paid_date DATE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('paid', 'pending', 'overdue')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payroll (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    payroll_date DATE NOT NULL,
    total_amount NUMERIC(18, 2) NOT NULL,
    employee_count INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS loans (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    loan_type VARCHAR(100),
    lender_name VARCHAR(150),
    principal_amount NUMERIC(18, 2),
    outstanding_amount NUMERIC(18, 2),
    interest_rate NUMERIC(7, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS loan_emi (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    loan_id BIGINT NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
    emi_date DATE NOT NULL,
    emi_amount NUMERIC(18, 2) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('paid', 'pending', 'overdue')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS txn_classification (
    id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    confidence NUMERIC(5, 4) NOT NULL,
    rule_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cashflow_daily (
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    cashflow_date DATE NOT NULL,
    inflow NUMERIC(18, 2) NOT NULL DEFAULT 0,
    outflow NUMERIC(18, 2) NOT NULL DEFAULT 0,
    net_cashflow NUMERIC(18, 2) NOT NULL DEFAULT 0,
    closing_balance NUMERIC(18, 2),
    PRIMARY KEY (business_id, cashflow_date)
);

CREATE TABLE IF NOT EXISTS forecast (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_inflow NUMERIC(18, 2),
    predicted_outflow NUMERIC(18, 2),
    predicted_closing_balance NUMERIC(18, 2),
    liquidity_gap NUMERIC(18, 2),
    overdraft_probability NUMERIC(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES business(id) ON DELETE CASCADE,
    score_date DATE,
    forecast_date DATE,
    liquidity_score INT CHECK (liquidity_score BETWEEN 0 AND 100),
    default_risk_score INT CHECK (default_risk_score BETWEEN 0 AND 100),
    overdraft_risk_score INT CHECK (overdraft_risk_score BETWEEN 0 AND 100),
    working_capital_score INT CHECK (working_capital_score BETWEEN 0 AND 100),
    overall_risk_band VARCHAR(50) CHECK (overall_risk_band IN ('safe', 'moderate', 'high', 'critical')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
