import io
import csv
from flask import Blueprint, jsonify, Response

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/report', methods=['POST'])
def generate_report():
    # Build a CSV with financial overview data
    data = [
        ['Report Generated', 'FlowSight AI Overview'],
        ['Metric', 'Value'],
        ['Cash Balance', '$42,500.00'],
        ['Cash Gap', '-$12,450.00'],
        ['Invoice Delay Risk', '3 invoices predicted late'],
        ['Working Capital Score', '64/100']
    ]
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    output = si.getvalue()
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=financial_overview_report.csv"}
    )

@dashboard_bp.route('/overview', methods=['GET'])
def get_overview():
    # Return mock overview data matching what frontend expects
    return jsonify({
        "cashBalance": 42500.00,
        "cashGap": -12450.00,
        "invoiceDelayRisk": 3,
        "workingCapitalScore": 64
    }), 200
