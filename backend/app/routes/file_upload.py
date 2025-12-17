from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.models import db, Attachment, QuestionBank, User, Quiz, QuizQuestionMap, Choice
from app.middleware.auth import role_required
from app.services.ai_service import LLMService
import PyPDF2
import docx

bp = Blueprint('file_upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path, file_type):
    """Extract text content from uploaded file"""
    try:
        if file_type == 'pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                return text.strip()
        
        elif file_type in ['doc', 'docx']:
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        
        return ''
    except Exception as e:
        current_app.logger.error(f"Text extraction error: {str(e)}")
        return ''



@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file for quiz generation"""
    user_id = int(get_jwt_identity())  # Convert string to int
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PDF, DOC, DOCX, or TXT'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create attachment record
        attachment = Attachment(
            file_name=filename,
            file_path=file_path,
            file_type=filename.rsplit('.', 1)[1].lower(),
            file_size=file_size
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': attachment.attachment_id,
            'file_name': filename,
            'file_size': file_size,
            'file_type': attachment.file_type
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upload file: {str(e)}'}), 500


@bp.route('/<int:file_id>/generate-quiz', methods=['POST'])
@jwt_required()
def generate_quiz_from_file(file_id):
    """Generate quiz from uploaded file"""
    user_id = int(get_jwt_identity())
    
    # Get request data
    data = request.get_json() or {}
    num_questions = data.get('num_questions', 10)
    
    # Validate num_questions
    if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 50:
        return jsonify({'error': 'Number of questions must be between 1 and 50'}), 400
    
    # Get the attachment
    attachment = db.session.get(Attachment, file_id)
    
    if not attachment:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Extract text from file
        extracted_text = extract_text_from_file(attachment.file_path, attachment.file_type)
        
        if not extracted_text:
            return jsonify({'error': 'Failed to extract text from file'}), 400
        
        # Limit text length
        max_chars = 5000
        if len(extracted_text) > max_chars:
            extracted_text = extracted_text[:max_chars] + "..."
        
        # Generate questions using AI
        llm_service = LLMService()
        questions_data, confidence = llm_service.generate_quiz_questions(
            topic=f"Content from {attachment.file_name}",
            num_questions=num_questions,
            difficulty='Medium',
            question_type='MCQ',
            context=extracted_text
        )
        
        if not questions_data:
            return jsonify({'error': 'Failed to generate questions from the content'}), 500
        
        # Create a new quiz
        quiz = Quiz(
            quiz_title=f"Quiz from {attachment.file_name}",
            description=f"AI-generated quiz with {len(questions_data)} questions",
            difficulty_level='Medium',
            passing_marks=60,
            time_limit_minutes=len(questions_data) * 2,  # 2 minutes per question
            created_by=user_id
        )
        db.session.add(quiz)
        db.session.flush()  # Get quiz_id
        
        # Create questions and choices
        for idx, q_data in enumerate(questions_data):
            # Create question in QuestionBank
            question = QuestionBank(
                question_text=q_data['question_text'],
                question_type='MCQ',
                difficulty_level='Medium',
                explanation=q_data.get('explanation', ''),
                verification_status='Verified' if confidence > 0.7 else 'Pending',
                created_by=user_id
            )
            db.session.add(question)
            db.session.flush()  # Get question_id
            
            # Link question to quiz
            quiz_question_map = QuizQuestionMap(
                quiz_id=quiz.quiz_id,
                question_id=question.question_id,
                sequence_number=idx + 1
            )
            db.session.add(quiz_question_map)
            
            # Create choices
            for choice_data in q_data.get('choices', []):
                choice = Choice(
                    question_id=question.question_id,
                    choice_text=choice_data['text'],
                    is_correct=choice_data['is_correct']
                )
                db.session.add(choice)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz generated successfully',
            'quiz_id': quiz.quiz_id,
            'quiz_title': quiz.quiz_title,
            'num_questions': len(questions_data),
            'confidence': confidence
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Quiz generation error: {str(e)}")
        return jsonify({'error': f'Failed to generate quiz: {str(e)}'}), 500


@bp.route('/files', methods=['GET'])
@jwt_required()
def get_user_files():
    """Get all files uploaded by the current user"""
    user_id = get_jwt_identity()
    
    # Get all attachments (for now, return all since we don't have user_id in Attachment model)
    attachments = Attachment.query.order_by(Attachment.uploaded_at.desc()).limit(50).all()
    
    result = []
    for attachment in attachments:
        result.append({
            'attachment_id': attachment.attachment_id,
            'file_name': attachment.file_name,
            'file_type': attachment.file_type,
            'file_size': attachment.file_size,
            'uploaded_at': attachment.uploaded_at.isoformat() if attachment.uploaded_at else None
        })
    
    return jsonify({'files': result}), 200


@bp.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
@role_required(['Admin', 'Teacher'])
def delete_file(file_id):
    """Delete an uploaded file"""
    attachment = db.session.get(Attachment, file_id)
    
    if not attachment:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Delete physical file
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)
        
        # Delete database record
        db.session.delete(attachment)
        db.session.commit()
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500
