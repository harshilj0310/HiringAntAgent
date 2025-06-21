import logging
from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse
from bson import ObjectId
from datetime import datetime

from app.db import matches_collection, resumes_collection, jds_collection
from app.config import CONFIG
from app.tools.email2 import send_email

logger = logging.getLogger(__name__)
interview_router = APIRouter()

@interview_router.post("/schedule-interviews")
async def handle_schedule_interviews(request: Request):
    form = await request.form()
    from_email = form.get("from_email")
    if not from_email:
        logger.error("Missing from_email in schedule request.")
        return PlainTextResponse("Missing from_email", status_code=400)

    for key in form:
        if key.startswith("match_"):
            match_id = key.split("_")[1]
            slots = form.getlist(f"slots_{match_id}")
            slot_objects = []

            for slot_str in slots:
                try:
                    dt = datetime.strptime(slot_str, "%Y-%m-%dT%H:%M")
                    slot_objects.append(dt.isoformat())
                except Exception as e:
                    logger.warning(f"Invalid datetime format '{slot_str}' for match {match_id}: {e}")
                    continue

            match = matches_collection.find_one({"_id": ObjectId(match_id)})
            if not match:
                logger.warning(f"Match not found for ID: {match_id}")
                continue

            resume = resumes_collection.find_one({"_id": match["resume_id"]})
            jd = jds_collection.find_one({"_id": match["jd_id"]})
            if not resume or not jd:
                logger.error(f"Missing resume or JD for match {match_id}")
                continue

            job_title = jd.get("job_title", jd.get("filename", "Unknown"))
            candidate_email = resume.get("email")

            # DB update
            matches_collection.update_one(
                {"_id": ObjectId(match_id)},
                {"$set": {
                    "interview_status": "SLOT_PROPOSED",
                    "interview_details": {
                        "proposed_slots": slot_objects
                    }
                }}
            )
            logger.info(f"Updated proposed slots for match {match_id}")

            # Email to candidate
            confirm_link = f"{CONFIG['host_url']}/confirm-slot/{match_id}"
            subject = CONFIG["email_templates"]["slot_selection"]["subject"].format(job=job_title)
            body = CONFIG["email_templates"]["slot_selection"]["body"].format(
                job=job_title,
                confirm_link=confirm_link
            )

            send_email(from_email, candidate_email, subject, body)
            logger.info(f"Sent slot selection email to {candidate_email} for job {job_title}")

    return PlainTextResponse("Slots shared with candidates successfully.", status_code=200)


@interview_router.post("/confirm-slot/{match_id}")
async def handle_confirm_slot(match_id: str, request: Request):
    form = await request.form()
    selected_slot = form.get("selected_slot")

    match = matches_collection.find_one({"_id": ObjectId(match_id)})
    if not match or "interview_details" not in match:
        logger.warning(f"Match not found or missing interview details for ID {match_id}")
        return PlainTextResponse("Invalid match or no proposed slots found.", status_code=404)

    if not selected_slot:
        logger.error("No slot selected by candidate.")
        return PlainTextResponse("No slot selected.", status_code=400)

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
    logger.info(f"Candidate confirmed slot for match {match_id}: {selected_slot}")

    subject = CONFIG["email_templates"]["interview_confirmation"]["subject"].format(job=job_title)
    body = CONFIG["email_templates"]["interview_confirmation"]["body"].format(
        job=job_title,
        slot=selected_slot
    )

    send_email(CONFIG["default_sender_email"], candidate_email, subject, body)
    logger.info(f"Sent interview confirmation to {candidate_email} for slot {selected_slot}")

    return PlainTextResponse("Your slot has been confirmed. A confirmation email has been sent.", status_code=200)
