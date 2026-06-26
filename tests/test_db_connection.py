import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, SessionLocal
from models.models import Email

def main():
    print("Testing Supabase DB Connection and Initialization...")
    try:
        init_db()
        print("[OK] Database tables created/checked successfully!")
        
        db = SessionLocal()
        count = db.query(Email).count()
        print(f"[OK] Connection verified. Found {count} emails in the database.")
        db.close()
    except Exception as e:
        print(f"[FAIL] Database Connection failed: {e}")

if __name__ == "__main__":
    main()
