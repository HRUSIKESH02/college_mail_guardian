from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.db import SessionLocal
from models.models import Email, Reminder, WhitelistedSender
from gmail.service import fetch_unread_emails, mark_email_read
from ai.service import classify_email
from whatsapp.service import send_whatsapp_alert
from app.config import settings
import email.utils

def process_emails():
    db: Session = SessionLocal()
    try:
        emails = fetch_unread_emails()
        for e in emails:
            exists = db.query(Email).filter_by(gmail_message_id=e["message_id"]).first()
            if exists:
                continue

            # Check if sender matches the database whitelist or general college domains
            is_db_whitelisted = False
            matches_college_domain = False
            
            _, sender_email = email.utils.parseaddr(e["sender"])
            sender_email = sender_email.lower()
            sender_domain = sender_email.split('@')[-1] if '@' in sender_email else ""
            
            # 1. Check database whitelist
            whitelisted_senders = db.query(WhitelistedSender).all()
            if whitelisted_senders:
                for ws in whitelisted_senders:
                    val = ws.email_or_domain.strip().lower()
                    if val in sender_email:
                        is_db_whitelisted = True
                        break
            
            # 2. Check college domains in .env
            if settings.college_domains:
                allowed_domains = [d.strip().lower() for d in settings.college_domains.split(",") if d.strip()]
                if sender_domain in allowed_domains:
                    matches_college_domain = True
            else:
                matches_college_domain = True
                
            # Filter condition:
            # If the DB whitelist has entries, we allow emails that are either in the DB whitelist or match the general college domains.
            # If the DB whitelist is empty, we only allow emails that match the general college domains.
            if whitelisted_senders:
                if not (is_db_whitelisted or matches_college_domain):
                    print(f"Skipping email (not in whitelist and not in college domains): {e['sender']}")
                    mark_email_read(e["message_id"])
                    continue
            else:
                if not matches_college_domain:
                    print(f"Skipping email (not in college domains): {e['sender']}")
                    mark_email_read(e["message_id"])
                    continue
            
            ai_result = classify_email(e)
            
            if ai_result["priority"] == "IGNORE":
                mark_email_read(e["message_id"])
                continue
                
            new_email = Email(
                gmail_message_id=e["message_id"],
                sender=e["sender"],
                subject=e["subject"],
                body_snippet=e["body"],
                priority=ai_result["priority"],
                summary=ai_result["summary"],
                deadline_detected=ai_result["deadline_detected"],
                deadline_text=ai_result["deadline_text"],
                action_required=ai_result["action_required"]
            )
            db.add(new_email)
            db.commit()
            db.refresh(new_email)

            # Send WhatsApp alert if it is from a whitelisted sender OR has CRITICAL priority
            should_alert = is_db_whitelisted or ai_result["priority"] == "CRITICAL"
            
            if should_alert:
                send_whatsapp_alert(e, ai_result)
                
            # Setup reminders only for Critical and Important tasks
            if ai_result["priority"] in ["CRITICAL", "IMPORTANT"]:
                reminder = Reminder(
                    email_id=new_email.id,
                    next_reminder_at=datetime.utcnow() + timedelta(hours=6),
                    reminder_count=0
                )
                db.add(reminder)
                db.commit()
    finally:
        db.close()

def check_reminders():
    db: Session = SessionLocal()
    try:
        active_reminders = db.query(Reminder).filter(Reminder.is_active == True, Reminder.next_reminder_at <= datetime.utcnow()).all()
        
        for rem in active_reminders:
            email_data = db.query(Email).filter(Email.id == rem.email_id).first()
            if not email_data or email_data.is_acknowledged:
                rem.is_active = False
                db.commit()
                continue
                
            ai_result = {
                "summary": f"REMINDER: {email_data.summary}",
                "deadline_text": email_data.deadline_text,
                "action_required": email_data.action_required
            }
            send_whatsapp_alert({"subject": email_data.subject, "sender": email_data.sender}, ai_result)
            
            # Reschedule reminder to run again in 6 hours (repeats infinitely until acknowledged)
            rem.next_reminder_at = datetime.utcnow() + timedelta(hours=6)
            rem.reminder_count += 1
            db.commit()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_emails, 'interval', minutes=5, id='email_checker')
    scheduler.add_job(check_reminders, 'interval', minutes=15, id='reminder_checker')
    scheduler.start()