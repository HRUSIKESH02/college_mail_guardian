import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from models.models import Email

def print_all_db_emails():
    db = SessionLocal()
    try:
        emails = db.query(Email).all()
        print(f"Total emails stored in database: {len(emails)}")
        print("-" * 60)
        for idx, email in enumerate(emails):
            print(f"{idx+1}. ID: {email.id}")
            print(f"   Gmail ID: {email.gmail_message_id}")
            print(f"   From: {email.sender}")
            print(f"   Subject: {email.subject}")
            print(f"   Priority: {email.priority}")
            print(f"   Acknowledged: {email.is_acknowledged}")
            print("-" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    print_all_db_emails()
