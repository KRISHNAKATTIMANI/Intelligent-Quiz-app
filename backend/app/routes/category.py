from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.models import db, Category, Subcategory, Topic, QuestionBank
from app.middleware.auth import role_required

bp = Blueprint('category', __name__)


@bp.route('/all', methods=['GET'])
def get_all_categories():
    """Get all categories with subcategories (simplified for dropdown - public endpoint)"""
    categories = Category.query.order_by(Category.category_name).all()
    
    result = []
    for category in categories:
        subcategories_data = [
            {
                'subcategory_id': subcategory.subcategory_id,
                'subcategory_name': subcategory.subcategory_name,
                'description': subcategory.description
            }
            for subcategory in category.subcategories
        ]
        
        result.append({
            'category_id': category.category_id,
            'category_name': category.category_name,
            'description': category.description,
            'icon': category.icon,
            'subcategories': subcategories_data
        })
    
    return jsonify(result), 200


@bp.route('/', methods=['GET'])
def get_categories():
    """Get all categories with subcategories and topics"""
    categories = Category.query.order_by(Category.category_name).all()
    
    result = []
    for category in categories:
        subcategories_data = []
        for subcategory in category.subcategories:
            topics_data = [
                {
                    'topic_id': topic.topic_id,
                    'topic_name': topic.topic_name,
                    'description': topic.description,
                    'question_count': QuestionBank.query.filter_by(topic_id=topic.topic_id).count()
                }
                for topic in subcategory.topics
            ]
            
            subcategories_data.append({
                'subcategory_id': subcategory.subcategory_id,
                'subcategory_name': subcategory.subcategory_name,
                'description': subcategory.description,
                'topics': topics_data
            })
        
        result.append({
            'category_id': category.category_id,
            'category_name': category.category_name,
            'description': category.description,
            'icon': category.icon,
            'subcategories': subcategories_data
        })
    
    return jsonify({'categories': result}), 200


