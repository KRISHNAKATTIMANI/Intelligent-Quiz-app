# AI Question Generation & Auto-Cleanup

## Overview
The application now generates quiz questions dynamically using OpenAI's GPT-3.5-turbo model. AI-generated questions are automatically stored in the database and deleted after 7 days to maintain database health.

## Features

### 1. Dynamic AI Question Generation
- Questions are generated on-demand based on user-selected topics
- Uses OpenAI GPT-3.5-turbo for high-quality question generation
- Generates multiple-choice questions with 4 options
- Includes explanations for correct answers
- Questions are immediately available for quizzes

### 2. Automatic 7-Day Cleanup
- AI-generated questions are automatically marked with a timestamp
- Questions older than 7 days are eligible for deletion
- Cleanup protects questions that are:
  - Currently in active quizzes
  - Have existing attempt history
- Safe deletion ensures no data loss for user progress

### 3. Manual Cleanup Management
Run cleanup tasks manually using:
```bash
# Show cleanup statistics
python manage.py stats

# Run cleanup (delete old AI questions)
python manage.py cleanup

# Show help
python manage.py help
```

### 4. Admin API Endpoints
Admin users can manage cleanup via API:
- `POST /api/admin/cleanup/run` - Run cleanup tasks
- `GET /api/admin/cleanup/stats` - Get cleanup statistics
- `GET /api/admin/health` - Health check with stats

## Configuration

### Environment Variables (.env)
```env
# OpenAI API Key - DO NOT COMMIT TO GIT
OPENAI_API_KEY=sk-proj-your-key-here

# Model selection (default: gpt-3.5-turbo)
LLM_MODEL=gpt-3.5-turbo

# Retention period for AI-generated questions (default: 7 days)
AI_QUESTION_RETENTION_DAYS=7
```

### Important Security Notes
⚠️ **NEVER commit your OpenAI API key to GitHub**
- The `.env` file is already in `.gitignore`
- API keys are loaded from environment variables only
- Keep your API key secret and secure

## Usage

### Generating Quizzes with AI
1. Select a category and subcategory
2. Choose number of questions
3. Select difficulty level (EASY, MEDIUM, HARD, ADVANCE)
4. Configure timer options
5. Click "Start Quiz"

The system will:
- Check for existing questions in the database
- Generate new questions using AI if needed
- Store generated questions for 7 days
- Create the quiz immediately

### Monitoring Question Storage
Check cleanup statistics:
```bash
python manage.py stats
```

Output example:
```
📊 Database Cleanup Statistics
==================================================

Retention Policy: 7 days
Cutoff Date: 2025-12-09T10:30:00

AI-Generated Questions:
  - Total: 150
  - Last 24 hours: 45
  - Last 7 days: 120
  - Eligible for cleanup: 30

⚠️  30 questions can be deleted
   Run 'python manage.py cleanup' to perform cleanup
==================================================
```

### Running Cleanup
```bash
python manage.py cleanup
```

Output example:
```
🧹 Starting database cleanup...
--------------------------------------------------

1. Cleaning up old AI-generated questions...
   ✓ Deleted 25 AI-generated questions older than 7 days. Skipped 5 questions still in use.

2. Cleaning up orphaned choices...
   ✓ Deleted 0 orphaned choices

==================================================
Cleanup complete! ✨
```

## Automated Cleanup (Optional)

### Windows Task Scheduler
Create a scheduled task to run cleanup daily:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 2 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py cleanup`
7. Start in: `D:\path\to\intelligent-quiz-app\backend`

### Linux/Mac Cron Job
Add to crontab (`crontab -e`):
```bash
# Run cleanup daily at 2 AM
0 2 * * * cd /path/to/intelligent-quiz-app/backend && python manage.py cleanup
```

## API Reference

### Generate Quiz with AI
```http
POST /api/quiz/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "subcategory_id": 1,
  "num_questions": 10,
  "difficulty_level": "MEDIUM",
  "timer_option": "whole",
  "total_time": 30,
  "instructions": "Read carefully",
  "use_ai": true
}
```

Response:
```json
{
  "message": "Quiz generated successfully",
  "quiz_id": 123,
  "questions": [...],
  "ai_generated": true
}
```

### Admin: Get Cleanup Stats
```http
GET /api/admin/cleanup/stats
Authorization: Bearer <admin-token>
```

### Admin: Run Cleanup
```http
POST /api/admin/cleanup/run
Authorization: Bearer <admin-token>
```

## Question Storage Model

AI-generated questions are stored with:
- `source`: "AI-Generated"
- `created_at`: Timestamp for age calculation
- `confidence_score`: AI confidence (0.0-1.0)
- `is_verified`: Auto-verified if confidence > 0.7

## Troubleshooting

### "Not enough questions available"
This error occurs when:
- Selected subcategory has no questions
- Not enough questions for requested number
- AI generation is disabled

**Solution**:
- Ensure `use_ai: true` in request
- Check OpenAI API key is configured
- Verify API key has credits/quota
- Try a different subcategory

### API Key Errors
```
OpenAI API error: Incorrect API key provided
```

**Solution**:
1. Check `.env` file has correct API key
2. Verify no extra spaces in key
3. Restart the server after updating `.env`

### Cleanup Not Working
**Solution**:
1. Check retention days configuration
2. Verify questions are older than retention period
3. Check if questions are in use (won't be deleted)

## Best Practices

1. **Regular Cleanup**: Run cleanup weekly to maintain database health
2. **Monitor Stats**: Check stats before cleanup to understand impact
3. **API Key Security**: Never commit API keys, use environment variables
4. **Backup First**: Backup database before manual cleanup operations
5. **Review Logs**: Check application logs for cleanup results

## Database Schema Updates

New fields added to `question_bank` table:
- Already has `created_at` timestamp
- Already has `source` enum ('AI-Generated')
- Already has `confidence_score`

No migration needed - schema already supports the feature!

## Cost Management

OpenAI API costs:
- GPT-3.5-turbo: ~$0.0015 per request (varies by token count)
- 10 questions ≈ 1000-2000 tokens
- Cost per 10 questions: ~$0.001 - $0.003

To reduce costs:
- Enable cleanup to remove unused questions
- Use existing questions when available
- Set appropriate retention period
- Monitor API usage in OpenAI dashboard
