# Python Quiz Management System - Backend Setup Guide

## Prerequisites Checklist
Before proceeding, ensure you have:
- ✅ Python 3.11 or higher installed
- ✅ PostgreSQL 14+ installed and running
- ✅ Redis server installed and running
- ✅ pip and virtualenv available

## Step 1: Create Virtual Environment

```powershell
# Navigate to backend folder
cd "d:\Infosys springboard internship 6.0\intelligent-quiz-app\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and update these critical values:

```env
# Database - UPDATE THESE!
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/quiz_db

# Security - CHANGE THESE!
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# AI Keys - ADD YOUR KEYS!
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

## Step 4: Create PostgreSQL Database

```powershell
# Open PostgreSQL command line (psql)
psql -U postgres

# In psql, create database:
CREATE DATABASE quiz_db;

# Exit psql
\q
```

## Step 5: Initialize Database

```powershell
# Run database initialization script
python init_db.py
```

This will:
- Create all database tables
- Create default roles (Admin, Teacher, Student)
- Create admin user (username: admin, password: Admin@123)
- Create sample categories and topics

## Step 6: Start Redis (if not running)

```powershell
# If you have Redis installed via Chocolatey or MSI:
redis-server

# Or if using Docker:
docker run -d -p 6379:6379 redis:latest
```

## Step 7: Start Flask Server

```powershell
python run.py
```

The server should start on `http://localhost:5000`

## Step 8: Test the API

### Test health endpoint:
```powershell
curl http://localhost:5000/health
```

### Test login:
```powershell
$body = @{
    username = "admin"
    password = "Admin@123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Body $body -ContentType "application/json"
```

## Step 9: (Optional) Start Celery Worker

For async quiz generation tasks:

```powershell
# In a new terminal, activate venv and run:
celery -A app.celery worker --loglevel=info
```

## Troubleshooting

### Issue: Port 5000 already in use
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue: PostgreSQL connection refused
- Ensure PostgreSQL service is running
- Check username and password in .env
- Verify database "quiz_db" exists

### Issue: Redis connection error
- Ensure Redis server is running: `redis-cli ping` should return PONG
- Check REDIS_URL in .env

### Issue: Module not found errors
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## API Endpoints Available

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login
- POST `/api/auth/refresh` - Refresh token
- GET `/api/auth/me` - Get current user

### Categories
- GET `/api/categories` - List all categories
- POST `/api/categories` - Create category (Admin/Teacher)

### Questions
- GET `/api/questions` - List questions
- POST `/api/questions` - Create question (Admin/Teacher)
- POST `/api/questions/generate` - AI generate questions (Admin/Teacher)

## Next Steps

1. ✅ Backend is now running
2. 🔄 Set up the React frontend (see frontend folder)
3. 🚀 Start building your quiz application!

## Database Schema

The system includes 20+ tables:
- Users and Roles
- Categories, Subcategories, Topics
- Question Bank with Choices
- Quizzes and Quiz-Question mappings
- Attempts and Attempt Answers
- Streaks, Recommendations, Analytics
- Tags, Attachments, Explanations

## Default Admin Credentials

**Username:** admin  
**Password:** Admin@123  
**Role:** Admin

⚠️ **IMPORTANT:** Change the admin password immediately in production!

## Support

For issues or questions, check the main README.md in the project root.
