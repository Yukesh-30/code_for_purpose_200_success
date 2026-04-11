from flask import Blueprint, jsonify, request, g
from models import db, Alert
from middleware.auth import require_auth

alert_bp = Blueprint('alerts', __name__)


@alert_bp.route('/alerts', methods=['GET'])
@require_auth
def get_alerts():
    business_id = request.args.get('business_id', type=int)
    if not business_id:
        return jsonify({'error': 'business_id is required'}), 400

    alerts = Alert.query.filter_by(business_id=business_id).order_by(Alert.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': a.id,
        'alert_type': a.alert_type,
        'alert_message': a.alert_message,
        'severity': a.severity,
        'is_read': a.is_read,
        'created_at': a.created_at.isoformat() if a.created_at else None,
    } for a in alerts]), 200


@alert_bp.route('/alerts/<int:alert_id>/read', methods=['PATCH'])
@require_auth
def mark_alert_read(alert_id):
    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    alert.is_read = True
    db.session.commit()
    return jsonify({'message': 'Alert marked as read'}), 200


@alert_bp.route('/alerts/unread-count', methods=['GET'])
@require_auth
def unread_count():
    business_id = request.args.get('business_id', type=int)
    if not business_id:
        return jsonify({'error': 'business_id is required'}), 400
    count = Alert.query.filter_by(business_id=business_id, is_read=False).count()
    return jsonify({'unread_count': count}), 200
