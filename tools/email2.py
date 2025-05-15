import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
from dotenv import load_dotenv
import os

load_dotenv()

def send_email():
    from_email = input("Enter your email address: ").strip()
    from_password = os.getenv("EMAIL_PASSWORD")
    """from_password = getpass.getpass("Enter your email password (input hidden): ").strip()"""
    to_email = input("Enter recipient's email address: ").strip()
    subject = input("Enter subject of the email: ").strip()
    body = input("Enter body of the email: ").strip()

    smtp_server = input("Enter SMTP server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
    smtp_port_input = input("Enter SMTP port (default: 587): ").strip()
    smtp_port = int(smtp_port_input) if smtp_port_input else 587

    # Create message
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print(f"\n✅ Email sent successfully to {to_email}.")
    except Exception as e:
        print(f"\n❌ Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
