from flask import Blueprint, request, jsonify
from models import db, User
from services.auth_service import hash_password, check_password, generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(
        full_name=data.get('full_name'),
        email=data['email'],
        password_hash=hash_password(data['password']),
        role=data.get('role', 'msme_owner'),
        phone_number=data.get('phone_number')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully",
        "user_id": new_user.id
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Missing credentials"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password(data['password'], user.password_hash):
        return jsonify({"message": "Invalid email or password"}), 401
    
    token = generate_token(user.id, user.role)
    
    return jsonify({
        "access_token": token,
        "role": user.role,
        "user": {
            "name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }), 200
