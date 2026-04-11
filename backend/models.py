from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ─────────────────────────────────────────────
# Core User + Business Models
# ─────────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'msme_owner', 'relationship_manager', 'admin'
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'phone_number': self.phone_number
        }


class BusinessProfile(db.Model):
    __tablename__ = 'business_profiles'

    id = db.Column(db.Integer, primary_key=True)
    # user_id does not exist in the Neon DB — omitted intentionally
    business_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    gst_number = db.Column(db.String(50))
    annual_revenue = db.Column(db.Numeric(15, 2))
    employee_count = db.Column(db.Integer)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    bank_name = db.Column(db.String(150), nullable=False)
    account_number = db.Column(db.String(100), nullable=False)
    ifsc_code = db.Column(db.String(20))
    account_type = db.Column(db.String(50))
    current_balance = db.Column(db.Numeric(15, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BankTransaction(db.Model):
    __tablename__ = 'bank_transactions'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', ondelete='CASCADE'))
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_type = db.Column(db.String(20))  # 'credit', 'debit'
    category = db.Column(db.String(100))
    merchant_name = db.Column(db.String(200))
    payment_mode = db.Column(db.String(50))
    balance_after_transaction = db.Column(db.Numeric(15, 2))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InvoiceRecord(db.Model):
    __tablename__ = 'invoice_records'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    invoice_number = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(200))
    invoice_amount = db.Column(db.Numeric(15, 2), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    actual_payment_date = db.Column(db.Date)
    status = db.Column(db.String(50))  # 'paid', 'pending', 'overdue'
    delay_days = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    expense_name = db.Column(db.String(200))
    expense_category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2))
    expense_date = db.Column(db.Date)
    recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────
# Obligations & Risk Models (NEW)
# ─────────────────────────────────────────────

class VendorPayment(db.Model):
    __tablename__ = 'vendor_payments'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    vendor_name = db.Column(db.String(200))
    payment_amount = db.Column(db.Numeric(15, 2))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50))  # 'pending', 'paid', 'overdue'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LoanObligation(db.Model):
    __tablename__ = 'loan_obligations'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    loan_type = db.Column(db.String(100))
    lender_name = db.Column(db.String(200))
    emi_amount = db.Column(db.Numeric(15, 2))
    due_date = db.Column(db.Date)
    outstanding_amount = db.Column(db.Numeric(15, 2))
    interest_rate = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RiskScore(db.Model):
    __tablename__ = 'risk_scores'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    forecast_date = db.Column(db.Date)
    liquidity_score = db.Column(db.Integer)
    default_risk_score = db.Column(db.Integer)
    overdraft_risk_score = db.Column(db.Integer)
    working_capital_score = db.Column(db.Integer)
    overall_risk_band = db.Column(db.String(50))  # 'safe', 'moderate', 'high', 'critical'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    alert_type = db.Column(db.String(100))
    alert_message = db.Column(db.Text)
    severity = db.Column(db.String(50))  # 'low', 'medium', 'high', 'critical'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BankingProductRecommendation(db.Model):
    __tablename__ = 'banking_product_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    recommended_product = db.Column(db.String(200))
    reason = db.Column(db.Text)
    confidence_score = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CashflowForecast(db.Model):
    __tablename__ = 'cashflow_forecasts'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    forecast_date = db.Column(db.Date)
    predicted_inflow = db.Column(db.Numeric(15, 2))
    predicted_outflow = db.Column(db.Numeric(15, 2))
    predicted_closing_balance = db.Column(db.Numeric(15, 2))
    liquidity_gap = db.Column(db.Numeric(15, 2))
    overdraft_probability = db.Column(db.Numeric(5, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SalarySchedule(db.Model):
    __tablename__ = 'salary_schedule'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    payroll_date = db.Column(db.Date)
    total_salary_amount = db.Column(db.Numeric(15, 2))
    employee_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QueryHistory(db.Model):
    __tablename__ = 'query_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    user_query = db.Column(db.Text)
    generated_sql = db.Column(db.Text)
    response_summary = db.Column(db.Text)
    result_json = db.Column(db.JSON)
    tags = db.Column(db.ARRAY(db.String))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RelationshipManager(db.Model):
    __tablename__ = 'relationship_managers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    employee_code = db.Column(db.String(50))
    region = db.Column(db.String(100))
    branch_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustomerPortfolio(db.Model):
    __tablename__ = 'customer_portfolios'

    id = db.Column(db.Integer, primary_key=True)
    relationship_manager_id = db.Column(db.Integer, db.ForeignKey('relationship_managers.id', ondelete='CASCADE'))
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    assigned_date = db.Column(db.Date)
    portfolio_status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
