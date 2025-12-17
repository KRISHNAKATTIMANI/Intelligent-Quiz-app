from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Role
from app.utils.cleanup import cleanup_old_ai_questions, cleanup_orphaned_choices, get_cleanup_stats
from functools import wraps

bp = Blueprint('admin', __name__)


def admin_required():
    """Decorator to require admin role"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = int(get_jwt_identity())
            user = User.query.get(current_user_id)
            
            if not user or user.role.role_name != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@bp.route('/cleanup/run', methods=['POST'])
@admin_required()
def run_cleanup():
    """Run database cleanup tasks (admin only)"""
    try:
        # Run AI question cleanup
        ai_result = cleanup_old_ai_questions()
        
        # Run orphaned choices cleanup
        choices_result = cleanup_orphaned_choices()
        
        return jsonify({
            'success': True,
            'ai_questions': ai_result,
            'orphaned_choices': choices_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Admin cleanup error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/cleanup/stats', methods=['GET'])
@admin_required()
def get_stats():
    """Get cleanup statistics (admin only)"""
    try:
        stats = get_cleanup_stats()
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Admin stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/health', methods=['GET'])
@admin_required()
def health_check():
    """Admin health check endpoint"""
    try:
        from app.models import db
        
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Get basic stats
        stats = get_cleanup_stats()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ai_questions': stats.get('total_ai_questions', 0),
            'cleanup_eligible': stats.get('cleanup_eligible', 0)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
