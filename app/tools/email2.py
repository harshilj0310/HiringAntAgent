import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def send_email(from_email, to_email, subject, body):
    from_password = os.getenv("EMAIL_PASSWORD")

    if not from_password:
        logging.error("EMAIL_PASSWORD not found in environment variables.")
        return

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = None
    try:
        logging.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        logging.info(f"Email sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError:
        logging.exception("Authentication failed: Check email credentials.")
    except smtplib.SMTPException as smtp_err:
        logging.exception(f"SMTP error occurred: {smtp_err}")
    except Exception as e:
        logging.exception(f"Unexpected error occurred while sending email: {e}")
    finally:
        if server:
            try:
                server.quit()
                logging.info("SMTP server connection closed.")
            except Exception as e:
                logging.warning(f"Failed to close SMTP server connection: {e}")
