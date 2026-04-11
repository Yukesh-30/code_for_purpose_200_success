from flask import Blueprint, jsonify

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/apply', methods=['POST'])
def apply_now():
    return jsonify({"message": "Application submitted for the selected banking product."}), 200

@recommendation_bp.route('/simulate', methods=['POST'])
def simulate_impact():
    return jsonify({"message": "Impact simulation complete. Check forecasting tab for updated liquidity bounds."}), 200
