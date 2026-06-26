from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    gmail_client_id: str = os.getenv("GMAIL_CLIENT_ID")
    gmail_client_secret: str = os.getenv("GMAIL_CLIENT_SECRET")
    gmail_refresh_token: str = os.getenv("GMAIL_REFRESH_TOKEN")
    user_email: str = os.getenv("USER_EMAIL")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_whatsapp_number: str = os.getenv("TWILIO_WHATSAPP_NUMBER")
    your_whatsapp_number: str = os.getenv("YOUR_WHATSAPP_NUMBER")
    college_domains: str = os.getenv("COLLEGE_DOMAINS", "")
    start_time: str = os.getenv("START_TIME", "2026-06-26T09:00:00Z")

settings = Settings()