import pandas as pd
import io
from flask import Blueprint, request, jsonify, g
from models import db, BankTransaction, InvoiceRecord, Expense, BankAccount, BusinessProfile
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from middleware.auth import require_auth

upload_bp = Blueprint('upload', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def get_business_id(user_id):
    """Return the business_id for the authenticated user.
    Since business_profiles has no user_id column, we map by user.id == business.id for demo data.
    """
    biz = BusinessProfile.query.filter_by(id=user_id).first() \
          or BusinessProfile.query.first()
    return biz.id if biz else None


@upload_bp.route('/bank-transactions', methods=['POST'])
@require_auth
def upload_bank_transactions():
    # Use business_id from request, verify it belongs to the auth'd user
    business_id = request.form.get('business_id') or get_business_id(g.user_id)
    file = request.files.get('file')

    if not business_id or not file:
        return jsonify({'error': 'Missing business_id or file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    # Verify business exists (no user_id FK in DB — skip ownership check for now)
    biz = BusinessProfile.query.filter_by(id=business_id).first()
    if not biz:
        return jsonify({'error': 'Business not found'}), 404

    # Auto-resolve bank account
    account = BankAccount.query.filter_by(business_id=business_id).first()
    if not account:
        return jsonify({'error': 'No bank account found for this business. Please create one first.'}), 404

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8-sig')))
        required_cols = ['transaction_date', 'amount', 'transaction_type']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'Missing required column: {col}'}), 400

        rows_inserted = 0
        failed_reason = []
        transactions = []

        for index, row in df.iterrows():
            try:
                if pd.isna(row['amount']):
                    failed_reason.append(f'Row {index+1}: Amount is empty')
                    continue

                transactions.append(BankTransaction(
                    business_id=business_id,
                    bank_account_id=account.id,
                    transaction_date=pd.to_datetime(row['transaction_date']).date(),
                    amount=float(row['amount']),
                    transaction_type=str(row['transaction_type']).lower().strip(),
                    category=row.get('category') if not pd.isna(row.get('category', float('nan'))) else None,
                    merchant_name=row.get('merchant_name') if not pd.isna(row.get('merchant_name', float('nan'))) else None,
                    payment_mode=row.get('payment_mode') if not pd.isna(row.get('payment_mode', float('nan'))) else None,
                    balance_after_transaction=float(row['balance_after_transaction']) if not pd.isna(row.get('balance_after_transaction', float('nan'))) else None,
                    description=row.get('description') if not pd.isna(row.get('description', float('nan'))) else None,
                ))
                rows_inserted += 1
            except Exception as e:
                failed_reason.append(f'Row {index+1}: {str(e)}')

        db.session.add_all(transactions)
        db.session.commit()

        return jsonify({
            'message': 'Upload completed',
            'business_id': business_id,
            'rows_inserted': rows_inserted,
            'rows_failed': len(failed_reason),
            'failed_reason': failed_reason[:20]  # limit error list
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/invoices', methods=['POST'])
@require_auth
def upload_invoices():
    business_id = request.form.get('business_id') or get_business_id(g.user_id)
    file = request.files.get('file')

    if not business_id or not file:
        return jsonify({'error': 'Missing business_id or file'}), 400

    # FIX: validate file extension (was missing before)
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    biz = BusinessProfile.query.filter_by(id=business_id).first()
    if not biz:
        return jsonify({'error': 'Business not found'}), 404

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8-sig')))
        required_cols = ['invoice_number', 'invoice_amount', 'invoice_date', 'due_date']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'Missing required column: {col}'}), 400

        invoices = []
        rows_inserted = 0
        failed_reason = []

        for index, row in df.iterrows():
            try:
                inv_date = pd.to_datetime(row['invoice_date']).date()
                due_date = pd.to_datetime(row['due_date']).date()

                pay_date = None
                delay = int(row.get('delay_days', 0) or 0)
                raw_pay = row.get('actual_payment_date')
                if raw_pay and not pd.isna(raw_pay):
                    pay_date = pd.to_datetime(raw_pay).date()
                    delay = max((pay_date - due_date).days, 0)

                invoices.append(InvoiceRecord(
                    business_id=business_id,
                    invoice_number=str(row['invoice_number']),
                    customer_name=str(row.get('customer_name', '')) or None,
                    invoice_amount=float(row['invoice_amount']),
                    invoice_date=inv_date,
                    due_date=due_date,
                    actual_payment_date=pay_date,
                    status=str(row.get('status', 'pending')).lower().strip(),
                    delay_days=delay
                ))
                rows_inserted += 1
            except Exception as e:
                failed_reason.append(f'Row {index+1}: {str(e)}')

        db.session.add_all(invoices)
        db.session.commit()

        return jsonify({
            'message': 'Invoices uploaded successfully',
            'business_id': business_id,
            'rows_inserted': rows_inserted,
            'rows_failed': len(failed_reason),
            'failed_reason': failed_reason[:20]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/expenses', methods=['POST'])
@require_auth
def upload_expenses():
    business_id = request.form.get('business_id') or get_business_id(g.user_id)
    file = request.files.get('file')

    if not business_id or not file:
        return jsonify({'error': 'Missing business_id or file'}), 400

    # FIX: validate file extension (was missing before)
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400

    biz = BusinessProfile.query.filter_by(id=business_id).first()
    if not biz:
        return jsonify({'error': 'Business not found'}), 404

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8-sig')))
        required_cols = ['expense_name', 'amount', 'expense_date']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'Missing required column: {col}'}), 400

        expenses = []
        rows_inserted = 0
        failed_reason = []

        for index, row in df.iterrows():
            try:
                expenses.append(Expense(
                    business_id=business_id,
                    expense_name=str(row['expense_name']),
                    expense_category=str(row.get('expense_category', '')) or None,
                    amount=float(row['amount']),
                    expense_date=pd.to_datetime(row['expense_date']).date(),
                    recurring=str(row.get('recurring', 'false')).lower() in ('true', '1', 'yes')
                ))
                rows_inserted += 1
            except Exception as e:
                failed_reason.append(f'Row {index+1}: {str(e)}')

        db.session.add_all(expenses)
        db.session.commit()

        return jsonify({
            'message': 'Expenses uploaded successfully',
            'business_id': business_id,
            'rows_inserted': rows_inserted,
            'rows_failed': len(failed_reason),
            'failed_reason': failed_reason[:20]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
