from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from flask import Blueprint, g, jsonify, request
from sqlalchemy import func

from middleware.auth import require_auth
from models import (
    Alert, BankAccount, BankTransaction, BankingProductRecommendation,
    BusinessProfile, CashflowForecast, InvoiceRecord, LoanObligation,
    RiskScore, VendorPayment, db,
)

dashboard_bp = Blueprint('dashboard', __name__)


def _require_business_id():
    """Get business_id from query param or fall back to user's own business."""
    bid = request.args.get('business_id', type=int)
    if not bid:
        from routes.upload_routes import get_business_id
        bid = get_business_id(g.user_id)
    return bid


# ── MSME Dashboard Stats (single fast endpoint) ───────────────────────────────
@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    business_id = _require_business_id()
    if not business_id:
        return jsonify({'error': 'business_id is required'}), 400

    # 1. Closing balance — latest transaction balance
    latest_txn = (
        BankTransaction.query
        .filter_by(business_id=business_id)
        .order_by(BankTransaction.transaction_date.desc(), BankTransaction.id.desc())
        .first()
    )
    account = BankAccount.query.filter_by(business_id=business_id).first()
    balance = (
        float(latest_txn.balance_after_transaction)
        if latest_txn and latest_txn.balance_after_transaction
        else float(account.current_balance) if account else 0.0
    )

    # 2. Cashflow last 30 days
    since = date.today() - timedelta(days=30)
    txns = (
        BankTransaction.query
        .filter(BankTransaction.business_id == business_id,
                BankTransaction.transaction_date >= since)
        .all()
    )
    inflow  = sum(float(t.amount) for t in txns if t.transaction_type == 'credit')
    outflow = sum(float(t.amount) for t in txns if t.transaction_type == 'debit')

    daily: dict[str, dict] = defaultdict(lambda: {'inflow': 0.0, 'outflow': 0.0})
    for t in txns:
        d = t.transaction_date.isoformat()
        if t.transaction_type == 'credit':
            daily[d]['inflow'] += float(t.amount)
        else:
            daily[d]['outflow'] += float(t.amount)
    history = [
        {'date': d, 'inflow': daily[d]['inflow'], 'outflow': daily[d]['outflow'],
         'net': daily[d]['inflow'] - daily[d]['outflow']}
        for d in sorted(daily)
    ]

    # 3. Risk score
    risk = (
        RiskScore.query
        .filter_by(business_id=business_id)
        .order_by(RiskScore.forecast_date.desc())
        .first()
    )

    # 4. Invoices (latest 5)
    invoices = (
        InvoiceRecord.query
        .filter_by(business_id=business_id)
        .order_by(InvoiceRecord.due_date.asc())
        .limit(5).all()
    )

    # 5. Vendor payments (pending)
    vendors = (
        VendorPayment.query
        .filter_by(business_id=business_id, status='pending')
        .order_by(VendorPayment.due_date.asc())
        .limit(5).all()
    )

    # 6. Loans
    loans = (
        LoanObligation.query
        .filter_by(business_id=business_id)
        .order_by(LoanObligation.due_date.asc())
        .limit(5).all()
    )

    # 7. Recommendations
    recs = (
        BankingProductRecommendation.query
        .filter_by(business_id=business_id)
        .order_by(BankingProductRecommendation.confidence_score.desc())
        .limit(3).all()
    )

    return jsonify({
        'balance': balance,
        'cashflow': {
            'inflow': inflow,
            'outflow': outflow,
            'net': inflow - outflow,
            'history': history,
        },
        'risk_score': {
            'overall_risk_band':  risk.overall_risk_band  if risk else 'unknown',
            'liquidity_score':    risk.liquidity_score    if risk else 0,
            'default_risk_score': risk.default_risk_score if risk else 0,
            'overdraft_risk_score':   risk.overdraft_risk_score   if risk else 0,
            'working_capital_score':  risk.working_capital_score  if risk else 0,
        },
        'invoices': [{
            'invoice_number': i.invoice_number,
            'customer_name':  i.customer_name,
            'amount':    float(i.invoice_amount),
            'due_date':  i.due_date.isoformat(),
            'status':    i.status,
            'delay_days': i.delay_days or 0,
        } for i in invoices],
        'vendors': [{
            'vendor_name': v.vendor_name,
            'amount':  float(v.payment_amount),
            'due_date': v.due_date.isoformat() if v.due_date else None,
            'status':  v.status,
        } for v in vendors],
        'loans': [{
            'lender_name': l.lender_name,
            'loan_type':   l.loan_type,
            'emi_amount':  float(l.emi_amount),
            'due_date':    l.due_date.isoformat() if l.due_date else None,
            'outstanding_amount': float(l.outstanding_amount) if l.outstanding_amount else 0,
        } for l in loans],
        'recommendations': [{
            'product':    r.recommended_product,
            'reason':     r.reason,
            'confidence': float(r.confidence_score),
        } for r in recs],
    }), 200


