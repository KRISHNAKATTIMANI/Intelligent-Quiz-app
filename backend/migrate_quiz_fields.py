"""Add timer and instructions fields to quizzes table"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Add new columns to quizzes table
        with db.engine.connect() as conn:
            # Check if columns exist before adding
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'quizzes' 
                AND column_name IN ('timer_option', 'per_question_time', 'instructions')
            """))
            
            existing_columns = {row[0] for row in result}
            
            if 'timer_option' not in existing_columns:
                conn.execute(text("ALTER TABLE quizzes ADD COLUMN timer_option VARCHAR(10)"))
                print("Added timer_option column")
            
            if 'per_question_time' not in existing_columns:
                conn.execute(text("ALTER TABLE quizzes ADD COLUMN per_question_time INTEGER"))
                print("Added per_question_time column")
            
            if 'instructions' not in existing_columns:
                conn.execute(text("ALTER TABLE quizzes ADD COLUMN instructions TEXT"))
                print("Added instructions column")
            
            conn.commit()
            print("\nMigration completed successfully!")
            
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        db.session.rollback()
