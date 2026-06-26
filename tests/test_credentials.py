import sys
import os

# Add parent directory to sys.path to allow imports from app, gmail, etc.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from twilio.rest import Client

def test_gemini():
    print("\n--- Testing Gemini API Key (google-genai SDK) ---")
    try:
        # Initialize the new Google GenAI client
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Hello! Say 'Gemini is configured successfully!' in English."
        )
        print(f"[OK] Gemini API Success! Response:\n{response.text.strip()}")
        return True
    except Exception as e:
        print(f"[FAIL] Gemini API Error: {e}")
        return False

def test_gmail():
    print("\n--- Testing Gmail OAuth Credentials ---")
    try:
        creds = Credentials(
            token=None,
            refresh_token=settings.gmail_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.gmail_client_id,
            client_secret=settings.gmail_client_secret,
            scopes=["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]
        )
        print("Attempting credential refresh...")
        creds.refresh(Request())
        print("Credential refreshed successfully.")
        
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        print(f"[OK] Gmail API Success! Connected account: {profile.get('emailAddress')}")
        return True
    except Exception as e:
        print(f"[FAIL] Gmail API Error: {e}")
        return False

def test_twilio():
    print("\n--- Testing Twilio Credentials ---")
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        account = client.api.v2010.accounts(settings.twilio_account_sid).fetch()
        print(f"[OK] Twilio Auth Success! Account Name: {account.friendly_name} (Status: {account.status})")
        
        print("Sending WhatsApp test alert...")
        message = client.messages.create(
            body="🚨 *COLLEGE MAIL GUARDIAN TEST ALERT*\n\nTwilio WhatsApp integration is working successfully!",
            from_=settings.twilio_whatsapp_number,
            to=settings.your_whatsapp_number
        )
        print(f"[OK] WhatsApp sent successfully! Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[FAIL] Twilio Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting integration tests...")
    print(f"USER_EMAIL: {settings.user_email}")
    print(f"YOUR_WHATSAPP_NUMBER: {settings.your_whatsapp_number}")
    
    gemini_ok = test_gemini()
    gmail_ok = test_gmail()
    twilio_ok = test_twilio()
    
    print("\n==============================")
    print("TEST SUMMARY:")
    print(f"Gemini API: {'PASS' if gemini_ok else 'FAIL'}")
    print(f"Gmail API:  {'PASS' if gmail_ok else 'FAIL'}")
    print(f"Twilio API: {'PASS' if twilio_ok else 'FAIL'}")
    print("==============================")