# ── Bank / RM Portfolio Views ─────────────────────────────────────────────────
@dashboard_bp.route('/bank/portfolio', methods=['GET'])
@require_auth
def bank_portfolio():
    businesses = BusinessProfile.query.order_by(BusinessProfile.id).limit(50).all()
    result = []
    for biz in businesses:
        risk = (
            RiskScore.query.filter_by(business_id=biz.id)
            .order_by(RiskScore.forecast_date.desc()).first()
        )
        txn_count = (
            db.session.query(func.count(BankTransaction.id))
            .filter(BankTransaction.business_id == biz.id).scalar() or 0
        )
        result.append({
            'business_id':   biz.id,
            'business_name': biz.business_name,
            'industry':      biz.industry,
            'city':          biz.city,
            'state':         biz.state,
            'risk_band':     risk.overall_risk_band if risk else 'unknown',
            'liquidity_score':    risk.liquidity_score    if risk else None,
            'default_risk_score': risk.default_risk_score if risk else None,
            'transaction_count':  txn_count,
        })
    return jsonify({'businesses': result, 'total': len(result)}), 200


@dashboard_bp.route('/bank/risk-list', methods=['GET'])
@require_auth
def high_risk_list():
    rows = (
        db.session.query(RiskScore, BusinessProfile)
        .join(BusinessProfile, RiskScore.business_id == BusinessProfile.id)
        .filter(RiskScore.overall_risk_band.in_(['high', 'critical']))
        .order_by(RiskScore.forecast_date.desc())
        .limit(100).all()
    )
    return jsonify([{
        'business_id':   r.business_id,
        'business_name': b.business_name,
        'industry':      b.industry,
        'risk_band':     r.overall_risk_band,
        'liquidity_score':       r.liquidity_score,
        'default_risk_score':    r.default_risk_score,
        'overdraft_risk_score':  r.overdraft_risk_score,
        'working_capital_score': r.working_capital_score,
        'forecast_date': r.forecast_date.isoformat() if r.forecast_date else None,
    } for r, b in rows]), 200


@dashboard_bp.route('/bank/business/<int:business_id>', methods=['GET'])
@require_auth
def business_detail(business_id):
    biz = BusinessProfile.query.get_or_404(business_id)
    risk_history = (
        RiskScore.query.filter_by(business_id=business_id)
        .order_by(RiskScore.forecast_date.desc()).limit(10).all()
    )
    alerts = (
        Alert.query.filter_by(business_id=business_id)
        .order_by(Alert.created_at.desc()).limit(10).all()
    )
    return jsonify({
        'business': {
            'id': biz.id,
            'business_name': biz.business_name,
            'business_type': biz.business_type,
            'industry':      biz.industry,
            'city':          biz.city,
            'state':         biz.state,
            'annual_revenue': float(biz.annual_revenue) if biz.annual_revenue else None,
            'employee_count': biz.employee_count,
        },
        'risk_history': [{
            'forecast_date':    r.forecast_date.isoformat() if r.forecast_date else None,
            'liquidity_score':  r.liquidity_score,
            'default_risk_score': r.default_risk_score,
            'overall_risk_band':  r.overall_risk_band,
        } for r in risk_history],
        'alerts': [{
            'alert_type':    a.alert_type,
            'alert_message': a.alert_message,
            'severity':      a.severity,
            'is_read':       a.is_read,
        } for a in alerts],
    }), 200


# ── Alerts ────────────────────────────────────────────────────────────────────
@dashboard_bp.route('/alerts', methods=['GET'])
@require_auth
def get_alerts():
    business_id = _require_business_id()
    if not business_id:
        return jsonify({'error': 'business_id is required'}), 400
    alerts = (
        Alert.query.filter_by(business_id=business_id)
        .order_by(Alert.created_at.desc()).limit(50).all()
    )
    return jsonify([{
        'id':            a.id,
        'alert_type':    a.alert_type,
        'alert_message': a.alert_message,
        'severity':      a.severity,
        'is_read':       a.is_read,
        'created_at':    a.created_at.isoformat() if a.created_at else None,
    } for a in alerts]), 200


@dashboard_bp.route('/alerts/<int:alert_id>/read', methods=['PATCH'])
@require_auth
def mark_alert_read(alert_id):
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    alert.is_read = True
    db.session.commit()
    return jsonify({'message': 'Marked as read'}), 200


@dashboard_bp.route('/alerts/unread-count', methods=['GET'])
@require_auth
def unread_count():
    business_id = _require_business_id()
    if not business_id:
        return jsonify({'error': 'business_id is required'}), 400
    count = Alert.query.filter_by(business_id=business_id, is_read=False).count()
    return jsonify({'unread_count': count}), 200
