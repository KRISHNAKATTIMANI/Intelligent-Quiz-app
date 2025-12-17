"""
Add timer and instructions columns to quizzes table
"""
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    try:
        print("Adding timer_option, per_question_time, and instructions columns to quizzes table...")
        
        # Add columns using raw SQL
        db.session.execute(db.text("""
            ALTER TABLE quizzes 
            ADD COLUMN IF NOT EXISTS timer_option VARCHAR(10),
            ADD COLUMN IF NOT EXISTS per_question_time INTEGER,
            ADD COLUMN IF NOT EXISTS instructions TEXT;
        """))
        
        db.session.commit()
        print("✓ Columns added successfully!")
        
        # Verify columns were added
        result = db.session.execute(db.text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'quizzes' 
            AND column_name IN ('timer_option', 'per_question_time', 'instructions');
        """))
        
        columns = [row[0] for row in result]
        print(f"\n✓ Verified columns exist: {', '.join(columns)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error: {str(e)}")
