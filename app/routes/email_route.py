import logging
from flask import Blueprint, request
from app.tools.email2 import send_email
from app.config import CONFIG
from app.db import matches_collection, resumes_collection, jds_collection
from bson import ObjectId

logger = logging.getLogger(__name__)
email_bp = Blueprint('email', __name__)
THRESHOLD = CONFIG["threshold"]

@email_bp.route('/send-mails', methods=['POST'])
def send_emails():
    from_email = request.form.get("from_email")
    proceed = request.form.get("proceed") == "on"
    match_ids = request.form.getlist("matches")

    if not match_ids or not from_email:
        return "Missing matches or from_email", 400

    if not proceed:
        return "Mail sending cancelled by user.", 200

    object_ids = [ObjectId(mid) for mid in match_ids]

    raw_matches = matches_collection.find({
        "_id": {"$in": object_ids},
        "email_status": "Pending"
    })

    for match in raw_matches:
        resume = resumes_collection.find_one({"_id": match["resume_id"]})
        jd = jds_collection.find_one({"_id": match["jd_id"]})

        if not resume or not jd:
            logger.warning(f"Missing resume or JD for match: {match['_id']}")
            continue

        email = resume.get("email")
        job = jd.get("job_title", jd.get("filename", "Unknown Role"))
        score = match["match_result"].get("score", 0)

        if not email:
            logger.error(f"Email not found in match: {match['_id']}. Skipping...")
            continue

        if score >= THRESHOLD:
            subject = CONFIG["email_templates"]["shortlist"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["shortlist"]["body"].format(job=job)

            send_email(from_email, email, subject, body)

            matches_collection.update_one(
                {"_id": match["_id"]},
                {"$set": {
                    "email_status": "Sent",
                    "interview_status": "PENDING"
                }}
            )
        else:
            subject = CONFIG["email_templates"]["rejection"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["rejection"]["body"].format(job=job)

            send_email(from_email, email, subject, body)

            matches_collection.update_one(
                {"_id": match["_id"]},
                {"$set": {"email_status": "Sent"}}
            )

    return "Selected emails sent successfully.", 200
