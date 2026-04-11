from flask import Blueprint, jsonify

risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/remind', methods=['POST'])
def send_reminder():
    return jsonify({"message": "Automated payment reminder sent to client."}), 200

@risk_bp.route('/factor', methods=['POST'])
def apply_factoring():
    return jsonify({"message": "Invoice factoring application initiated."}), 200
