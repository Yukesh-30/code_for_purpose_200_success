# Talk to Data Financial Intelligence Design

## Goal

Build a production-grade MSME cashflow intelligence service that lets users ask natural-language questions about financial data, receive database-grounded answers, understand drivers, forecast future cashflow, and detect anomalies without hallucinated facts.

## Architecture

```text
Frontend Chat UI
  -> Existing Flask Intelligence API
     POST /chat
     POST /forecast
     POST /anomaly
        -> LangGraph Orchestrator
           -> Intent Agent
           -> Semantic Agent + Vector Store
           -> SQL Agent
           -> Deterministic SQL Validator
           -> Read-only Postgres Execution Layer
           -> Analysis Agent
           -> Forecast Agent
           -> Anomaly Agent
           -> Explanation Agent
        -> Response Builder
           answer, explanation, SQL, supporting data, chart-ready data

PostgreSQL
  Canonical: business, accounts, transactions, invoices, vendor_payments,
  payroll, loans, loan_emi, txn_classification, cashflow_daily, forecast,
  risk_scores

Current Neon tables
  users, business_profiles, bank_accounts, bank_transactions,
  cashflow_forecasts, invoice_records, invoice_delay_predictions, expenses,
  salary_schedule, vendor_payments, loan_obligations, risk_scores,
  banking_product_recommendations, alerts, query_history, chat_sessions,
  chat_messages, relationship_managers, customer_portfolios

Semantic Store
  ChromaDB when configured, deterministic local retrieval as fallback
  Stores metric definitions, column meanings, and query examples
```

The existing Flask app remains the single web server for auth/business/upload flows and the Talk-to-Data intelligence surface. The `backend/app` package contains reusable intelligence engine modules, not a separate web server.

## Data Model

The target banking-style schema uses canonical tables requested by the product spec. The semantic layer also knows the current Neon table names, such as `business_profiles`, `bank_transactions`, `cashflow_forecasts`, `salary_schedule`, and `loan_obligations`, so current data can be queried before a canonical migration.

Core metric definitions:

- `revenue`: credits into the business account
- `expense`: debits from the business account
- `cashflow`: inflow minus outflow
- `profit`: revenue minus expense
- `closing_balance`: latest transaction balance after transaction

## Agent Responsibilities

- Intent Agent: classifies question type and requests clarification for ambiguity.
- Semantic Agent: maps business terms to metrics, tables, columns, and retrieved semantic examples.
- SQL Agent: generates read-only SQL from trusted semantic mappings.
- SQL Validator: blocks non-read operations, validates tables/columns, enforces row limits, and rejects unsafe SQL.
- Execution Layer: runs validated SQL in a read-only transaction.
- Analysis Agent: identifies drivers, deltas, trends, and insufficient-data cases.
- Forecast Agent: produces deterministic rolling-average forecasts and explanation-ready data.
- Anomaly Agent: detects unusual inflows/outflows using statistical rules.
- Explanation Agent: produces business-friendly responses grounded only in returned data and SQL.

## Model Routing

Default model map:

- Intent Agent: `openai/gpt-oss-20b`
- Semantic Agent: `meta-llama/llama-4-scout-17b-16e-instruct`
- SQL Agent: `openai/gpt-oss-120b`
- SQL Validator: deterministic validator first, `openai/gpt-oss-20b` only for optional critique
- Analysis Agent: `qwen/qwen3-32b`
- Explanation Agent: `llama-3.3-70b-versatile`
- Forecast Agent: deterministic forecast first, `openai/gpt-oss-20b` only for optional narrative
- Anomaly Agent: deterministic anomaly detection first, `qwen/qwen3-32b` only for optional narrative

LLM use is optional and routed through an OpenAI-compatible endpoint, such as Groq. Safety-critical behavior is deterministic and schema-validated.

## Edge Cases

- Ambiguous query: return `needs_clarification` with a concrete question.
- Missing data: return `insufficient_data`.
- SQL hallucination: reject SQL with unknown tables/columns or non-read statements.
- Large result: enforce a configured maximum row limit and summarize.
- Time context: normalize terms like `last month` and `previous quarter` using a timezone-aware clock.
- Derived metrics: calculate cashflow and profit with trusted formulas.
- Follow-up query: use conversation memory from previous query metadata.
- Unsafe query: block all write/DDL/admin statements.

## Testing

Focused tests cover time parsing, semantic metric mapping, SQL validation, and response behavior for insufficient data and unsafe queries.
