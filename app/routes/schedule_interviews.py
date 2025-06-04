from flask import Blueprint, request
from bson import ObjectId
from datetime import datetime

from app.db import matches_collection, resumes_collection, jds_collection
from app.config import CONFIG
from app.tools.email2 import send_email

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/schedule-interviews', methods=["POST"])
def handle_schedule_interviews():
    from_email = request.form.get("from_email")
    if not from_email:
        return "Missing from_email", 400

    for key in request.form:
        if key.startswith("match_"):
            match_id = key.split("_")[1]
            slots = request.form.getlist(f"slots_{match_id}")  # List of date-time strings
            slot_objects = []
            for slot_str in slots:
                try:
                    dt = datetime.strptime(slot_str, "%Y-%m-%dT%H:%M")
                    slot_objects.append(dt.isoformat())
                except:
                    continue

            match = matches_collection.find_one({"_id": ObjectId(match_id)})
            if not match:
                continue
            resume = resumes_collection.find_one({"_id": match["resume_id"]})
            jd = jds_collection.find_one({"_id": match["jd_id"]})

            if not resume or not jd:
                continue

            job_title = jd.get("job_title", jd.get("filename", "Unknown"))
            candidate_email = resume.get("email")

            # Update DB
            matches_collection.update_one(
                {"_id": ObjectId(match_id)},
                {"$set": {
                    "interview_status": "SLOT_PROPOSED",
                    "interview_details": {
                        "proposed_slots": slot_objects
                    }
                }}
            )

            # Email
            confirm_link = f"{CONFIG['host_url']}/confirm-slot/{match_id}"
            subject = CONFIG["email_templates"]["slot_selection"]["subject"].format(job=job_title)
            body = CONFIG["email_templates"]["slot_selection"]["body"].format(
                job=job_title,
                confirm_link=confirm_link
            )

            send_email(from_email, candidate_email, subject, body)

    return "Slots shared with candidates successfully.", 200


@interview_bp.route("/confirm-slot/<match_id>", methods=["POST"])
def handle_confirm_slot(match_id):
    match = matches_collection.find_one({"_id": ObjectId(match_id)})
    if not match or "interview_details" not in match:
        return "Invalid match or no proposed slots found.", 404

    selected_slot = request.form.get("selected_slot")
    if not selected_slot:
        return "No slot selected.", 400

    resume = resumes_collection.find_one({"_id": match["resume_id"]})
    jd = jds_collection.find_one({"_id": match["jd_id"]})
    job_title = jd.get("job_title", jd.get("filename", "Unknown"))
    candidate_email = resume.get("email")

    matches_collection.update_one(
        {"_id": ObjectId(match_id)},
        {"$set": {
            "interview_status": "SCHEDULED",
            "interview_details.confirmed_slot": selected_slot
        }}
    )

    subject = CONFIG["email_templates"]["interview_confirmation"]["subject"].format(job=job_title)
    body = CONFIG["email_templates"]["interview_confirmation"]["body"].format(
        job=job_title,
        slot=selected_slot
    )

    send_email(CONFIG["default_sender_email"], candidate_email, subject, body)
    return "Your slot has been confirmed. A confirmation email has been sent.", 200
