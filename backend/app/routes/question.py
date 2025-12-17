from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_
from app.models import db, QuestionBank, Choice, Topic, Tag, QuestionTag, Attachment
from app.middleware.auth import role_required
from app.services.ai_service import llm_service, content_moderator

bp = Blueprint('question', __name__)


@bp.route('/', methods=['GET'])
@jwt_required()
def get_questions(user):
    """Get questions with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    topic_id = request.args.get('topic_id', type=int)
    difficulty = request.args.get('difficulty')
    question_type = request.args.get('type')
    search = request.args.get('search', '')
    
    query = QuestionBank.query
    
    # Apply filters
    if topic_id:
        query = query.filter_by(topic_id=topic_id)
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    if question_type:
        query = query.filter_by(question_type=question_type)
    
    if search:
        query = query.filter(QuestionBank.question_text.ilike(f'%{search}%'))
    
    # Paginate
    pagination = query.order_by(QuestionBank.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    questions = []
    for question in pagination.items:
        choices_data = [
            {
                'choice_id': choice.choice_id,
                'choice_text': choice.choice_text,
                'is_correct': choice.is_correct
            }
            for choice in question.choices
        ]
        
        questions.append({
            'question_id': question.question_id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'difficulty_level': question.difficulty_level,
            'points': question.points,
            'time_limit_seconds': question.time_limit_seconds,
            'source': question.source,
            'confidence_score': float(question.confidence_score) if question.confidence_score else None,
            'is_verified': question.is_verified,
            'topic': {
                'topic_id': question.topic.topic_id,
                'topic_name': question.topic.topic_name
            },
            'choices': choices_data,
            'created_at': question.created_at.isoformat()
        })
    
    return jsonify({
        'questions': questions,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200


@bp.route('/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question(user, question_id):
    """Get a single question with full details"""
    question = db.session.get(QuestionBank, question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    choices_data = [
        {
            'choice_id': choice.choice_id,
            'choice_text': choice.choice_text,
            'is_correct': choice.is_correct
        }
        for choice in question.choices
    ]
    
    tags_data = [
        {'tag_id': tag.tag_id, 'tag_name': tag.tag_name}
        for tag in question.tags
    ]
    
    return jsonify({
        'question': {
            'question_id': question.question_id,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'difficulty_level': question.difficulty_level,
            'points': question.points,
            'time_limit_seconds': question.time_limit_seconds,
            'explanation_text': question.explanation_text,
            'source': question.source,
            'confidence_score': float(question.confidence_score) if question.confidence_score else None,
            'is_verified': question.is_verified,
            'topic': {
                'topic_id': question.topic.topic_id,
                'topic_name': question.topic.topic_name,
                'subcategory': {
                    'subcategory_id': question.topic.subcategory.subcategory_id,
                    'subcategory_name': question.topic.subcategory.subcategory_name
                }
            },
            'choices': choices_data,
            'tags': tags_data,
            'created_at': question.created_at.isoformat()
        }
    }), 200


@bp.route('/', methods=['POST'])
@role_required('Admin', 'Teacher')
def create_question(user):
    """Create a new question manually"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['topic_id', 'question_text', 'question_type', 'difficulty_level']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check topic exists
    topic = db.session.get(Topic, data['topic_id'])
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    
    # Content moderation
    moderation_result = content_moderator.moderate_content(data['question_text'])
    if not moderation_result['is_safe']:
        return jsonify({
            'error': 'Content moderation failed',
            'details': moderation_result
        }), 400
    
    # Create question
    question = QuestionBank(
        topic_id=data['topic_id'],
        question_text=data['question_text'],
        question_type=data['question_type'],
        difficulty_level=data['difficulty_level'],
        points=data.get('points', 1),
        time_limit_seconds=data.get('time_limit_seconds'),
        explanation_text=data.get('explanation'),
        source='Manual',
        is_verified=True
    )
    
    try:
        db.session.add(question)
        db.session.flush()  # Get question_id
        
        # Add choices
        if data.get('choices'):
            for choice_data in data['choices']:
                choice = Choice(
                    question_id=question.question_id,
                    choice_text=choice_data['text'],
                    is_correct=choice_data.get('is_correct', False)
                )
                db.session.add(choice)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Question created successfully',
            'question_id': question.question_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create question: {str(e)}'}), 500


@bp.route('/generate', methods=['POST'])
@role_required('Admin', 'Teacher')
def generate_questions(user):
    """Generate questions using AI"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('topic_id'):
        return jsonify({'error': 'topic_id is required'}), 400
    
    # Get topic
    topic = db.session.get(Topic, data['topic_id'])
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    
    # Extract parameters
    num_questions = data.get('num_questions', 10)
    difficulty = data.get('difficulty', 'Medium')
    question_type = data.get('question_type', 'MCQ')
    context = data.get('context')  # Optional context from file
    
    # Generate questions using AI
    generated_questions, confidence = llm_service.generate_quiz_questions(
        topic=topic.topic_name,
        num_questions=num_questions,
        difficulty=difficulty,
        question_type=question_type,
        context=context
    )
    
    if not generated_questions:
        return jsonify({'error': 'Failed to generate questions'}), 500
    
    # Save generated questions to database
    saved_questions = []
    
    try:
        for q_data in generated_questions:
            # Content moderation
            moderation_result = content_moderator.moderate_content(q_data['question_text'])
            if not moderation_result['is_safe']:
                continue  # Skip unsafe questions
            
            question = QuestionBank(
                topic_id=topic.topic_id,
                question_text=q_data['question_text'],
                question_type=question_type,
                difficulty_level=difficulty,
                points=1,
                explanation_text=q_data.get('explanation'),
                source='AI-Generated',
                confidence_score=q_data.get('confidence', confidence),
                is_verified=False  # AI-generated questions need verification
            )
            
            db.session.add(question)
            db.session.flush()
            
            # Add choices
            if question_type in ['MCQ', 'True/False'] and 'choices' in q_data:
                for choice_data in q_data['choices']:
                    choice = Choice(
                        question_id=question.question_id,
                        choice_text=choice_data['text'],
                        is_correct=choice_data.get('is_correct', False)
                    )
                    db.session.add(choice)
            
            saved_questions.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'confidence_score': float(question.confidence_score)
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Generated {len(saved_questions)} questions successfully',
            'questions': saved_questions,
            'average_confidence': confidence
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save generated questions: {str(e)}'}), 500


@bp.route('/<int:question_id>', methods=['PUT'])
@role_required('Admin', 'Teacher')
def update_question(user, question_id):
    """Update a question"""
    question = db.session.get(QuestionBank, question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'question_text' in data:
        # Content moderation
        moderation_result = content_moderator.moderate_content(data['question_text'])
        if not moderation_result['is_safe']:
            return jsonify({
                'error': 'Content moderation failed',
                'details': moderation_result
            }), 400
        question.question_text = data['question_text']
    
    if 'difficulty_level' in data:
        question.difficulty_level = data['difficulty_level']
    
    if 'points' in data:
        question.points = data['points']
    
    if 'explanation_text' in data:
        question.explanation_text = data['explanation_text']
    
    if 'is_verified' in data:
        question.is_verified = data['is_verified']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Question updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update question: {str(e)}'}), 500


@bp.route('/<int:question_id>', methods=['DELETE'])
@role_required('Admin', 'Teacher')
def delete_question(user, question_id):
    """Delete a question"""
    question = db.session.get(QuestionBank, question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    try:
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete question: {str(e)}'}), 500
