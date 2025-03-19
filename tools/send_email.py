import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Define the scope
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the correct path to credentials.json and token.json
credentials_path = os.path.join(script_dir, "credentials.json")
token_path = os.path.join(script_dir, "token.json")

def authenticate_gmail():
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


# Send email function
def send_email(to, subject, message):
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)
    
    msg = MIMEText(message)
    msg["to"] = to
    msg["subject"] = subject
    encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    raw = {"raw": encoded_message}
    service.users().messages().send(userId="me", body=raw).execute()
    print("Email sent successfully!")

# Example usage
if __name__ == "__main__":

    send_email("22b0666@iitb.ac.in", "Test Subject", "Hello, this is a test email.")
