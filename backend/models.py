from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'msme_owner', 'relationship_manager', 'admin'
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "phone_number": self.phone_number
        }

class BusinessProfile(db.Model):
    __tablename__ = 'business_profiles'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    gst_number = db.Column(db.String(50))
    annual_revenue = db.Column(db.Numeric(15,2))
    employee_count = db.Column(db.Integer)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BusinessUser(db.Model):
    __tablename__ = 'business_users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    role = db.Column(db.String(50))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'business_id', name='_user_business_uc'),)

class QueryHistory(db.Model):
    __tablename__ = 'query_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    user_query = db.Column(db.Text)
    generated_sql = db.Column(db.Text)
    response_summary = db.Column(db.Text)
    result_json = db.Column(db.JSON)
    tags = db.Column(db.ARRAY(db.String))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    session_name = db.Column(db.String(200))

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id', ondelete='CASCADE'))
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    sender_type = db.Column(db.String(50)) # 'user', 'ai'
    message_text = db.Column(db.Text)

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    bank_name = db.Column(db.String(150), nullable=False)
    account_number = db.Column(db.String(100), nullable=False)
    ifsc_code = db.Column(db.String(20))
    account_type = db.Column(db.String(50))
    current_balance = db.Column(db.Numeric(15,2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BankTransaction(db.Model):
    __tablename__ = 'bank_transactions'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id', ondelete='CASCADE'))
    transaction_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(15,2), nullable=False)
    transaction_type = db.Column(db.String(20)) # 'credit', 'debit'
    category = db.Column(db.String(100))
    merchant_name = db.Column(db.String(200))
    payment_mode = db.Column(db.String(50))
    balance_after_transaction = db.Column(db.Numeric(15,2))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InvoiceRecord(db.Model):
    __tablename__ = 'invoice_records'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    invoice_number = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(200))
    invoice_amount = db.Column(db.Numeric(15,2), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    actual_payment_date = db.Column(db.Date)
    status = db.Column(db.String(50)) # 'paid', 'pending', 'overdue'
    delay_days = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id', ondelete='CASCADE'))
    expense_name = db.Column(db.String(200))
    expense_category = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15,2))
    expense_date = db.Column(db.Date)
    recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
