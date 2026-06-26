from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from database.db import Base
from datetime import datetime

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    gmail_message_id = Column(String, unique=True, index=True)
    sender = Column(String)
    subject = Column(String)
    body_snippet = Column(Text)
    priority = Column(String)
    summary = Column(Text)
    deadline_detected = Column(Boolean, default=False)
    deadline_text = Column(String, nullable=True)
    action_required = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer)
    next_reminder_at = Column(DateTime)
    reminder_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class WhitelistedSender(Base):
    __tablename__ = "whitelisted_senders"
    id = Column(Integer, primary_key=True, index=True)
    email_or_domain = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)