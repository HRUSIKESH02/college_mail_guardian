import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import settings
import base64
import email

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
            mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(msg_data["raw"]))
            
            sender = mime_msg["From"]
            subject = mime_msg["Subject"]
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