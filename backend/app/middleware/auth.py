from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User, db


def jwt_required_with_user(fn):
    """Decorator that validates JWT and loads user"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return fn(user, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator that checks if user has required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            if user.role.role_name not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator
