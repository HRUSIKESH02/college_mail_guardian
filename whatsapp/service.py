from twilio.rest import Client
from app.config import settings

def send_whatsapp_alert(email_data, ai_result):
    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
        deadline_str = ai_result.get("deadline_text") or "None specified"
        action_str = "Yes" if ai_result.get("action_required") else "No"
        
        message = f"""🚨 *COLLEGE ALERT*

*Subject:* {email_data['subject']}

*Summary:*
{ai_result['summary']}

*Deadline:*
{deadline_str}

*Action Required:*
{action_str}

*Sender:*
{email_data['sender']}"""

        msg = client.messages.create(
            body=message,
            from_=settings.twilio_whatsapp_number,
            to=settings.your_whatsapp_number
        )
        print(f"WhatsApp sent: {msg.sid}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")