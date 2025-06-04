# --- frontend_bp.py (Updated to handle GET routes only) ---
from flask import Blueprint, render_template, request
from bson import ObjectId
from app.db import matches_collection, resumes_collection, jds_collection

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    return render_template("home.html")

@frontend_bp.route('/upload-resume/<job_title>', methods=['GET'])
def resume_form(job_title):
    return render_template('upload_resume.html', job_title=job_title)

@frontend_bp.route('/student')
def student_form():
    return render_template('student_form.html')

@frontend_bp.route('/provider')
def provider_form():
    return render_template('provider_form.html')

@frontend_bp.route('/schedule-interviews', methods=['GET'])
def schedule_interviews_page():
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
    return render_template("schedule_interviews.html", matches=matches_display)

@frontend_bp.route("/confirm-slot/<match_id>", methods=['GET'])
def confirm_slot_page(match_id):
    match = matches_collection.find_one({"_id": ObjectId(match_id)})
    if not match or "interview_details" not in match:
        return "Invalid match or no proposed slots found.", 404

    slots = match["interview_details"].get("proposed_slots", [])
    resume = resumes_collection.find_one({"_id": match["resume_id"]})
    jd = jds_collection.find_one({"_id": match["jd_id"]})
    job_title = jd.get("job_title", jd.get("filename", "Unknown"))
    candidate_email = resume.get("email")

    return render_template("confirm_slot.html", slots=slots, job_title=job_title, candidate_email=candidate_email)

@frontend_bp.route('/send-mails', methods=['GET'])
def email_form():
    pending_matches = list(matches_collection.find({"email_status": "Pending"}))
    
    matches_display = []
    for match in pending_matches:
        resume = resumes_collection.find_one({"_id": match["resume_id"]})
        jd = jds_collection.find_one({"_id": match["jd_id"]})
        matches_display.append({
            "id": str(match["_id"]),
            "resume_filename": resume.get("filename", "Unknown") if resume else "Unknown",
            "job_title": jd.get("job_title", jd.get("filename", "Unknown")) if jd else "Unknown",
            "score": match["match_result"].get("score", 0) if "match_result" in match else 0,
            "explanation": match["match_result"].get("explanation", "No explanation provided") if "match_result" in match else "No explanation provided"
        })
    return render_template("send_emails.html", matches=matches_display)