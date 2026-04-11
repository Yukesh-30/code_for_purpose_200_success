import os
import json
from flask import Blueprint, request, jsonify
from groq import Groq
from schema.db_schema import SCHEMA
from services.auth_service import token_required
from models import db, BusinessProfile, BusinessUser, QueryHistory
from sqlalchemy import text
import json

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

def resolve_query_context(current_query, chat_history_list):
    # Format chat history for the prompt
    formatted_history = []
    for msg in chat_history_list:
        role = msg.get('role', 'unknown').upper()
        text = msg.get('text', '')
        formatted_history.append(f"{role}: {text}")
    
    chat_history_str = "\n".join(formatted_history) if formatted_history else "No previous conversation."

    prompt = f"""You are an intelligent query understanding system for a financial analytics platform.

Your job is to:
1. Understand the current user query
2. Use the previous conversation context (last messages)
3. Resolve ambiguity
4. Extract structured entities
5. Rewrite a clear, complete refined query

-----------------------------------
CURRENT USER QUERY:
{current_query}

-----------------------------------
CONVERSATION HISTORY (last messages):
{chat_history_str}

-----------------------------------

TASKS:

1. REFINE QUERY:
- Expand vague queries into complete, explicit analytical queries
- Resolve pronouns like "this", "that", "it"
- Add missing context (time, metrics, comparisons if implied)

2. EXTRACT ENTITIES:
Identify and extract:

- time_range (e.g., "March", "last quarter", "2024")
- metrics (e.g., revenue, expenses, profit, cashflow)
- dimensions (e.g., category, department)
- intent:
    - "comparison"
    - "trend"
    - "aggregation"
    - "anomaly"
    - "reason" (for "why" questions)

3. HANDLE "WHY" QUESTIONS:
If query asks "why":
- Convert into analytical query comparing factors
- Example:
  "Why is my cashflow low?"
  →
  "Analyze revenue vs expenses and category-wise breakdown to identify reasons for low cashflow"

-----------------------------------

OUTPUT FORMAT (STRICT JSON):

{{
  "refined_query": "clear, complete analytical query",
  "entities": {{
    "time_range": "...",
    "metrics": ["..."],
    "dimensions": ["..."],
    "intent": "..."
  }}
}}

-----------------------------------

RULES:
- DO NOT return explanation
- DO NOT hallucinate unavailable metrics
- Keep refined_query concise but complete
- Always infer intent if possible

Return ONLY JSON.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

@chatbot_bp.route('/context-resolver', methods=['POST'])
@token_required
def context_resolver(current_user):
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query in request body"}), 400

    try:
        result = resolve_query_context(data['query'], data.get('chat_history', []))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def select_relevant_tables(user_query):
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

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

@chatbot_bp.route('/select-tables', methods=['POST'])
@token_required
def select_tables(current_user):
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query in request body"}), 400

    try:
        result = select_relevant_tables(data['query'])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_sql_query(user_query, requested_tables, business_id):
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

10. Give the SQL query with LIMIT. Use a maximum value of 100.
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

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

@chatbot_bp.route('/generate-sql', methods=['POST'])
@token_required
def generate_sql(current_user):
    data = request.get_json()
    if not data or 'query' not in data or 'tables' not in data:
        return jsonify({"error": "Missing query or tables in request body"}), 400

    # Fetch business_id for the current user from mapping table
    mapping = BusinessUser.query.filter_by(user_id=current_user['user_id']).first()
    if not mapping:
        return jsonify({"error": "No business profile mapped for this user"}), 404
    
    try:
        result = generate_sql_query(data['query'], data['tables'], mapping.business_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def execute_raw_sql(sql_query):
    # Safety Validation
    is_safe, error_msg = is_safe_sql(sql_query)
    if not is_safe:
        raise ValueError(error_msg)

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
    return rows

@chatbot_bp.route('/execute-sql', methods=['POST'])
@token_required
def execute_sql(current_user):
    data = request.get_json()
    if not data or 'sql' not in data:
        return jsonify({"error": "Missing sql in request body"}), 400

    try:
        rows = execute_raw_sql(data['sql'])
        return jsonify({
            "rows": rows,
            "row_count": len(rows)
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_business_insight(user_query, sql_query, result_data, user_id, business_id):
    prompt = f"""You are a financial analytics insight generator.

Your job is to analyze structured query results and generate meaningful business insights.

-----------------------------------
USER QUERY:
{user_query}

-----------------------------------
SQL USED:
{sql_query}

-----------------------------------
DATA (QUERY RESULT):
{json.dumps(result_data)}

-----------------------------------

TASKS:

1. UNDERSTAND INTENT:
- Identify what the user is trying to understand
- Especially handle "why" questions → find causes, trends, anomalies

2. ANALYZE DATA:
- Look for:
  - trends (increase/decrease over time)
  - comparisons (revenue vs expenses)
  - anomalies (sudden spikes/drops)
  - patterns (consistent decline, seasonal effects)

3. GENERATE SUMMARY:
- Write a clear, concise explanation
- Focus on **business meaning**, not raw numbers
- If "why" → explain possible reasons based ONLY on data

4. GENERATE TAGS:
- Extract key topics (e.g., "revenue", "expenses", "cashflow", "decline")

5. SUGGEST CHART TYPE:
Choose the best visualization:
- "line" → trends over time
- "bar" → category comparisons
- "pie" → proportions
- "table" → raw listing
- "area" → cumulative trends

6. CONFIDENCE SCORE:
- 0 to 1
- High (0.8–1.0): clear pattern
- Medium (0.5–0.8): some signal
- Low (<0.5): unclear or insufficient data

-----------------------------------

STRICT RULES:

- DO NOT hallucinate data not present
- DO NOT invent causes without evidence
- If data is insufficient, say so in summary
- Keep summary under 2–3 sentences
- Be precise and business-focused

-----------------------------------

OUTPUT FORMAT (STRICT JSON):

{{
  "summary": "clear business insight",
  "tags": ["tag1", "tag2"],
  "chart_type": "line/bar/pie/table/area",
  "confidence": 0.0
}}

-----------------------------------

Return ONLY JSON. No explanation.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    insight_content = json.loads(completion.choices[0].message.content)
    
    # Save to History
    new_history = QueryHistory(
        user_id=user_id,
        business_id=business_id,
        user_query=json.dumps(user_query),
        generated_sql=sql_query,
        response_summary=insight_content.get('summary'),
        result_json=result_data,
        tags=insight_content.get('tags', [])
    )
    db.session.add(new_history)
    db.session.commit()
    
    return insight_content

@chatbot_bp.route('/generate-insight', methods=['POST'])
@token_required
def generate_insight(current_user):
    data = request.get_json()
    if not data or 'query' not in data or 'sql' not in data or 'data' not in data:
        return jsonify({"error": "Missing query, sql, or data in request body"}), 400

    # Resolve business_id
    mapping = BusinessUser.query.filter_by(user_id=current_user['user_id']).first()
    if not mapping:
        return jsonify({"error": "No business profile mapped for this user"}), 404

    try:
        result = generate_business_insight(data['query'], data['sql'], data['data'], current_user['user_id'], mapping.business_id)
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
