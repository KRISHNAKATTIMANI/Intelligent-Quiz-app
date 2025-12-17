# 🎯 Intelligent Quiz Management System

A modern, AI-powered quiz platform built with Python Flask, React, and PostgreSQL.

## ✨ Features

### 🎓 Core Features
- **Multi-role System**: Admin, Instructor, Student
- **AI Quiz Generation**: Generate quizzes from categories or uploaded materials
- **File Upload**: Extract text from PDFs, docs and auto-generate MCQs
- **Smart Question Bank**: Organized by categories → subcategories → topics
- **Resume Functionality**: Continue quizzes where you left off
- **Real-time Auto-save**: Never lose your progress

### 🤖 AI-Powered
- **LLM Integration**: GPT/Claude for intelligent quiz generation
- **Confidence Scoring**: Auto-validate generated questions
- **Content Moderation**: Profanity, PII, and hate speech detection
- **Smart Recommendations**: AI suggests topics based on performance

### 📊 Analytics & Gamification
- **Performance Tracking**: Detailed analytics by topic and difficulty
- **Streak System**: Daily activity tracking
- **Leaderboards**: Compete with peers
- **Achievement System**: Unlock badges and rewards
- **Dashboard Caching**: Fast, responsive experience

### 👥 Social Features
- **Group Quizzes**: Create and join quiz groups
- **Social Sharing**: Share results and achievements
- **Friends System**: Invite and compete with friends

### 🛡️ Security & Moderation
- **JWT Authentication**: Secure token-based auth
- **Role-based Access**: Granular permissions
- **Content Moderation**: Review and approve generated content
- **File Scanning**: Virus and malware detection
- **Rate Limiting**: API protection

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** with Flask
- **SQLAlchemy** ORM
- **PostgreSQL** database
- **Flask-JWT-Extended** for auth
- **Celery** for background tasks
- **Redis** for caching and queue
- **OpenAI/Anthropic** for LLM
- **PyPDF2/pytesseract** for OCR

### Frontend
- **React 18** with Hooks
- **TypeScript**
- **Vite** for blazing fast builds
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Query** for state management
- **Recharts** for analytics

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.11+**
- **PostgreSQL 14+**
- **Redis** (for caching)
- **Node.js 18+** (for frontend)
- **OpenAI API Key** (for quiz generation)

## 🚀 Quick Start

### 1. Database Setup

Please provide your PostgreSQL credentials:
```
Database name: quiz_db
Username: postgres
Password: your_password
Host: localhost
Port: 5432
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env with your credentials:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/quiz_db
# OPENAI_API_KEY=your-api-key
# SECRET_KEY=your-secret-key

# Initialize database
flask db upgrade

# Seed initial data
python seed.py

# Start backend
flask run
```

Backend will run on `http://localhost:5000`

### 3. Redis Setup (Required)

**Windows:**
```bash
# Download Redis from https://github.com/microsoftarchive/redis/releases
# Or use WSL/Docker
docker run -d -p 6379:6379 redis
```

**Linux/Mac:**
```bash
# Install Redis
sudo apt install redis-server  # Ubuntu
brew install redis            # Mac

# Start Redis
redis-server
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env
copy .env.example .env

# Start frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

### 5. Celery Worker (Optional - for async tasks)

```bash
cd backend
celery -A app.celery worker --loglevel=info
```

## 📁 Project Structure

```
intelligent-quiz-app/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # API blueprints
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Helper functions
│   │   ├── ai/              # LLM integration
│   │   ├── middleware/      # Auth & validation
│   │   └── __init__.py      # App factory
│   ├── migrations/          # Database migrations
│   ├── requirements.txt
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API services
│   │   ├── store/           # State management
│   │   └── utils/           # Helper functions
│   └── package.json
└── README.md
```

## 🎯 User Journeys

### Student Journey
1. Sign up / Login
2. Browse categories or upload study material
3. Configure quiz (difficulty, question count)
4. Take quiz with timer
5. View results and explanations
6. Get AI recommendations
7. Track streaks and progress

### Instructor Journey
1. Login with instructor role
2. Create custom quizzes
3. Add questions to question bank
4. Review AI-generated questions
5. Manage categories and topics
6. View student analytics

### Admin Journey
1. User management
2. Content moderation
3. System configuration
4. Analytics and reports

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Quiz Generation
- `POST /api/quiz/generate` - Generate quiz from category
- `POST /api/quiz/from-file` - Generate from uploaded file
- `GET /api/quiz/:id` - Get quiz details
- `POST /api/quiz/:id/start` - Start attempt

### Attempts
- `POST /api/attempt/:id/answer` - Save answer
- `POST /api/attempt/:id/submit` - Submit quiz
- `GET /api/attempt/:id/review` - Review attempt

### Categories
- `GET /api/categories` - List categories
- `GET /api/categories/:id/topics` - Get topics

### Dashboard
- `GET /api/dashboard` - User dashboard data
- `GET /api/dashboard/streaks` - Streak information
- `GET /api/dashboard/leaderboard` - Leaderboard

## 🤖 AI Integration

The app uses LLM for:

1. **Quiz Generation**: Generate questions from category/topic
2. **File Processing**: Extract and generate MCQs from documents
3. **Question Validation**: Check quality and correctness
4. **Recommendations**: Suggest next topics
5. **Explanation Generation**: Create detailed explanations

### Prompt Template Example
```python
Generate 10 multiple choice questions about {topic}.
Format: JSON array with question_text, options (4 choices), 
correct_index, explanation, difficulty.
```

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- SQL injection prevention
- XSS protection
- CSRF tokens
- File upload validation
- Rate limiting
- Content moderation

## 📊 Caching Strategy

- Redis for session storage
- Question bank caching
- Dashboard data caching (5 min TTL)
- LLM response caching
- Static asset caching

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 🚀 Deployment

### Backend (Railway/Render/Heroku)
1. Push to GitHub
2. Connect to hosting platform
3. Set environment variables
4. Deploy

### Frontend (Vercel/Netlify)
1. Push to GitHub
2. Connect to Vercel/Netlify
3. Configure build settings
4. Deploy

## 📈 Roadmap

- [x] Core quiz functionality
- [x] AI quiz generation
- [x] File upload & OCR
- [x] Analytics & streaks
- [ ] Mobile app (React Native)
- [ ] Offline mode
- [ ] Voice-based quizzes
- [ ] Video content support
- [ ] Advanced AI tutoring

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md

## 📄 License

MIT License - see LICENSE file

## 🆘 Support

For issues: create an issue on GitHub
For questions: contact@quizapp.com

---

Built with ❤️ using Python, React, and AI
