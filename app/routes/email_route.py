import logging
from flask import Blueprint, request, jsonify
from app.tools.email2 import send_email
from app.config import CONFIG

logger = logging.getLogger(__name__)

email_bp = Blueprint('email', __name__)
THRESHOLD = CONFIG["threshold"]

@email_bp.route('/send-mails', methods=['POST'])
def send_emails():
    logger.info("Enter into send_email end point...")
    data = request.get_json()
    matches = data.get("matches", [])
    from_email = data.get("from_email")
    proceed = data.get("proceed", False)  # Must be true to send
    
    logger.info(f"matches as {matches},email as {from_email} and process equal {proceed}")

    if not matches or not from_email:
        return jsonify({"error": "Missing match data or from_email"}), 400
    logger.info('matches are present')

    if not proceed:
        return jsonify({"message": "Mail sending cancelled by user."}), 200
    logger.info('process is True, mail should be sent')

    for match in matches:
        email = match.get("email")
        job = match.get("job")
        score = match.get("score", 0)
        logger.info('logging inside the loop with match : {match}')
        if not email:
            logger.error("Email not found for match :{match}. continue the process...")
            continue

        if score >= THRESHOLD:
            subject = CONFIG["email_templates"]["shortlist"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["shortlist"]["body"].format(job=job)
        else:
            subject = CONFIG["email_templates"]["rejection"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["rejection"]["body"].format(job=job)

        send_email(from_email, email, subject, body)

    return jsonify({"message": "Emails sent successfully."}), 200