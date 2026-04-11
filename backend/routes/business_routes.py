from flask import Blueprint, request, jsonify, g
from models import db, BusinessProfile, BankAccount, User
from middleware.auth import require_auth

business_bp = Blueprint('business', __name__)


def _biz_to_dict(b: BusinessProfile) -> dict:
    return {
        'id': b.id,
        'business_name': b.business_name,
        'business_type': b.business_type,
        'industry': b.industry,
        'gst_number': b.gst_number,
        'annual_revenue': float(b.annual_revenue) if b.annual_revenue else None,
        'employee_count': b.employee_count,
        'city': b.city,
        'state': b.state,
    }


@business_bp.route('/create', methods=['POST'])
@require_auth
def create_business():
    data = request.get_json(force=True, silent=True) or {}

    required = ['business_name', 'business_type', 'industry']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400

    user = User.query.get(g.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # No user_id FK in DB — check by matching id (demo mapping)
    existing = BusinessProfile.query.filter_by(id=g.user_id).first()
    if existing:
        return jsonify({
            'message': 'Business profile already exists',
            'business_id': existing.id,
            'business_name': existing.business_name,
        }), 200

    try:
        biz = BusinessProfile(
            business_name=data['business_name'].strip(),
            business_type=data['business_type'],
            industry=data['industry'],
            gst_number=data.get('gst_number'),
            annual_revenue=data.get('annual_revenue'),
            employee_count=data.get('employee_count'),
            city=data.get('city'),
            state=data.get('state'),
        )
        db.session.add(biz)
        db.session.flush()

        account = BankAccount(
            business_id=biz.id,
            bank_name='Primary Business Bank',
            account_number=f'ACC-{biz.id:05d}',
            account_type='Current',
            current_balance=0,
        )
        db.session.add(account)
        db.session.commit()

        return jsonify({
            'message': 'Business profile created',
            'business_id': biz.id,
            'business_name': biz.business_name,
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@business_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    # Map user_id → business_id (demo: same id)
    biz = BusinessProfile.query.filter_by(id=g.user_id).first() \
          or BusinessProfile.query.first()
    if not biz:
        return jsonify({'error': 'No business profile found'}), 404
    return jsonify(_biz_to_dict(biz)), 200


@business_bp.route('/list', methods=['GET'])
@require_auth
def list_businesses():
    """For relationship managers — list all businesses."""
    businesses = BusinessProfile.query.order_by(BusinessProfile.id).limit(100).all()
    return jsonify([_biz_to_dict(b) for b in businesses]), 200
