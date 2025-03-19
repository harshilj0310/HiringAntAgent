import os
from langchain_google_community.gmail.send_message import GmailSendMessage
from langchain_google_community.gmail.utils import (
    get_gmail_credentials,
    build_resource_service,
)

# Define scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Get the correct path for credentials.json
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Move up one directory
credentials_path = os.path.join(script_dir, "tools", "credentials.json")
token_path = os.path.join(script_dir, "tools", "token.json")

# Authenticate using credentials
credentials = get_gmail_credentials(
    token_file=token_path,
    scopes=SCOPES,
    client_secrets_file=credentials_path,
)

# Build Gmail API service
api_resource = build_resource_service(credentials=credentials)

# Initialize LangChain Gmail tool
send_email_tool = GmailSendMessage(api_resource=api_resource)

# Function to send an email
def send_email(to, subject, message):
    email_data = {
        "to": to,
        "subject": subject,
        "body": {"content": message, "type": "plain"},  # Fix body format
    }
    send_email_tool.invoke(email_data)
    print("Email sent successfully!")



# Example Usage
send_email("22b0666@iitb.ac.in", "Test Subject", "Hello, this is a test email.")
