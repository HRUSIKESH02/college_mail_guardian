import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gmail.service import get_gmail_service

def check_all_unread():
    print("Connecting to Gmail API...")
    try:
        service = get_gmail_service()
        # Query for all unread messages anywhere (including spam/categories just in case)
        results = service.users().messages().list(userId="me", q="is:unread", maxResults=20).execute()
        messages = results.get("messages", [])
        
        print(f"\nFound {len(messages)} unread email(s) in your account:")
        print("-" * 60)
        
        for idx, msg in enumerate(messages):
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            
            sender = "Unknown"
            subject = "No Subject"
            date = "Unknown"
            
            for h in headers:
                if h["name"] == "From":
                    sender = h["value"]
                elif h["name"] == "Subject":
                    subject = h["value"]
                elif h["name"] == "Date":
                    date = h["value"]
                    
            # Print safely to console by encoding/decoding or setting sys.stdout to utf-8 encoding
            safe_sender = sender.encode('utf-8', errors='replace').decode(sys.stdout.encoding, errors='replace')
            safe_subject = subject.encode('utf-8', errors='replace').decode(sys.stdout.encoding, errors='replace')
            print(f"{idx+1}. From: {safe_sender}")
            print(f"   Subject: {safe_subject}")
            print(f"   Date: {date}")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error querying Gmail: {e}")

if __name__ == "__main__":
    check_all_unread()
