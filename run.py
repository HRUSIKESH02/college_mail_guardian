import sys
import os
import uvicorn

# Ensure the current directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("            COLLEGE MAIL GUARDIAN STARTING           ")
    print("=" * 60)
    print("Dashboard URL:        http://localhost:8000")
    print("Database:             SQLite (mail_guardian.db)")
    print("Email Polling Worker: APScheduler (every 5 minutes)")
    print("Press Ctrl+C to shutdown.")
    print("=" * 60)
    
    # Run uvicorn server
    uvicorn.run("dashboard.app:app", host="0.0.0.0", port=8000, reload=False)
