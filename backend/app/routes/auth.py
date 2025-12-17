from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime
from app.models import db, User, Role
from app.utils.password import hash_password, verify_password, validate_password_strength
from app.utils.validators import validate_registration_data

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input data
    is_valid, error = validate_registration_data(data)
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Validate password strength
    is_valid, error = validate_password_strength(data['password'])
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Get role (default to 'Student' if not specified)
    role_name = data.get('role', 'Student')
    role = Role.query.filter_by(role_name=role_name).first()
    
    if not role:
        # If role doesn't exist, create default roles
        role = Role.query.filter_by(role_name='Student').first()
        if not role:
            return jsonify({'error': 'Default roles not initialized'}), 500
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        full_name=data['full_name'],
        role_id=role.role_id,
        profile_image=data.get('profile_image')
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Create tokens - identity must be string
        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': role.role_name,
                'profile_image': user.profile_image
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    # Verify password
    if not verify_password(data['password'], user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens - identity must be string
    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.role_name,
            'profile_image': user.profile_image,
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return jsonify({
        'access_token': access_token
    }), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.role_name,
            'profile_image': user.profile_image,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    }), 200


@bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'profile_image' in data:
        user.profile_image = data['profile_image']
    
    if 'email' in data and data['email'] != user.email:
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        user.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'profile_image': user.profile_image
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password are required'}), 400
    
    # Verify current password
    if not verify_password(data['current_password'], user.password_hash):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password
    is_valid, error = validate_password_strength(data['new_password'])
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # Update password
    user.password_hash = hash_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500
