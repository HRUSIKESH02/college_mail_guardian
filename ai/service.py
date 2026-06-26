from google import genai
import json
from app.config import settings

def classify_email(email_data):
    prompt = f"""You are a college email classifier. Analyze the email and return JSON.
    Email From: {email_data['sender']}
    Subject: {email_data['subject']}
    Body: {email_data['body']}
    
    Return ONLY valid JSON in this exact format:
    {{
        "priority": "CRITICAL|IMPORTANT|NORMAL|IGNORE",
        "reason": "Brief reason",
        "deadline_detected": true/false,
        "deadline_text": "Extracted deadline or null",
        "action_required": true/false,
        "summary": "Short summary in simple language"
    }}"""
    
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        json_str = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"AI Classification Error: {e}")
        return {"priority": "NORMAL", "reason": "Parsing error", "deadline_detected": False, "deadline_text": None, "action_required": False, "summary": "Could not summarize."}