@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a single category with details"""
    category = db.session.get(Category, category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Count total questions in this category
    total_questions = db.session.query(func.count(QuestionBank.question_id))\
        .join(Topic)\
        .join(Subcategory)\
        .filter(Subcategory.category_id == category_id)\
        .scalar()
    
    subcategories_data = []
    for subcategory in category.subcategories:
        topics_data = [
            {
                'topic_id': topic.topic_id,
                'topic_name': topic.topic_name,
                'description': topic.description,
                'question_count': QuestionBank.query.filter_by(topic_id=topic.topic_id).count()
            }
            for topic in subcategory.topics
        ]
        
        subcategories_data.append({
            'subcategory_id': subcategory.subcategory_id,
            'subcategory_name': subcategory.subcategory_name,
            'description': subcategory.description,
            'topics': topics_data
        })
    
    return jsonify({
        'category': {
            'category_id': category.category_id,
            'category_name': category.category_name,
            'description': category.description,
            'icon': category.icon,
            'total_questions': total_questions,
            'subcategories': subcategories_data
        }
    }), 200


@bp.route('/', methods=['POST'])
@role_required('Admin', 'Teacher')
def create_category(user):
    """Create a new category (Admin/Teacher only)"""
    data = request.get_json()
    
    if not data.get('category_name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    # Check if category already exists
    if Category.query.filter_by(category_name=data['category_name']).first():
        return jsonify({'error': 'Category already exists'}), 409
    
    category = Category(
        category_name=data['category_name'],
        description=data.get('description'),
        icon=data.get('icon')
    )
    
    try:
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': {
                'category_id': category.category_id,
                'category_name': category.category_name,
                'description': category.description,
                'icon': category.icon
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create category: {str(e)}'}), 500


@bp.route('/<int:category_id>', methods=['PUT'])
@role_required('Admin', 'Teacher')
def update_category(user, category_id):
    """Update a category (Admin/Teacher only)"""
    category = db.session.get(Category, category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    data = request.get_json()
    
    if 'category_name' in data:
        # Check if new name already exists
        existing = Category.query.filter(
            Category.category_name == data['category_name'],
            Category.category_id != category_id
        ).first()
        if existing:
            return jsonify({'error': 'Category name already exists'}), 409
        category.category_name = data['category_name']
    
    if 'description' in data:
        category.description = data['description']
    
    if 'icon' in data:
        category.icon = data['icon']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Category updated successfully',
            'category': {
                'category_id': category.category_id,
                'category_name': category.category_name,
                'description': category.description,
                'icon': category.icon
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update category: {str(e)}'}), 500


@bp.route('/<int:category_id>', methods=['DELETE'])
@role_required('Admin')
def delete_category(user, category_id):
    """Delete a category (Admin only)"""
    category = db.session.get(Category, category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete category: {str(e)}'}), 500


# Subcategory routes
@bp.route('/subcategories', methods=['POST'])
@role_required('Admin', 'Teacher')
def create_subcategory(user):
    """Create a new subcategory"""
    data = request.get_json()
    
    if not data.get('category_id') or not data.get('subcategory_name'):
        return jsonify({'error': 'Category ID and subcategory name are required'}), 400
    
    # Check if category exists
    category = db.session.get(Category, data['category_id'])
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Check if subcategory already exists in this category
    existing = Subcategory.query.filter_by(
        category_id=data['category_id'],
        subcategory_name=data['subcategory_name']
    ).first()
    
    if existing:
        return jsonify({'error': 'Subcategory already exists in this category'}), 409
    
    subcategory = Subcategory(
        category_id=data['category_id'],
        subcategory_name=data['subcategory_name'],
        description=data.get('description')
    )
    
    try:
        db.session.add(subcategory)
        db.session.commit()
        
        return jsonify({
            'message': 'Subcategory created successfully',
            'subcategory': {
                'subcategory_id': subcategory.subcategory_id,
                'category_id': subcategory.category_id,
                'subcategory_name': subcategory.subcategory_name,
                'description': subcategory.description
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create subcategory: {str(e)}'}), 500


# Topic routes
@bp.route('/topics', methods=['POST'])
@role_required('Admin', 'Teacher')
def create_topic(user):
    """Create a new topic"""
    data = request.get_json()
    
    if not data.get('subcategory_id') or not data.get('topic_name'):
        return jsonify({'error': 'Subcategory ID and topic name are required'}), 400
    
    # Check if subcategory exists
    subcategory = db.session.get(Subcategory, data['subcategory_id'])
    if not subcategory:
        return jsonify({'error': 'Subcategory not found'}), 404
    
    # Check if topic already exists in this subcategory
    existing = Topic.query.filter_by(
        subcategory_id=data['subcategory_id'],
        topic_name=data['topic_name']
    ).first()
    
    if existing:
        return jsonify({'error': 'Topic already exists in this subcategory'}), 409
    
    topic = Topic(
        subcategory_id=data['subcategory_id'],
        topic_name=data['topic_name'],
        description=data.get('description')
    )
    
    try:
        db.session.add(topic)
        db.session.commit()
        
        return jsonify({
            'message': 'Topic created successfully',
            'topic': {
                'topic_id': topic.topic_id,
                'subcategory_id': topic.subcategory_id,
                'topic_name': topic.topic_name,
                'description': topic.description
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create topic: {str(e)}'}), 500


@bp.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    """Get a single topic with details"""
    topic = db.session.get(Topic, topic_id)
    
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    
    question_count = QuestionBank.query.filter_by(topic_id=topic_id).count()
    
    return jsonify({
        'topic': {
            'topic_id': topic.topic_id,
            'topic_name': topic.topic_name,
            'description': topic.description,
            'subcategory': {
                'subcategory_id': topic.subcategory.subcategory_id,
                'subcategory_name': topic.subcategory.subcategory_name,
                'category': {
                    'category_id': topic.subcategory.category.category_id,
                    'category_name': topic.subcategory.category.category_name
                }
            },
            'question_count': question_count
        }
    }), 200
