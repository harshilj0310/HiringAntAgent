import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv(override=True)

logger = logging.getLogger(__name__)

def send_email(from_email, to_email, subject, body) -> bool:
    logger.info("Entering the send email function")
    from_password = os.getenv("EMAIL_PASSWORD")

    if not from_password:
        logger.error("EMAIL_PASSWORD not found in environment variables.")
        return False  # Return failure

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    logger.info(f"this is from email :{from_email} and this is pass :{from_password}")

    server = None
    try:
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        logger.info(f"Email sent successfully to {to_email}")
        return True 
    except smtplib.SMTPAuthenticationError:
        logger.exception("Authentication failed: Check email credentials.")
    except smtplib.SMTPException as smtp_err:
        logger.exception(f"SMTP error occurred: {smtp_err}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred while sending email: {e}")
    finally:
        if server:
            try:
                server.quit()
                logger.info("SMTP server connection closed.")
            except Exception as e:
                logger.warning(f"Failed to close SMTP server connection: {e}")
    return False 
