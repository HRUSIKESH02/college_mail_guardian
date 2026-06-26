import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from models.models import Email, Reminder

def clear_database():
    print("Clearing all emails and reminders from the database...")
    db = SessionLocal()
    try:
        # Delete all records from Email and Reminder tables
        deleted_reminders = db.query(Reminder).delete()
        deleted_emails = db.query(Email).delete()
        db.commit()
        print(f"[OK] Database cleared! Deleted {deleted_emails} emails and {deleted_reminders} reminders.")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] Error clearing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_database()
