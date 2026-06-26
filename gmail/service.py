import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import settings
import base64
import email
from email.header import decode_header

def decode_mime_header(header_value):
    if not header_value:
        return ""
    try:
        decoded_parts = decode_header(header_value)
        header_text = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    header_text.append(part.decode(encoding or 'utf-8', errors='replace'))
                except Exception:
                    header_text.append(part.decode('utf-8', errors='replace'))
            else:
                header_text.append(str(part))
        return "".join(header_text)
    except Exception:
        return header_value

def get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=settings.gmail_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)

def fetch_unread_emails():
    service = get_gmail_service()
    try:
        results = service.users().messages().list(userId="me", q="is:unread", maxResults=10).execute()
        messages = results.get("messages", [])
        
        emails_data = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="raw").execute()
            
            # Filter out old emails based on internalDate
            internal_date_ms = int(msg_data.get("internalDate", 0))
            if internal_date_ms:
                from datetime import datetime, timezone
                msg_date = datetime.fromtimestamp(internal_date_ms / 1000.0, tz=timezone.utc)
                try:
                    cutoff = datetime.fromisoformat(settings.start_time.replace("Z", "+00:00"))
                except Exception:
                    cutoff = datetime(2026, 6, 26, 9, 0, 0, tzinfo=timezone.utc)
                
                if msg_date < cutoff:
                    print(f"Skipping old email (received {msg_date} before cutoff {cutoff})")
                    # Mark as read in Gmail so it doesn't get fetched again
                    service.users().messages().modify(userId="me", id=msg["id"], body={"removeLabelIds": ["UNREAD"]}).execute()
                    continue
            
            mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(msg_data["raw"]))
            
            sender = decode_mime_header(mime_msg["From"])
            subject = decode_mime_header(mime_msg["Subject"])
            body = ""
            if mime_msg.is_multipart():
                for part in mime_msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = mime_msg.get_payload(decode=True).decode()

            emails_data.append({
                "message_id": msg["id"],
                "sender": sender,
                "subject": subject,
                "body": body[:2000]
            })
        return emails_data
    except Exception as e:
        print(f"Gmail API Error: {e}")
        return []

def mark_email_read(message_id):
    service = get_gmail_service()
    service.users().messages().modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}).execute()