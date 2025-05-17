import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_email(from_email, to_email, subject, body):
    from_password = os.getenv("EMAIL_PASSWORD")

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

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
    from_email = input("Enter your email address: ").strip()
    to_email = input("Enter recipient's email address: ").strip()

    # Set these dynamically based on your condition
    is_selected = True  # Change this as per your logic

    if is_selected:
        subject = "Congratulations! You have been selected"
        body = "We are pleased to inform you that you have been selected for the role."
    else:
        subject = "Application Update"
        body = "Thank you for applying. Unfortunately, you have not been selected at this time."

    send_email(from_email, to_email, subject, body)
