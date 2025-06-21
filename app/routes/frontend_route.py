import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from app.db import matches_collection, resumes_collection, jds_collection

logger = logging.getLogger(__name__)
frontend_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@frontend_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    logger.info("Rendering home page.")
    return templates.TemplateResponse("home.html", {"request": request})


@frontend_router.get("/upload-resume/{job_title}", response_class=HTMLResponse)
async def resume_form(request: Request, job_title: str):
    logger.info(f"Rendering resume upload page for job title: {job_title}")
    return templates.TemplateResponse("upload_resume.html", {"request": request, "job_title": job_title})


@frontend_router.get("/student", response_class=HTMLResponse)
async def student_form(request: Request):
    logger.info("Rendering student form.")
    return templates.TemplateResponse("student_form.html", {"request": request})


@frontend_router.get("/provider", response_class=HTMLResponse)
async def provider_form(request: Request):
    logger.info("Rendering provider form.")
    return templates.TemplateResponse("provider_form.html", {"request": request})


@frontend_router.get("/schedule-interviews", response_class=HTMLResponse)
async def schedule_interviews_page(request: Request):
    logger.info("Rendering schedule interviews page.")
    pending_matches = list(matches_collection.find({"interview_status": "PENDING"}))
    matches_display = []

    for match in pending_matches:
        resume = resumes_collection.find_one({"_id": match["resume_id"]})
        jd = jds_collection.find_one({"_id": match["jd_id"]})
        matches_display.append({
            "id": str(match["_id"]),
            "resume_filename": resume.get("filename", "Unknown") if resume else "Unknown",
            "email": resume.get("email", "Unknown") if resume else "Unknown",
            "job_title": jd.get("job_title", jd.get("filename", "Unknown")) if jd else "Unknown",
            "score": match["match_result"].get("score", 0)
        })

    return templates.TemplateResponse("schedule_interviews.html", {"request": request, "matches": matches_display})


@frontend_router.get("/confirm-slot/{match_id}", response_class=HTMLResponse)
async def confirm_slot_page(request: Request, match_id: str):
    match = matches_collection.find_one({"_id": ObjectId(match_id)})
    if not match or "interview_details" not in match:
        logger.warning(f"No interview details for match {match_id}")
        return PlainTextResponse("Invalid match or no proposed slots found.", status_code=404)

    slots = match["interview_details"].get("proposed_slots", [])
    resume = resumes_collection.find_one({"_id": match["resume_id"]})
    jd = jds_collection.find_one({"_id": match["jd_id"]})
    job_title = jd.get("job_title", jd.get("filename", "Unknown"))
    candidate_email = resume.get("email")

    return templates.TemplateResponse("confirm_slot.html", {
        "request": request,
        "slots": slots,
        "job_title": job_title,
        "candidate_email": candidate_email
    })


@frontend_router.get("/send-mails", response_class=HTMLResponse)
async def email_form(request: Request):
    logger.info("Rendering email form page.")
    pending_matches = list(matches_collection.find({"email_status": "Pending"}))

    matches_display = []
    for match in pending_matches:
        resume = resumes_collection.find_one({"_id": match["resume_id"]})
        jd = jds_collection.find_one({"_id": match["jd_id"]})
        matches_display.append({
            "id": str(match["_id"]),
            "resume_filename": resume.get("filename", "Unknown") if resume else "Unknown",
            "job_title": jd.get("job_title", jd.get("filename", "Unknown")) if jd else "Unknown",
            "score": match.get("match_result", {}).get("score", 0),
            "explanation": match.get("match_result", {}).get("explanation", "No explanation provided")
        })

    return templates.TemplateResponse("send_emails.html", {"request": request, "matches": matches_display})
