import pandas as pd
import io
from flask import Blueprint, request, jsonify
from models import db, BankTransaction, InvoiceRecord, Expense, BankAccount, BusinessProfile
from sqlalchemy.exc import IntegrityError
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

@upload_bp.route('/bank-transactions', methods=['POST'])
def upload_bank_transactions():
    business_id = request.form.get('business_id')
    file = request.files.get('file')

    if not business_id or not file:
        return jsonify({"error": "Missing business_id or file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    # Auto-resolve bank account
    account = BankAccount.query.filter_by(business_id=business_id).first()
    if not account:
        return jsonify({"error": "No bank account found for this business. Please create one first."}), 404

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
        required_cols = ['transaction_date', 'amount', 'transaction_type']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({"error": f"Missing required column: {col}"}), 400

        rows_inserted = 0
        failed_reason = []
        
        transactions = []
        for index, row in df.iterrows():
            try:
                # Basic validation
                if pd.isna(row['amount']):
                    failed_reason.append(f"Row {index+1}: Amount is empty")
                    continue
                
                transactions.append(BankTransaction(
                    business_id=business_id,
                    bank_account_id=account.id,
                    transaction_date=pd.to_datetime(row['transaction_date']).date(),
                    amount=float(row['amount']),
                    transaction_type=str(row['transaction_type']).lower(),
                    category=row.get('category'),
                    merchant_name=row.get('merchant_name'),
                    payment_mode=row.get('payment_mode'),
                    balance_after_transaction=row.get('balance_after_transaction'),
                    description=row.get('description')
                ))
                rows_inserted += 1
            except Exception as e:
                failed_reason.append(f"Row {index+1}: {str(e)}")

        db.session.add_all(transactions)
        db.session.commit()

        return jsonify({
            "message": "Upload completed",
            "business_id": business_id,
            "rows_inserted": rows_inserted,
            "rows_failed": len(failed_reason),
            "failed_reason": failed_reason
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/invoices', methods=['POST'])
def upload_invoices():
    business_id = request.form.get('business_id')
    file = request.files.get('file')

    if not business_id or not file:
        return jsonify({"error": "Missing business_id or file"}), 400

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
        required_cols = ['invoice_number', 'invoice_amount', 'invoice_date', 'due_date']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({"error": f"Missing required column: {col}"}), 400

        invoices = []
        rows_inserted = 0
        failed_reason = []

        for index, row in df.iterrows():
            try:
                inv_date = pd.to_datetime(row['invoice_date']).date()
                due_date = pd.to_datetime(row['due_date']).date()
                
                # Handle optional actual_payment_date for delay calculation
                pay_date = None
                delay = row.get('delay_days', 0)
                if not pd.isna(row.get('actual_payment_date')):
                    pay_date = pd.to_datetime(row['actual_payment_date']).date()
                    delay = (pay_date - due_date).days

                invoices.append(InvoiceRecord(
                    business_id=business_id,
                    invoice_number=row['invoice_number'],
                    customer_name=row.get('customer_name'),
                    invoice_amount=float(row['invoice_amount']),
                    invoice_date=inv_date,
                    due_date=due_date,
                    actual_payment_date=pay_date,
                    status=row.get('status', 'pending'),
                    delay_days=int(delay)
                ))
                rows_inserted += 1
            except Exception as e:
                failed_reason.append(f"Row {index+1}: {str(e)}")

        db.session.add_all(invoices)
        db.session.commit()

        return jsonify({
            "message": "Invoices uploaded successfully",
            "business_id": business_id,
            "rows_inserted": rows_inserted,
            "rows_failed": len(failed_reason),
            "failed_reason": failed_reason
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@upload_bp.route('/expenses', methods=['POST'])
def upload_expenses():
    business_id = request.form.get('business_id')
    file = request.files.get('file')

    if not business_id or not file:
        return jsonify({"error": "Missing business_id or file"}), 400

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
        required_cols = ['expense_name', 'amount', 'expense_date']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({"error": f"Missing required column: {col}"}), 400

        expenses = []
        rows_inserted = 0
        failed_reason = []

        for index, row in df.iterrows():
            try:
                expenses.append(Expense(
                    business_id=business_id,
                    expense_name=row['expense_name'],
                    expense_category=row.get('expense_category'),
                    amount=float(row['amount']),
                    expense_date=pd.to_datetime(row['expense_date']).date(),
                    recurring=str(row.get('recurring', 'false')).lower() == 'true'
                ))
                rows_inserted += 1
            except Exception as e:
                failed_reason.append(f"Row {index+1}: {str(e)}")

        db.session.add_all(expenses)
        db.session.commit()

        return jsonify({
            "message": "Expenses uploaded successfully",
            "business_id": business_id,
            "rows_inserted": rows_inserted,
            "rows_failed": len(failed_reason),
            "failed_reason": failed_reason
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
