from flask import Blueprint, request, jsonify
from app.utils import process_matching
import os
import tempfile
from tools.email2 import send_email
import yaml,logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)

THRESHOLD = CONFIG["threshold"]


@main_bp.route('/match', methods=['POST'])
def match_endpoint():
    resumes = request.files.getlist('resumes')
    jds = request.files.getlist('jds')

    if not resumes or not jds:
        return jsonify({"error": "Both resumes and JDs must be uploaded."}), 400

    with tempfile.TemporaryDirectory() as tempdir:
        resume_paths, jd_paths = [], []

        for file in resumes:
            path = os.path.join(tempdir, file.filename)
            file.save(path)
            resume_paths.append(path)

        for file in jds:
            path = os.path.join(tempdir, file.filename)
            file.save(path)
            jd_paths.append(path)

        try:
            matches = process_matching(resume_paths, jd_paths)
            return jsonify(matches), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@main_bp.route('/send-mails', methods=['POST'])
def send_emails():
    data = request.get_json()
    matches = data.get("matches", [])
    from_email = data.get("from_email")
    proceed = data.get("proceed", False)  # Must be true to send
    
    logger.info(f"so here we have matches as {matches},email as {from_email} and process equal {proceed}")

    if not matches or not from_email:
        return jsonify({"error": "Missing match data or from_email"}), 400
    logger.info('matches are present')

    if not proceed:
        return jsonify({"message": "Mail sending cancelled by user."}), 200
    logger.info('process is True so mail should be sent')

    for match in matches:
        email = match.get("email")
        job = match.get("job")
        score = match.get("score", 0)
        logger.info('logging inside the loop with match : {match}')
        if not email:
            continue

        if score >= THRESHOLD:
            subject = CONFIG["email_templates"]["shortlist"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["shortlist"]["body"].format(job=job)
        else:
            subject = CONFIG["email_templates"]["rejection"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["rejection"]["body"].format(job=job)

        send_email(from_email, email, subject, body)

    return jsonify({"message": "Emails sent successfully."}), 200
