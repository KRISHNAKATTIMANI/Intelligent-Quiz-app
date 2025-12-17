from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Quiz, QuestionBank, QuizQuestionMap, Topic, User, Choice
from app.services.ai_service import LLMService
from datetime import datetime
import random

bp = Blueprint('quiz', __name__)
llm_service = LLMService()


@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_quiz():
    """Generate a quiz from category/topic selection with AI-generated questions"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Extract parameters - support both old and new API
        topic_id = data.get('topic_id')
        subcategory_id = data.get('subcategory_id')
        difficulty_input = data.get('difficulty_level') or data.get('difficulty', 'Medium')
        
        # Map difficulty levels: EASY->Easy, MEDIUM->Medium, HARD->Hard, ADVANCE->Hard
        difficulty_map = {
            'EASY': 'Easy',
            'MEDIUM': 'Medium',
            'HARD': 'Hard',
            'ADVANCE': 'Hard',  # Map ADVANCE to Hard since we only have Easy/Medium/Hard
            'Easy': 'Easy',
            'Medium': 'Medium',
            'Hard': 'Hard'
        }
        difficulty = difficulty_map.get(difficulty_input, 'Medium')
        
        num_questions = data.get('num_questions', 10)
        time_limit = data.get('time_limit', 30)  # minutes
        use_ai = data.get('use_ai', True)  # Option to use AI generation
        timer_option = data.get('timer_option', 'whole')
        total_time = data.get('total_time')
        per_question_time = data.get('per_question_time')
        instructions = data.get('instructions', '')
        
        # Handle both topic_id and subcategory_id for compatibility
        if subcategory_id and not topic_id:
            # Get first topic from subcategory
            from app.models import Subcategory
            subcategory = Subcategory.query.get(subcategory_id)
            if not subcategory:
                return jsonify({'error': 'Subcategory not found'}), 404
            topics = Topic.query.filter_by(subcategory_id=subcategory_id).all()
            if not topics:
                return jsonify({'error': 'No topics found for this subcategory'}), 404
            topic_id = topics[0].topic_id
        
        if not topic_id:
            return jsonify({'error': 'topic_id or subcategory_id is required'}), 400
        
        # Get topic details
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({'error': 'Topic not found'}), 404
        
        # Check existing questions first
        query = QuestionBank.query.filter_by(topic_id=topic_id, is_verified=True)
        if difficulty != 'Mixed':
            query = query.filter_by(difficulty_level=difficulty)
        
        existing_questions = query.all()
        
        # If not enough existing questions and AI is enabled, generate new ones
        if len(existing_questions) < num_questions and use_ai:
            current_app.logger.info(f"Generating {num_questions - len(existing_questions)} questions using AI for topic: {topic.topic_name}")
            
            # Generate questions using AI
            ai_questions, confidence = llm_service.generate_quiz_questions(
                topic=topic.topic_name,
                num_questions=num_questions - len(existing_questions),
                difficulty=difficulty,
                question_type='MCQ',
                context=None
            )
            
            current_app.logger.info(f"AI generated {len(ai_questions)} questions with confidence {confidence}")
            
            # Check if AI generation failed
            if not ai_questions:
                current_app.logger.error("AI question generation returned empty list")
                return jsonify({
                    'error': 'AI question generation failed. Please check your API key and try again.',
                    'details': 'OpenAI API may not be configured correctly'
                }), 500
            
            # Save AI-generated questions to database
            for q_data in ai_questions:
                new_question = QuestionBank(
                    topic_id=topic_id,
                    question_text=q_data['question_text'],
                    question_type='MCQ',
                    difficulty_level=difficulty,
                    points=1,
                    explanation_text=q_data.get('explanation', ''),
                    source='AI-Generated',
                    confidence_score=q_data.get('confidence', confidence),
                    is_verified=confidence > 0.7  # Auto-verify high confidence questions
                )
                db.session.add(new_question)
                db.session.flush()
                
                # Add choices
                for choice_data in q_data['choices']:
                    choice = Choice(
                        question_id=new_question.question_id,
                        choice_text=choice_data['text'],
                        is_correct=choice_data['is_correct']
                    )
                    db.session.add(choice)
                
                existing_questions.append(new_question)
            
            db.session.commit()
        
        # Select questions for quiz
        if len(existing_questions) < num_questions:
            return jsonify({
                'error': f'Not enough questions available. Found {len(existing_questions)}, requested {num_questions}',
                'suggestion': 'Try enabling AI generation or reduce the number of questions'
            }), 400
        
        selected_questions = random.sample(existing_questions, num_questions)
        
        # Calculate total marks
        total_marks = sum(q.points for q in selected_questions)
        passing_marks = int(total_marks * 0.4)  # 40% to pass
        
        # Create quiz
        quiz = Quiz(
            quiz_title=f"{topic.topic_name} Quiz",
            quiz_description=f"Quiz on {topic.topic_name} - {difficulty} difficulty",
            created_by=current_user_id,
            total_marks=total_marks,
            passing_marks=passing_marks,
            time_limit_minutes=total_time if timer_option == 'whole' and total_time else time_limit,
            difficulty_level=difficulty,
            is_published=True,
            is_public=True,
            shuffle_questions=True,
            shuffle_choices=True,
            allow_review=True,
            show_correct_answers=True,
            timer_option=timer_option,
            per_question_time=per_question_time if timer_option == 'each' else None,
            instructions=instructions
        )
        db.session.add(quiz)
        db.session.flush()
        
        # Map questions to quiz
        for idx, question in enumerate(selected_questions):
            mapping = QuizQuestionMap(
                quiz_id=quiz.quiz_id,
                question_id=question.question_id,
                question_order=idx + 1
            )
            db.session.add(mapping)
        
        db.session.commit()
        
        # Get questions with choices for immediate display
        questions_data = []
        mappings = QuizQuestionMap.query.filter_by(quiz_id=quiz.quiz_id).order_by(QuizQuestionMap.question_order).all()
        
        for mapping in mappings:
            question = mapping.question
            choices = []
            
            for choice in question.choices:
                choices.append({
                    'choice_id': choice.choice_id,
                    'choice_text': choice.choice_text
                })
            
            questions_data.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'points': question.points,
                'choices': choices
            })
        
        return jsonify({
            'message': 'Quiz generated successfully',
            'quiz_id': quiz.quiz_id,
            'quiz_title': quiz.quiz_title,
            'quiz_description': quiz.quiz_description,
            'total_questions': num_questions,
            'total_marks': total_marks,
            'time_limit': time_limit,
            'difficulty': difficulty,
            'timer_option': timer_option,
            'total_time': total_time,
            'per_question_time': per_question_time,
            'instructions': instructions,
            'questions': questions_data,
            'ai_generated': use_ai and len(ai_questions) > 0
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Quiz generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_quizzes():
    """Get all published quizzes"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get all published quizzes
        quizzes = Quiz.query.filter_by(is_published=True).all()
        
        result = []
        for quiz in quizzes:
            result.append({
                'quiz_id': quiz.quiz_id,
                'quiz_title': quiz.quiz_title,
                'quiz_description': quiz.quiz_description,
                'difficulty_level': quiz.difficulty_level,
                'total_marks': quiz.total_marks,
                'time_limit_minutes': quiz.time_limit_minutes,
                'total_questions': quiz.question_mappings.count(),
                'created_at': quiz.created_at.isoformat(),
                'is_public': quiz.is_public
            })
        
        return jsonify({'quizzes': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes_list():
    """Alternative route for getting all quizzes (matches frontend API call)"""
    return get_all_quizzes()


@bp.route('/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_details(quiz_id):
    """Get quiz details with questions"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Get questions with choices
        questions = []
        mappings = QuizQuestionMap.query.filter_by(quiz_id=quiz_id).order_by(QuizQuestionMap.question_order).all()
        
        for mapping in mappings:
            question = mapping.question
            choices = []
            
            for choice in question.choices:
                choices.append({
                    'choice_id': choice.choice_id,
                    'choice_text': choice.choice_text,
                    # Don't send is_correct initially
                })
            
            # Shuffle choices if needed
            if quiz.shuffle_choices:
                random.shuffle(choices)
            
            questions.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'difficulty_level': question.difficulty_level,
                'points': question.points,
                'time_limit_seconds': question.time_limit_seconds,
                'choices': choices
            })
        
        # Shuffle questions if needed
        if quiz.shuffle_questions:
            random.shuffle(questions)
        
        return jsonify({
            'quiz_id': quiz.quiz_id,
            'quiz_title': quiz.quiz_title,
            'quiz_description': quiz.quiz_description,
            'total_marks': quiz.total_marks,
            'passing_marks': quiz.passing_marks,
            'time_limit_minutes': quiz.time_limit_minutes,
            'difficulty_level': quiz.difficulty_level,
            'total_questions': len(questions),
            'questions': questions,
            'allow_review': quiz.allow_review,
            'show_correct_answers': quiz.show_correct_answers,
            'timer_option': quiz.timer_option,
            'per_question_time': quiz.per_question_time,
            'instructions': quiz.instructions
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    """Submit quiz answers and calculate results"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        answers = data.get('answers', {})  # {question_id: 'A'/'B'/'C'/'D'}
        time_taken = data.get('time_taken', 0)  # in seconds
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Get all questions with their correct answers
        mappings = QuizQuestionMap.query.filter_by(quiz_id=quiz_id).all()
        
        correct_count = 0
        total_questions = len(mappings)
        results = []
        
        for mapping in mappings:
            question = mapping.question
            question_id = str(question.question_id)
            user_answer = answers.get(question_id, '').upper()
            
            # Find correct answer from choices
            correct_choice = None
            for choice in question.choices:
                if choice.is_correct:
                    correct_choice = choice
                    break
            
            # Get choice letter (A, B, C, D) from choice text
            # This is a simplified approach - in production, you'd store choice letters
            choice_letters = ['A', 'B', 'C', 'D']
            correct_answer = 'A'  # default
            
            if correct_choice:
                for idx, choice in enumerate(sorted(question.choices, key=lambda x: x.choice_id)):
                    if choice.choice_id == correct_choice.choice_id:
                        correct_answer = choice_letters[idx] if idx < len(choice_letters) else 'A'
                        break
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            
            results.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'user_answer': user_answer if user_answer else None,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation_text or ''
            })
        
        # Calculate score
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        passed = score >= (quiz.passing_marks / quiz.total_marks * 100) if quiz.total_marks > 0 else False
        
        # Create attempt record
        from app.models import Attempt
        attempt = Attempt(
            user_id=current_user_id,
            quiz_id=quiz_id,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_count,
            wrong_answers=total_questions - correct_count,
            time_taken_seconds=time_taken,
            status='completed',
            passed=passed,
            percentage=score
        )
        db.session.add(attempt)
        db.session.commit()
        
        return jsonify({
            'attempt_id': attempt.attempt_id,
            'score': round(score, 1),
            'correct_count': correct_count,
            'total_questions': total_questions,
            'time_taken': time_taken,
            'passed': passed,
            'results': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Quiz submission error: {str(e)}")
        return jsonify({'error': str(e)}), 500
