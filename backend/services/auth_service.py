import bcrypt
import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_secret')

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return 'Token expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        data = decode_token(token)
        if isinstance(data, str):
            return jsonify({"message": data}), 401
        
        return f(data, *args, **kwargs)
    
    return decorated
