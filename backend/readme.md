# FlowSight Talk-to-Data Financial Intelligence

This backend now exposes the Talk-to-Data intelligence system from the existing Flask server.

## Architecture

```text
Frontend Chat UI
  -> Existing Flask app in main.py
     POST /chat
     POST /forecast
     POST /anomaly
        -> Intent Agent
        -> Semantic Agent + Chroma/in-memory semantic retrieval
        -> SQL Agent
        -> LangChain tool adapters for semantic search and SQL validation
        -> SQL Validator
        -> Read-only PostgreSQL Executor
        -> Analysis / Forecast / Anomaly Agent
        -> Explanation Agent
        -> answer + explanation + SQL + supporting rows + chart-ready data

PostgreSQL/Neon
  Current tables: users, business_profiles, bank_accounts, bank_transactions,
  cashflow_forecasts, invoice_records, invoice_delay_predictions, expenses,
  salary_schedule, vendor_payments, loan_obligations, risk_scores,
  banking_product_recommendations, alerts, query_history, chat_sessions,
  chat_messages, relationship_managers, customer_portfolios

Target canonical schema:
  backend/app/db/schema.sql
```

## Run

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Example API Flow

Request:

```http
POST /chat
Content-Type: application/json

{
  "business_id": 1,
  "user_id": 1,
  "question": "Why did my cashflow change last month?",
  "include_sql": true
}
```

Response shape:

```json
{
  "status": "success",
  "answer": "Cashflow for the selected period is 125000.0 with inflow 300000.0 and outflow 175000.0.",
  "explanation": "I calculated cashflow as total credits minus total debits from scoped bank transactions. The supporting data is grouped daily so it can be charted or audited.",
  "sql": "SELECT ... FROM bank_transactions WHERE business_id = 1 ...",
  "supporting_data": {
    "columns": ["cashflow_date", "inflow", "outflow", "net_cashflow"],
    "rows": [],
    "row_count": 0,
    "truncated": false
  },
  "chart": {
    "type": "line",
    "x": "cashflow_date",
    "y": ["inflow", "outflow", "net_cashflow"],
    "series": []
  },
  "confidence": 0.82,
  "warnings": [],
  "follow_up_questions": []
}
```

Forecast:

```http
POST /forecast
Content-Type: application/json

{
  "business_id": 1,
  "horizon_days": 30,
  "include_sql": true
}
```

Anomaly detection:

```http
POST /anomaly
Content-Type: application/json

{
  "business_id": 1,
  "lookback_days": 90,
  "include_sql": true
}
```

## Trust Controls

- All generated SQL is read-only.
- SQL must be scoped to `business_id`.
- Unknown tables are rejected against both canonical and current Neon schemas.
- Large results are limited by `MAX_RESULT_ROWS`.
- Missing data returns `insufficient_data`.
- Unsafe requests return `blocked`.
- The response includes supporting rows and SQL when `include_sql` is true.
