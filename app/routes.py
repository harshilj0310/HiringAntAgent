from flask import Blueprint, request, jsonify
from app.utils import process_matching
import os
import tempfile
from tools.email2 import send_email
import yaml,logging
from werkzeug.utils import secure_filename
from datetime import datetime
from app.db import resumes_collection
from app.db import jds_collection

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)

THRESHOLD = CONFIG["threshold"]


@main_bp.route('/match', methods=['POST'])
def match_endpoint():
    logger.info("Enter into match_endpoint")
    resumes = request.files.getlist('resumes')
    jds = request.files.getlist('jds')

    if not resumes or not jds:
        logger.error("Either resumes or JDs is not uploaded.")
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
            logger.info("Calling process_matching function")
            matches = process_matching(resume_paths, jd_paths)
            return jsonify(matches), 200
        except Exception as e:
            logger.error("Error in process_matching function call")
            return jsonify({"error": str(e)}), 500


@main_bp.route('/send-mails', methods=['POST'])
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


@main_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files.get('resume')
    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    # Validate file extension
    allowed_exts = CONFIG.get("allowed_extensions_resume", [])
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        return jsonify({"error": "Invalid file type"}), 400

    # Secure and save the file
    filename = secure_filename(file.filename)
    upload_folder = CONFIG.get("resume_upload_folder", "uploads/resume")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # Extract metadata
    metadata = {
        "filename": filename,
        "filepath": file_path,
        "uploaded_at": datetime.utcnow(),
        "size_bytes": os.path.getsize(file_path),
        "extension": filename.rsplit('.', 1)[1].lower()
    }

    # Insert metadata into MongoDB
    result = resumes_collection.insert_one(metadata)
    metadata["_id"] = str(result.inserted_id)

    return jsonify({
        "message": "Resume uploaded successfully",
        "resume_id": str(result.inserted_id),
        "metadata": metadata
    }), 201


@main_bp.route('/upload-jd', methods=['POST'])
def upload_jd():
    file = request.files.get('jd')
    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    # Validate file extension
    allowed_exts = CONFIG.get("allowed_extensions_JD", [])
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        return jsonify({"error": "Invalid file type"}), 400

    # Secure filename and save
    filename = secure_filename(file.filename)
    upload_folder = CONFIG.get("jd_upload_folder", "uploads/jds")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # Extract metadata
    metadata = {
        "filename": filename,
        "filepath": file_path,
        "uploaded_at": datetime.utcnow(),
        "size_bytes": os.path.getsize(file_path),
        "extension": filename.rsplit('.', 1)[1].lower()
    }

    # Insert metadata into MongoDB
    result = jds_collection.insert_one(metadata)
    metadata["_id"] = str(result.inserted_id)
    return jsonify({
        "message": "JD uploaded successfully",
        "jd_id": str(result.inserted_id),
        "metadata": metadata
    }), 201