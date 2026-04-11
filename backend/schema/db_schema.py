SCHEMA = {
    "business_profiles": {
        "description": "MSME business details",
        "primary_key": "id",
        "columns": {
            "id": "unique business id",
            "business_name": "name of business",
            "industry": "industry type",
            "annual_revenue": "yearly revenue",
            "employee_count": "number of employees",
            "city": "business city",
            "state": "business state"
        }
    },

    "bank_transactions": {
        "description": "All money inflow and outflow transactions",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "transaction_date": "date of transaction",
            "amount": "transaction amount",
            "transaction_type": "credit or debit",
            "category": "transaction category",
            "merchant_name": "merchant involved",
            "payment_mode": "payment type",
            "balance_after_transaction": "balance after transaction"
        }
    },

    "invoice_records": {
        "description": "Customer invoices and payment status",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "invoice_amount": "invoice value",
            "invoice_date": "invoice date",
            "due_date": "payment due date",
            "actual_payment_date": "payment date",
            "status": "paid, pending, overdue",
            "delay_days": "delay in days"
        }
    },

    "expenses": {
        "description": "Business expenses",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "expense_name": "expense name",
            "expense_category": "expense category",
            "amount": "expense amount",
            "expense_date": "date",
            "recurring": "recurring or not"
        }
    },

    "loan_obligations": {
        "description": "Loan and EMI obligations",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "loan_type": "loan type",
            "emi_amount": "monthly EMI",
            "due_date": "due date",
            "outstanding_amount": "remaining amount",
            "interest_rate": "interest percentage"
        }
    },

    "cashflow_forecasts": {
        "description": "Future predicted cash flow",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "forecast_date": "future date",
            "predicted_inflow": "expected inflow",
            "predicted_outflow": "expected outflow",
            "predicted_closing_balance": "closing balance",
            "liquidity_gap": "shortfall",
            "overdraft_probability": "chance of overdraft"
        }
    },

    "risk_scores": {
        "description": "Financial risk scores",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "liquidity_score": "cash health",
            "default_risk_score": "default probability",
            "overdraft_risk_score": "overdraft probability",
            "working_capital_score": "capital strength",
            "overall_risk_band": "safe/moderate/high/critical"
        }
    },

    "vendor_payments": {
        "description": "Payments made to vendors",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "vendor_name": "vendor name",
            "payment_amount": "amount paid",
            "due_date": "payment due",
            "status": "paid/pending/overdue"
        }
    },

    "salary_schedule": {
        "description": "Monthly payroll",
        "primary_key": "id",
        "join_key": "business_id",
        "columns": {
            "business_id": "business reference id",
            "payroll_date": "salary date",
            "total_salary_amount": "total salary",
            "employee_count": "employees paid"
        }
    }
}