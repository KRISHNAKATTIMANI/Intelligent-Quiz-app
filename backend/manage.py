"""
Management commands for database maintenance and cleanup tasks
Run with: python manage.py <command>
"""
import sys
from app import create_app
from app.utils.cleanup import cleanup_old_ai_questions, cleanup_orphaned_choices, get_cleanup_stats


def run_cleanup():
    """Run all cleanup tasks"""
    print("🧹 Starting database cleanup...")
    print("-" * 50)
    
    # Cleanup old AI questions
    print("\n1. Cleaning up old AI-generated questions...")
    result = cleanup_old_ai_questions()
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Cleanup orphaned choices
    print("\n2. Cleaning up orphaned choices...")
    result = cleanup_orphaned_choices()
    if result['success']:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("Cleanup complete! ✨")


def show_stats():
    """Show cleanup statistics without performing cleanup"""
    print("📊 Database Cleanup Statistics")
    print("=" * 50)
    
    result = get_cleanup_stats()
    
    if result['success']:
        print(f"\nRetention Policy: {result['retention_days']} days")
        print(f"Cutoff Date: {result['cutoff_date']}")
        print(f"\nAI-Generated Questions:")
        print(f"  - Total: {result['total_ai_questions']}")
        print(f"  - Last 24 hours: {result['ai_questions_last_24h']}")
        print(f"  - Last 7 days: {result['ai_questions_last_7d']}")
        print(f"  - Eligible for cleanup: {result['cleanup_eligible']}")
        
        if result['cleanup_eligible'] > 0:
            print(f"\n⚠️  {result['cleanup_eligible']} questions can be deleted")
            print("   Run 'python manage.py cleanup' to perform cleanup")
        else:
            print("\n✓ No cleanup needed at this time")
    else:
        print(f"\n✗ Error: {result['error']}")
    
    print("=" * 50)


def show_help():
    """Show available commands"""
    print("Available commands:")
    print("  cleanup  - Run database cleanup (delete old AI questions)")
    print("  stats    - Show cleanup statistics")
    print("  help     - Show this help message")
    print("\nUsage: python manage.py <command>")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) < 2:
            print("Error: No command specified")
            show_help()
            sys.exit(1)
        
        command = sys.argv[1].lower()
        
        if command == 'cleanup':
            run_cleanup()
        elif command == 'stats':
            show_stats()
        elif command == 'help':
            show_help()
        else:
            print(f"Error: Unknown command '{command}'")
            show_help()
            sys.exit(1)
