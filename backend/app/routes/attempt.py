from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Attempt, Quiz, AttemptAnswer, QuestionBank, Choice, QuizQuestionMap, Streak
from datetime import datetime, timedelta

bp = Blueprint('attempt', __name__)


@bp.route('/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_attempt(quiz_id):
    """Start a new quiz attempt"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if quiz exists
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Get total questions
        total_questions = QuizQuestionMap.query.filter_by(quiz_id=quiz_id).count()
        
        # Create new attempt
        attempt = Attempt(
            user_id=current_user_id,
            quiz_id=quiz_id,
            start_time=datetime.utcnow(),
            total_questions=total_questions,
            status='In-Progress'
        )
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz attempt started',
            'attempt_id': attempt.attempt_id,
            'quiz_id': quiz_id,
            'start_time': attempt.start_time.isoformat(),
            'time_limit_minutes': quiz.time_limit_minutes
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_attempt(attempt_id):
    """Submit quiz attempt with answers"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        answers = data.get('answers', [])  # List of {question_id, selected_choice_id}
        
        # Get attempt
        attempt = Attempt.query.get(attempt_id)
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        if attempt.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if attempt.status == 'Completed':
            return jsonify({'error': 'Attempt already completed'}), 400
        
        # Process answers
        correct_count = 0
        wrong_count = 0
        total_score = 0
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            selected_choice_id = answer_data.get('selected_choice_id')
            time_spent = answer_data.get('time_spent_seconds', 0)
            
            if not question_id or not selected_choice_id:
                continue
            
            # Get question and selected choice
            question = QuestionBank.query.get(question_id)
            selected_choice = Choice.query.get(selected_choice_id)
            
            if not question or not selected_choice:
                continue
            
            # Check if answer is correct
            is_correct = selected_choice.is_correct
            points_earned = question.points if is_correct else 0
            
            if is_correct:
                correct_count += 1
                total_score += points_earned
            else:
                wrong_count += 1
            
            # Save answer
            attempt_answer = AttemptAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_choice_id=selected_choice_id,
                is_correct=is_correct,
                points_earned=points_earned,
                time_spent_seconds=time_spent
            )
            db.session.add(attempt_answer)
        
        # Calculate unanswered
        unanswered = attempt.total_questions - (correct_count + wrong_count)
        
        # Calculate time taken
        time_taken = int((datetime.utcnow() - attempt.start_time).total_seconds())
        
        # Get quiz for passing marks
        quiz = Quiz.query.get(attempt.quiz_id)
        passed = total_score >= (quiz.passing_marks or 0)
        
        # Calculate percentage
        percentage = (total_score / quiz.total_marks * 100) if quiz.total_marks > 0 else 0
        
        # Update attempt
        attempt.end_time = datetime.utcnow()
        attempt.score = total_score
        attempt.correct_answers = correct_count
        attempt.wrong_answers = wrong_count
        attempt.unanswered = unanswered
        attempt.time_taken_seconds = time_taken
        attempt.status = 'Completed'
        attempt.passed = passed
        attempt.percentage = round(percentage, 2)
        
        # Update streak
        update_user_streak(current_user_id, passed)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz submitted successfully',
            'attempt_id': attempt_id,
            'score': total_score,
            'total_marks': quiz.total_marks,
            'percentage': round(percentage, 2),
            'passed': passed,
            'correct_answers': correct_count,
            'wrong_answers': wrong_count,
            'unanswered': unanswered,
            'time_taken_seconds': time_taken
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_attempt_results(attempt_id):
    """Get detailed results for an attempt"""
    try:
        current_user_id = int(get_jwt_identity())
        
        attempt = Attempt.query.get(attempt_id)
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        if attempt.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get quiz details
        quiz = Quiz.query.get(attempt.quiz_id)
        
        # Get answers with questions and correct answers
        answers = []
        attempt_answers = AttemptAnswer.query.filter_by(attempt_id=attempt_id).all()
        
        for ans in attempt_answers:
            question = ans.question
            selected_choice = ans.selected_choice
            
            # Get all choices with correct answer
            choices = []
            for choice in question.choices:
                choices.append({
                    'choice_id': choice.choice_id,
                    'choice_text': choice.choice_text,
                    'is_correct': choice.is_correct
                })
            
            answers.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'selected_choice_id': selected_choice.choice_id if selected_choice else None,
                'selected_choice_text': selected_choice.choice_text if selected_choice else None,
                'is_correct': ans.is_correct,
                'points_earned': ans.points_earned,
                'points_possible': question.points,
                'explanation': question.explanation_text,
                'choices': choices if quiz.show_correct_answers else []
            })
        
        return jsonify({
            'attempt_id': attempt_id,
            'quiz_title': quiz.quiz_title,
            'score': attempt.score,
            'total_marks': quiz.total_marks,
            'percentage': float(attempt.percentage) if attempt.percentage else 0,
            'passed': attempt.passed,
            'correct_answers': attempt.correct_answers,
            'wrong_answers': attempt.wrong_answers,
            'unanswered': attempt.unanswered,
            'time_taken_seconds': attempt.time_taken_seconds,
            'start_time': attempt.start_time.isoformat(),
            'end_time': attempt.end_time.isoformat() if attempt.end_time else None,
            'answers': answers
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def update_user_streak(user_id, passed):
    """Update user's streak based on quiz performance"""
    try:
        today = datetime.utcnow().date()
        
        # Get or create streak record
        streak = Streak.query.filter_by(user_id=user_id).first()
        
        if not streak:
            streak = Streak(user_id=user_id, current_streak=0, longest_streak=0)
            db.session.add(streak)
        
        # Check if activity is from today
        if streak.last_activity_date == today:
            return  # Already updated today
        
        # Check if activity is consecutive
        yesterday = today - timedelta(days=1)
        
        if passed:
            if streak.last_activity_date == yesterday:
                # Consecutive day
                streak.current_streak += 1
            else:
                # New streak
                streak.current_streak = 1
            
            # Update longest streak
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        else:
            # Failed quiz, but don't break streak for missing days
            if streak.last_activity_date and streak.last_activity_date < yesterday:
                streak.current_streak = 0
        
        streak.last_activity_date = today
        db.session.commit()
        
    except Exception as e:
        print(f"Error updating streak: {e}")
        db.session.rollback()
