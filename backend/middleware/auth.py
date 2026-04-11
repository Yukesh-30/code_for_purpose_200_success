from functools import wraps
from flask import request, jsonify, g
from services.auth_service import decode_token


def require_auth(f):
    """JWT authentication decorator. Injects g.user_id and g.role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        token = auth_header[7:]
        payload = decode_token(token)
        if payload is None:
            return jsonify({'error': 'Token is invalid or has expired'}), 401
        g.user_id = payload['user_id']
        g.role = payload['role']
        g.business_id = payload.get('business_id')
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Role-based access control decorator. Use after @require_auth."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.get('role') not in roles:
                return jsonify({'error': f'Access denied. Required role: {", ".join(roles)}'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
