from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Attempt, Quiz, Streak

bp = Blueprint('dashboard', __name__)


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user dashboard statistics"""
    user_id = int(get_jwt_identity())  # Convert string back to int
    
    # Get user attempts
    attempts = Attempt.query.filter_by(user_id=user_id).all()
    
    # Calculate stats
    total_quizzes = len(attempts)
    completed_attempts = [a for a in attempts if a.status == 'Completed']
    
    if completed_attempts:
        avg_score = sum(a.percentage or 0 for a in completed_attempts) / len(completed_attempts)
        total_time = sum(a.time_taken_seconds or 0 for a in completed_attempts) // 3600  # Convert to hours
    else:
        avg_score = 0
        total_time = 0
    
    # Get streak
    streak = Streak.query.filter_by(user_id=user_id).first()
    current_streak = streak.current_streak if streak else 0
    
    return jsonify({
        'total_quizzes': total_quizzes,
        'average_score': round(avg_score, 1),
        'current_streak': current_streak,
        'total_time': total_time
    }), 200


@bp.route('/recent-attempts', methods=['GET'])
@jwt_required()
def get_recent_attempts():
    """Get user's recent quiz attempts"""
    user_id = int(get_jwt_identity())
    
    attempts = Attempt.query.filter_by(user_id=user_id)\
        .order_by(Attempt.created_at.desc())\
        .limit(10)\
        .all()
    
    result = []
    for attempt in attempts:
        result.append({
            'attempt_id': attempt.attempt_id,
            'quiz_title': attempt.quiz.quiz_title if attempt.quiz else 'Unknown',
            'score': attempt.score,
            'percentage': attempt.percentage,
            'status': attempt.status,
            'created_at': attempt.created_at.isoformat() if attempt.created_at else None
        })
    
    return jsonify({'attempts': result}), 200


@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized quiz recommendations"""
    user_id = int(get_jwt_identity())
    
    # For now, return sample recommendations
    # In production, this would use AI/ML to generate personalized recommendations
    return jsonify({
        'recommendations': []
    }), 200
