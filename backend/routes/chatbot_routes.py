import os
import json
from flask import Blueprint, request, jsonify
from groq import Groq
from schema.db_schema import SCHEMA
from services.auth_service import token_required
from models import db, BusinessProfile, BusinessUser
from sqlalchemy import text

chatbot_bp = Blueprint('chatbot', __name__)

# Initialize Groq client
# Ensure GROQ_API_KEY is set in your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_table_descriptions():
    descriptions = []
    for table_name, details in SCHEMA.items():
        descriptions.append(f"- {table_name}: {details['description']}")
    return "\n".join(descriptions)

def format_filtered_schema(tables):
    filtered_info = []
    for table_name in tables:
        if table_name in SCHEMA:
            details = SCHEMA[table_name]
            cols = ", ".join([f"{col}: {desc}" for col, desc in details['columns'].items()])
            filtered_info.append(f"Table: {table_name}\nDescription: {details['description']}\nColumns: {cols}")
    return "\n\n".join(filtered_info)

def is_safe_sql(sql):
    sql_lower = sql.lower()
    forbidden = [
        "insert", "update", "delete",
        "drop", "alter", "truncate",
        "create", "grant", "revoke"
    ]

    if any(word in sql_lower for word in forbidden):
        return False, "Dangerous keyword detected"

    if ";" in sql[:-1]:  # multiple statements
        return False, "Multiple queries not allowed"

    if "select" not in sql_lower:
        return False, "Only SELECT allowed"

    if "business_id" not in sql_lower:
        return False, "Missing business_id filter"

    if "limit" not in sql_lower:
        return False, "LIMIT required"

    return True, None

@chatbot_bp.route('/select-tables', methods=['POST'])
@token_required
def select_tables(current_user):
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query in request body"}), 400

    user_query = data['query']
    table_descriptions = get_table_descriptions()

    prompt = f"""You are an expert financial data analyst.

Your task is to identify the MOST RELEVANT database tables needed to answer the user's question.

-----------------------
USER QUESTION:
{user_query}
-----------------------

AVAILABLE TABLES:

{table_descriptions}

-----------------------

RULES:

1. Only select tables that are NECESSARY to answer the question.
2. Prefer MINIMUM tables (1–3 tables).
3. Use business logic:
   - Revenue / cash flow → bank_transactions
   - Payments / delays → invoice_records
   - Expenses → expenses
   - Loans / EMI → loan_obligations
   - Forecast / future → cashflow_forecasts
   - Risk → risk_scores
   - Vendor payments → vendor_payments
   - Salaries → salary_schedule

4. Do NOT include irrelevant tables.
5. Always assume queries are for ONE business (business_id filtering handled separately).

-----------------------

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "tables": ["table1", "table2"]
}}

-----------------------

Return ONLY JSON. No explanation."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content
        return jsonify(json.loads(response_content))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/generate-sql', methods=['POST'])
@token_required
def generate_sql(current_user):
    data = request.get_json()
    if not data or 'query' not in data or 'tables' not in data:
        return jsonify({"error": "Missing query or tables in request body"}), 400

    user_query = data['query']
    requested_tables = data['tables']

    # Fetch business_id for the current user from mapping table
    mapping = BusinessUser.query.filter_by(user_id=current_user['user_id']).first()
    if not mapping:
        return jsonify({"error": "No business profile mapped for this user"}), 404
    
    business_id = mapping.business_id
    filtered_schema = format_filtered_schema(requested_tables)

    prompt = f"""You are an expert PostgreSQL SQL generator for a financial analytics system.

Your job is to convert a natural language question into a VALID SQL (Postgres NEON DB) query.

-----------------------------------
USER QUESTION:
{user_query}
-----------------------------------

AVAILABLE TABLES AND SCHEMA:

{filtered_schema}

-----------------------------------

IMPORTANT RULES:

1. ONLY use the tables and columns provided above.
2. NEVER use columns or tables not listed.
3. ALWAYS filter by:
   business_id = {business_id}

4. If multiple tables are used:
   - JOIN using business_id

5. Use correct logic:
   - credit = inflow
   - debit = outflow
   - revenue = SUM(amount WHERE transaction_type = 'credit')
   - expenses = SUM(amount WHERE transaction_type = 'debit')

6. For "why" or analysis questions:
   - Use aggregation
   - Compare categories, time periods, or patterns

7. Use:
   - GROUP BY when needed
   - ORDER BY for meaningful output
   - LIMIT 100 for non-aggregated queries

8. For time-based queries:
   - Use transaction_date, invoice_date, etc.

9. DO NOT:
   - use DELETE, UPDATE, INSERT
   - use SELECT *
   - hallucinate columns

-----------------------------------

OUTPUT FORMAT (STRICT JSON):

{{
  "sql": "your_sql_query_here"
}}

-----------------------------------

EXAMPLES:

Q: total revenue last month
A:
{{
  "sql": "SELECT SUM(amount) FROM bank_transactions WHERE transaction_type = 'credit' AND business_id = {business_id} AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')"
}}

Q: delayed invoices
A:
{{
  "sql": "SELECT COUNT(*) FROM invoice_records WHERE status = 'overdue' AND business_id = {business_id}"
}}

Q: total expenses
A:
{{
  "sql": "SELECT SUM(amount) FROM bank_transactions WHERE transaction_type = 'debit' AND business_id = {business_id}"
}}

-----------------------------------

Return ONLY JSON. No explanation."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content
        return jsonify(json.loads(response_content))

    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@chatbot_bp.route('/execute-sql', methods=['POST'])
@token_required
def execute_sql(current_user):
    data = request.get_json()
    if not data or 'sql' not in data:
        return jsonify({"error": "Missing sql in request body"}), 400

    sql_query = data['sql']

    # Safety Validation
    is_safe, error_msg = is_safe_sql(sql_query)
    if not is_safe:
        return jsonify({"error": error_msg}), 400

    try:
        result = db.session.execute(text(sql_query))
        
        # Convert rows to dicts and handle non-serializable types
        rows = []
        for row in result.mappings():
            row_dict = {}
            for key, value in row.items():
                # Handle Decimal, Date, etc.
                if hasattr(value, 'isoformat'): # Date, DateTime
                    row_dict[key] = value.isoformat()
                elif isinstance(value, (int, float, str, bool, type(None))):
                    row_dict[key] = value
                else:
                    row_dict[key] = str(value)
            rows.append(row_dict)

        return jsonify({
            "rows": rows,
            "row_count": len(rows)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
