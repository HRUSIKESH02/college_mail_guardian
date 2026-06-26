from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database.db import get_db
from models.models import Email, Reminder, WhitelistedSender
from datetime import datetime, timedelta
from jinja2 import Template
import os

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, filter: str = None, db: Session = Depends(get_db)):
    query = db.query(Email).order_by(Email.created_at.desc())
    if filter:
        query = query.filter(Email.priority == filter)
    emails = query.all()
    
    # Calculate statistics for the dashboard
    total_count = db.query(Email).count()
    critical_count = db.query(Email).filter(Email.priority == 'CRITICAL').count()
    important_count = db.query(Email).filter(Email.priority == 'IMPORTANT').count()
    action_required_count = db.query(Email).filter(Email.action_required == True).count()
    active_reminders_count = db.query(Reminder).filter(Reminder.is_active == True).count()
    
    stats = {
        "total": total_count,
        "critical": critical_count,
        "important": important_count,
        "action_required": action_required_count,
        "active_reminders": active_reminders_count
    }
    
    whitelisted_senders = db.query(WhitelistedSender).order_by(WhitelistedSender.created_at.desc()).all()
    
    template_path = os.path.join(os.path.dirname(__file__), "templates/index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())
    
    return template.render(emails=emails, filter=filter, stats=stats, whitelisted_senders=whitelisted_senders)

@router.post("/api/acknowledge/{email_id}")
def acknowledge_email(email_id: int, action: str = Form(...), db: Session = Depends(get_db)):
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        return RedirectResponse("/", status_code=302)
        
    if action in ["done", "read"]:
        email.is_acknowledged = True
        db.query(Reminder).filter(Reminder.email_id == email_id).update({"is_active": False})
        
    elif action == "snooze":
        reminder = db.query(Reminder).filter(Reminder.email_id == email_id, Reminder.is_active == True).first()
        if reminder:
            reminder.next_reminder_at = datetime.utcnow() + timedelta(hours=6)
        else:
            db.add(Reminder(email_id=email_id, next_reminder_at=datetime.utcnow() + timedelta(hours=6), reminder_count=0))
            
    db.commit()
    return RedirectResponse("/", status_code=302)

@router.post("/api/whitelist/add")
def add_whitelisted_sender(email_or_domain: str = Form(...), db: Session = Depends(get_db)):
    email_or_domain = email_or_domain.strip().lower()
    if email_or_domain:
        exists = db.query(WhitelistedSender).filter_by(email_or_domain=email_or_domain).first()
        if not exists:
            db.add(WhitelistedSender(email_or_domain=email_or_domain))
            db.commit()
    return RedirectResponse("/", status_code=302)

@router.post("/api/whitelist/delete/{sender_id}")
def delete_whitelisted_sender(sender_id: int, db: Session = Depends(get_db)):
    db.query(WhitelistedSender).filter_by(id=sender_id).delete()
    db.commit()
    return RedirectResponse("/", status_code=302)

@router.post("/api/check-emails")
def check_emails_now():
    from scheduler.tasks import process_emails
    process_emails()
    return RedirectResponse("/", status_code=302)