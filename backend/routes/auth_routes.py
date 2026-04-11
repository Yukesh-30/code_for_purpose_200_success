from flask import Blueprint, request, jsonify, g
from models import db, User, BusinessProfile
from services.auth_service import hash_password, check_password, generate_token
from middleware.auth import require_auth

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True, silent=True)

    missing = [f for f in ('email', 'password', 'full_name') if not data or not data.get(f)]
    if missing:
        return jsonify({'message': f'Missing required fields: {", ".join(missing)}'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(
        full_name=data['full_name'].strip(),
        email=data['email'].strip().lower(),
        password_hash=hash_password(data['password']),
        role=data.get('role', 'msme_owner'),
        phone_number=data.get('phone_number'),
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True)

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing credentials'}), 400

    user = User.query.filter_by(email=data['email'].strip().lower()).first()

    if not user or not check_password(data['password'], user.password_hash):
        return jsonify({'message': 'Invalid email or password'}), 401

    token = generate_token(user.id, user.role)
    # business_profiles has no user_id column — map by user order for demo
    # In production this would be a proper user_id FK
    business = BusinessProfile.query.filter_by(id=user.id).first() \
               or BusinessProfile.query.first()
    business_id = business.id if business else None

    return jsonify({
        'access_token': token,
        'role': user.role,
        'business_id': business_id,
        'user': {
            'id': user.id,
            'name': user.full_name,
            'email': user.email,
            'role': user.role,
            'business_id': business_id,
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    user = User.query.get(g.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    business = BusinessProfile.query.filter_by(id=user.id).first() \
               or BusinessProfile.query.first()
    return jsonify({
        'id': user.id,
        'name': user.full_name,
        'email': user.email,
        'role': user.role,
        'business_id': business.id if business else None,
    }), 200
