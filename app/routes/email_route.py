import logging
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import PlainTextResponse
from typing import List
from app.tools.email2 import send_email
from app.config import CONFIG
from app.db import matches_collection, resumes_collection, jds_collection
from bson import ObjectId

logger = logging.getLogger(__name__)
email_router = APIRouter()
THRESHOLD = CONFIG["threshold"]

@email_router.post("/send-mails")
async def send_emails(
    request: Request,
    from_email: str = Form(...),
    proceed: str = Form(...),
    matches: List[str] = Form(...)
):
    if not matches or not from_email:
        logger.warning("Missing matches or from_email in form data.")
        return PlainTextResponse("Missing matches or from_email", status_code=status.HTTP_400_BAD_REQUEST)

    if proceed != "on":
        logger.info("User cancelled email sending.")
        return PlainTextResponse("Mail sending cancelled by user.", status_code=status.HTTP_200_OK)

    object_ids = [ObjectId(mid) for mid in matches]

    raw_matches = matches_collection.find({
        "_id": {"$in": object_ids},
        "email_status": "Pending"
    })

    sent_count = 0
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
            logger.info(f"Shortlisting candidate: {email} for {job}")
            
            success = send_email(from_email, email, subject, body)

            if success:
                matches_collection.update_one(
                    {"_id": match["_id"]},
                    {"$set": {
                        "email_status": "Sent",
                        "interview_status": "PENDING"
                    }}
                )
            else:
                logger.warning(f"Email sending failed for {email}, DB not updated.")

        else:
            subject = CONFIG["email_templates"]["rejection"]["subject"].format(job=job)
            body = CONFIG["email_templates"]["rejection"]["body"].format(job=job)
            logger.info(f"Rejecting candidate: {email} for {job}")
            send_email(from_email, email, subject, body)

            matches_collection.update_one(
                {"_id": match["_id"]},
                {"$set": {"email_status": "Sent"}}
            )
        sent_count += 1

    logger.info(f"Emails sent successfully for {sent_count} matches.")
    return PlainTextResponse("Selected emails sent successfully.", status_code=status.HTTP_200_OK)
