from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import os

from config import config
from app.models import db

# Initialize extensions
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=None  # Will be set in create_app
)
redis_client = None


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    # Initialize Redis
    global redis_client
    redis_client = Redis.from_url(app.config['REDIS_URL'])
    limiter.storage_uri = app.config['REDIS_URL']
    limiter.init_app(app)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes import auth, quiz, question, category, attempt, dashboard, file_upload, moderation, ai_search, admin
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(quiz.bp, url_prefix='/api/quiz')  # Handles both /quiz/* and /quizzes via routes
    app.register_blueprint(question.bp, url_prefix='/api/questions')
    app.register_blueprint(category.bp, url_prefix='/api/categories')
    app.register_blueprint(attempt.bp, url_prefix='/api/attempt')  # For /attempt/:id/submit
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    app.register_blueprint(file_upload.bp, url_prefix='/api/upload')
    app.register_blueprint(moderation.bp, url_prefix='/api/moderate')
    app.register_blueprint(ai_search.ai_search_bp, url_prefix='/api/ai')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    
    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Quiz Management System API is running'}
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired', 'msg': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token', 'msg': str(error)}, 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization required', 'msg': 'Missing authorization token'}, 401
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app
