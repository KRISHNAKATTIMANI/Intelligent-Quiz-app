from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.role_name}>'


# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    full_name = db.Column(db.String(255))
    profile_image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = db.relationship('Role', back_populates='users')
    quizzes = db.relationship('Quiz', back_populates='creator', lazy='dynamic')
    attempts = db.relationship('Attempt', back_populates='user', lazy='dynamic')
    recommendations = db.relationship('Recommendation', back_populates='user', lazy='dynamic')
    streaks = db.relationship('Streak', back_populates='user', lazy='dynamic')
    dashboard_cache = db.relationship('UserDashboardCache', back_populates='user', uselist=False)
    
    def __repr__(self):
        return f'<User {self.username}>'


# Category Model
class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subcategories = db.relationship('Subcategory', back_populates='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.category_name}>'


# Subcategory Model
class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    
    subcategory_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=False)
    subcategory_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', back_populates='subcategories')
    topics = db.relationship('Topic', back_populates='subcategory', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('category_id', 'subcategory_name', name='unique_subcategory_per_category'),
    )
    
    def __repr__(self):
        return f'<Subcategory {self.subcategory_name}>'


# Topic Model
class Topic(db.Model):
    __tablename__ = 'topics'
    
    topic_id = db.Column(db.Integer, primary_key=True)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.subcategory_id', ondelete='CASCADE'), nullable=False)
    topic_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subcategory = db.relationship('Subcategory', back_populates='topics')
    questions = db.relationship('QuestionBank', back_populates='topic', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('subcategory_id', 'topic_name', name='unique_topic_per_subcategory'),
    )
    
    def __repr__(self):
        return f'<Topic {self.topic_name}>'


# QuestionBank Model
class QuestionBank(db.Model):
    __tablename__ = 'question_bank'
    
    question_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('MCQ', 'True/False', 'Fill-in-the-Blank', name='question_type_enum'), nullable=False)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard', name='difficulty_level_enum'), nullable=False)
    points = db.Column(db.Integer, default=1)
    time_limit_seconds = db.Column(db.Integer)
    explanation_text = db.Column(db.Text)
    source = db.Column(db.Enum('Manual', 'AI-Generated', 'File-Upload', name='source_enum'), default='Manual')
    confidence_score = db.Column(db.Numeric(3, 2))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic = db.relationship('Topic', back_populates='questions')
    choices = db.relationship('Choice', back_populates='question', lazy='dynamic', cascade='all, delete-orphan')
    quiz_mappings = db.relationship('QuizQuestionMap', back_populates='question', lazy='dynamic')
    attempt_answers = db.relationship('AttemptAnswer', back_populates='question', lazy='dynamic')
    explanations = db.relationship('Explanation', back_populates='question', lazy='dynamic')
    tags = db.relationship('Tag', secondary='question_tags', back_populates='questions')
    attachments = db.relationship('Attachment', back_populates='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<QuestionBank {self.question_id}>'


# Choice Model
class Choice(db.Model):
    __tablename__ = 'choices'
    
    choice_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.question_id', ondelete='CASCADE'), nullable=False)
    choice_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('QuestionBank', back_populates='choices')
    
    def __repr__(self):
        return f'<Choice {self.choice_id}>'


# Quiz Model
class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    quiz_id = db.Column(db.Integer, primary_key=True)
    quiz_title = db.Column(db.String(255), nullable=False)
    quiz_description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    total_marks = db.Column(db.Integer)
    passing_marks = db.Column(db.Integer)
    time_limit_minutes = db.Column(db.Integer)
    difficulty_level = db.Column(db.Enum('Easy', 'Medium', 'Hard', 'Mixed', name='quiz_difficulty_enum'))
    is_published = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=True)
    shuffle_questions = db.Column(db.Boolean, default=False)
    shuffle_choices = db.Column(db.Boolean, default=False)
    allow_review = db.Column(db.Boolean, default=True)
    show_correct_answers = db.Column(db.Boolean, default=True)
    thumbnail_url = db.Column(db.String(500))
    timer_option = db.Column(db.String(10))  # 'whole' or 'each'
    per_question_time = db.Column(db.Integer)  # seconds per question
    instructions = db.Column(db.Text)  # quiz instructions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', back_populates='quizzes')
    question_mappings = db.relationship('QuizQuestionMap', back_populates='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('Attempt', back_populates='quiz', lazy='dynamic')
    
    def __repr__(self):
        return f'<Quiz {self.quiz_title}>'


# QuizQuestionMap Model
class QuizQuestionMap(db.Model):
    __tablename__ = 'quiz_question_map'
    
    map_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.question_id', ondelete='CASCADE'), nullable=False)
    question_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz = db.relationship('Quiz', back_populates='question_mappings')
    question = db.relationship('QuestionBank', back_populates='quiz_mappings')
    
    __table_args__ = (
        db.UniqueConstraint('quiz_id', 'question_id', name='unique_quiz_question'),
    )
    
    def __repr__(self):
        return f'<QuizQuestionMap quiz={self.quiz_id} question={self.question_id}>'


# Attempt Model
class Attempt(db.Model):
    __tablename__ = 'attempts'
    
    attempt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    wrong_answers = db.Column(db.Integer)
    unanswered = db.Column(db.Integer)
    time_taken_seconds = db.Column(db.Integer)
    status = db.Column(db.Enum('In-Progress', 'Completed', 'Abandoned', name='attempt_status_enum'), default='In-Progress')
    passed = db.Column(db.Boolean)
    percentage = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='attempts')
    quiz = db.relationship('Quiz', back_populates='attempts')
    answers = db.relationship('AttemptAnswer', back_populates='attempt', lazy='dynamic', cascade='all, delete-orphan')
    resume_point = db.relationship('ResumePoint', back_populates='attempt', uselist=False)
    
    def __repr__(self):
        return f'<Attempt {self.attempt_id} user={self.user_id}>'


