from flask import Blueprint, render_template, request
from bson import ObjectId
from app.db import matches_collection, resumes_collection, jds_collection
from datetime import datetime
from app.config import CONFIG
from app.tools.email2 import send_email

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/schedule-interviews', methods=["GET", "POST"])
def schedule_interviews():
    if request.method == "GET":
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

    elif request.method == "POST":
        from_email = request.form.get("from_email")
        if not from_email:
            return "Missing from_email", 400

        for key in request.form:
            if key.startswith("match_"):
                match_id = key.split("_")[1]
                date_val = request.form.get(f"date_{match_id}")
                time_val = request.form.get(f"time_{match_id}")

                if date_val and time_val:
                    dt_str = f"{date_val} {time_val}"
                    interview_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

                    # Fetch match, resume, and JD for email details
                    match = matches_collection.find_one({"_id": ObjectId(match_id)})
                    if not match:
                        continue
                    resume = resumes_collection.find_one({"_id": match["resume_id"]})
                    jd = jds_collection.find_one({"_id": match["jd_id"]})
                    if not resume or not jd:
                        continue

                    to_email = resume.get("email")
                    job_title = jd.get("job_title", jd.get("filename", "Unknown"))

                    subject = CONFIG["email_templates"]["interview"]["subject"].format(job=job_title)
                    body = CONFIG["email_templates"]["interview"]["body"].format(
                        job=job_title,
                        date=date_val,
                        time=time_val
                    )

                    send_email(from_email, to_email, subject, body)

                    # Update the database
                    matches_collection.update_one(
                        {"_id": ObjectId(match_id)},
                        {"$set": {
                            "interview_status": "SCHEDULED",
                            "interview_details": {
                                "datetime": interview_dt.isoformat()
                            }
                        }}
                    )

        return "Interview schedule updated and emails sent successfully.", 200
