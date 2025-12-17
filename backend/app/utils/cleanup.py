"""
Cleanup utilities for maintaining database health
"""
from datetime import datetime, timedelta
from flask import current_app
from app.models import db, QuestionBank, QuizQuestionMap, AttemptAnswer, Choice


def cleanup_old_ai_questions():
    """
    Delete AI-generated questions older than configured retention period (default 7 days).
    Only deletes questions that are not currently being used in any active quiz attempts.
    
    Returns:
        dict: Statistics about the cleanup operation
    """
    try:
        retention_days = current_app.config.get('AI_QUESTION_RETENTION_DAYS', 7)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Find AI-generated questions older than retention period
        old_questions = QuestionBank.query.filter(
            QuestionBank.source == 'AI-Generated',
            QuestionBank.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        skipped_count = 0
        
        for question in old_questions:
            # Check if question is used in any quiz attempts
            has_attempts = AttemptAnswer.query.filter_by(
                question_id=question.question_id
            ).first() is not None
            
            # Check if question is in an active quiz
            has_quiz = QuizQuestionMap.query.filter_by(
                question_id=question.question_id
            ).first() is not None
            
            if not has_attempts and not has_quiz:
                # Safe to delete - no quiz usage or attempt history
                # Choices will be deleted automatically due to cascade
                db.session.delete(question)
                deleted_count += 1
            else:
                # Skip deletion - question is in use
                skipped_count += 1
        
        db.session.commit()
        
        result = {
            'success': True,
            'deleted_count': deleted_count,
            'skipped_count': skipped_count,
            'retention_days': retention_days,
            'cutoff_date': cutoff_date.isoformat(),
            'message': f'Deleted {deleted_count} AI-generated questions older than {retention_days} days. Skipped {skipped_count} questions still in use.'
        }
        
        current_app.logger.info(result['message'])
        return result
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Cleanup error: {str(e)}"
        current_app.logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'deleted_count': 0,
            'skipped_count': 0
        }


def cleanup_orphaned_choices():
    """
    Delete choices that don't have a corresponding question.
    This can happen if questions are deleted outside of normal cascades.
    
    Returns:
        dict: Statistics about the cleanup operation
    """
    try:
        # Find choices without valid questions
        orphaned_choices = db.session.query(Choice).filter(
            ~Choice.question_id.in_(
                db.session.query(QuestionBank.question_id)
            )
        ).all()
        
        count = len(orphaned_choices)
        
        for choice in orphaned_choices:
            db.session.delete(choice)
        
        db.session.commit()
        
        result = {
            'success': True,
            'deleted_count': count,
            'message': f'Deleted {count} orphaned choices'
        }
        
        current_app.logger.info(result['message'])
        return result
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Orphaned choices cleanup error: {str(e)}"
        current_app.logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'deleted_count': 0
        }


def get_cleanup_stats():
    """
    Get statistics about questions that would be affected by cleanup.
    
    Returns:
        dict: Statistics about questions eligible for cleanup
    """
    try:
        retention_days = current_app.config.get('AI_QUESTION_RETENTION_DAYS', 7)
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Count old AI-generated questions
        old_ai_questions = QuestionBank.query.filter(
            QuestionBank.source == 'AI-Generated',
            QuestionBank.created_at < cutoff_date
        ).count()
        
        # Count total AI-generated questions
        total_ai_questions = QuestionBank.query.filter_by(
            source='AI-Generated'
        ).count()
        
        # Count questions by age ranges
        now = datetime.utcnow()
        last_24h = QuestionBank.query.filter(
            QuestionBank.source == 'AI-Generated',
            QuestionBank.created_at > now - timedelta(hours=24)
        ).count()
        
        last_7d = QuestionBank.query.filter(
            QuestionBank.source == 'AI-Generated',
            QuestionBank.created_at > now - timedelta(days=7)
        ).count()
        
        return {
            'success': True,
            'retention_days': retention_days,
            'cutoff_date': cutoff_date.isoformat(),
            'old_ai_questions': old_ai_questions,
            'total_ai_questions': total_ai_questions,
            'ai_questions_last_24h': last_24h,
            'ai_questions_last_7d': last_7d,
            'cleanup_eligible': old_ai_questions
        }
        
    except Exception as e:
        error_msg = f"Stats error: {str(e)}"
        current_app.logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg
        }