# AttemptAnswer Model
class AttemptAnswer(db.Model):
    __tablename__ = 'attempt_answers'
    
    answer_id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.attempt_id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.question_id', ondelete='CASCADE'), nullable=False)
    selected_choice_id = db.Column(db.Integer, db.ForeignKey('choices.choice_id', ondelete='SET NULL'))
    text_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    points_earned = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempt = db.relationship('Attempt', back_populates='answers')
    question = db.relationship('QuestionBank', back_populates='attempt_answers')
    selected_choice = db.relationship('Choice')
    
    def __repr__(self):
        return f'<AttemptAnswer {self.answer_id}>'


# ResumePoint Model
class ResumePoint(db.Model):
    __tablename__ = 'resume_points'
    
    resume_id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.attempt_id', ondelete='CASCADE'), unique=True, nullable=False)
    last_question_index = db.Column(db.Integer)
    time_remaining_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempt = db.relationship('Attempt', back_populates='resume_point')
    
    def __repr__(self):
        return f'<ResumePoint attempt={self.attempt_id}>'


# Explanation Model
class Explanation(db.Model):
    __tablename__ = 'explanations'
    
    explanation_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.question_id', ondelete='CASCADE'), nullable=False)
    explanation_text = db.Column(db.Text, nullable=False)
    source = db.Column(db.Enum('AI-Generated', 'Manual', name='explanation_source_enum'), default='Manual')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('QuestionBank', back_populates='explanations')
    
    def __repr__(self):
        return f'<Explanation {self.explanation_id}>'


# Recommendation Model
class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    recommendation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recommended_quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'))
    recommended_topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id', ondelete='CASCADE'))
    reason = db.Column(db.Text)
    confidence_score = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='recommendations')
    quiz = db.relationship('Quiz')
    topic = db.relationship('Topic')
    
    def __repr__(self):
        return f'<Recommendation {self.recommendation_id}>'


# Streak Model
class Streak(db.Model):
    __tablename__ = 'streaks'
    
    streak_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='streaks')
    
    def __repr__(self):
        return f'<Streak user={self.user_id} current={self.current_streak}>'


# UserDashboardCache Model
class UserDashboardCache(db.Model):
    __tablename__ = 'user_dashboard_cache'
    
    cache_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False)
    total_quizzes_taken = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Numeric(5, 2))
    total_time_spent_minutes = db.Column(db.Integer, default=0)
    best_category = db.Column(db.String(255))
    weak_topics = db.Column(db.JSON)
    recent_activity = db.Column(db.JSON)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='dashboard_cache')
    
    def __repr__(self):
        return f'<UserDashboardCache user={self.user_id}>'


# Attachment Model
class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    attachment_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.question_id', ondelete='CASCADE'))
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('QuestionBank', back_populates='attachments')
    
    def __repr__(self):
        return f'<Attachment {self.file_name}>'


# Tag Model
class Tag(db.Model):
    __tablename__ = 'tags'
    
    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('QuestionBank', secondary='question_tags', back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.tag_name}>'


# QuestionTag Model (Association Table)
class QuestionTag(db.Model):
    __tablename__ = 'question_tags'
    
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.question_id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QuestionTag question={self.question_id} tag={self.tag_id}>'
