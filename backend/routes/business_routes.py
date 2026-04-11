from flask import Blueprint, request, jsonify
from models import db, BusinessProfile, BankAccount, User, BusinessUser

business_bp = Blueprint('business', __name__)

@business_bp.route('/create', methods=['POST'])
def create_business():
    data = request.get_json()
    
    # Basic validation
    required_fields = ['user_id', 'business_name', 'business_type', 'industry']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
            
    # Check if user exists
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    try:
        new_business = BusinessProfile(
            business_name=data['business_name'],
            business_type=data['business_type'],
            industry=data['industry'],
            gst_number=data.get('gst_number'),
            annual_revenue=data.get('annual_revenue'),
            employee_count=data.get('employee_count'),
            city=data.get('city'),
            state=data.get('state')
        )
        
        db.session.add(new_business)
        db.session.flush() # Get ID before commit
        
        # Create user business mapping
        mapping = BusinessUser(
            user_id=data['user_id'],
            business_id=new_business.id,
            role='owner',
            is_primary=True
        )
        db.session.add(mapping)
        
        # Create a default bank account as discussed
        default_account = BankAccount(
            business_id=new_business.id,
            bank_name="Primary Business Bank",
            account_number="ACC-" + str(new_business.id).zfill(5),
            account_type="Current",
            current_balance=0
        )
        db.session.add(default_account)
        
        db.session.commit()
        
        return jsonify({
            "message": "Business profile and primary bank account created successfully",
            "business_id": new_business.id,
            "business_name": new_business.business_name
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
