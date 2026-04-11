from flask import Blueprint, request, jsonify
from models import db, User, BusinessUser
from services.auth_service import hash_password

team_bp = Blueprint('team', __name__)

@team_bp.route('/members', methods=['GET'])
def get_members():
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error": "Missing business_id"}), 400

    mappings = BusinessUser.query.filter_by(business_id=business_id).all()
    members = []
    for m in mappings:
        u = User.query.get(m.user_id)
        if u:
            members.append({
                "id": u.id,
                "name": u.full_name,
                "email": u.email,
                "role": m.role, # Role within the business
                "status": "Active" # Mocking status
            })

    return jsonify({"members": members}), 200

@team_bp.route('/invite', methods=['POST'])
def invite_member():
    data = request.get_json()
    req = ['business_id', 'email', 'name', 'role']
    for field in req:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        # Check if user exists
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            # Create user with dummy password
            user = User(
                full_name=data['name'],
                email=data['email'],
                password_hash=hash_password("welcome123"), # Default password for invited users
                role="msme_owner" # App system role
            )
            db.session.add(user)
            db.session.commit()

        # Check existing mapping
        mapping = BusinessUser.query.filter_by(user_id=user.id, business_id=data['business_id']).first()
        if mapping:
            return jsonify({"error": "User already in team"}), 400

        new_map = BusinessUser(
            user_id=user.id,
            business_id=data['business_id'],
            role=data['role']
        )
        db.session.add(new_map)
        db.session.commit()

        return jsonify({"message": "Member invited successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@team_bp.route('/remove', methods=['POST'])
def remove_member():
    data = request.get_json()
    if 'business_id' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing business_id or user_id"}), 400

    mapping = BusinessUser.query.filter_by(user_id=data['user_id'], business_id=data['business_id']).first()
    if not mapping:
        return jsonify({"error": "Member not found in this team"}), 404
        
    try:
        db.session.delete(mapping)
        db.session.commit()
        return jsonify({"message": "Member removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
