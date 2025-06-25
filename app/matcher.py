# app/services/matching_service.py

import hashlib
import time
from bson.objectid import ObjectId

from app.utils import process_matching_single
from app.db import jds_collection, matches_collection, fs, resumes_collection

matched_hashes = set()

def generate_resume_hash(resume):
    email = resume.get("email", "")
    job_title = resume.get("job_description_title", "")
    date = str(resume.get("uploaded_at", ""))[:10]
    phone = resume.get("mobile", "")
    base = f"{email}-{job_title}-{date}-{phone}"
    return hashlib.sha256(base.encode()).hexdigest()


def generate_jd_hash(jd):
    title = jd.get("job_title", jd.get("filename", ""))
    return hashlib.sha256(title.strip().lower().encode()).hexdigest()


def get_file_content(file_id):
    try:
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        grid_out = fs.get(file_id)
        return grid_out.read()
    except Exception as e:
        print(f"⚠️ Failed to read file from GridFS (id={file_id}): {e}")
        return None


def perform_resume_jd_matching():
    resumes = list(resumes_collection.find())
    jds = list(jds_collection.find())

    for resume in resumes:
        for jd in jds:
            resume_hash = generate_resume_hash(resume)
            jd_hash = generate_jd_hash(jd)
            combined_hash = f"{resume_hash}:{jd_hash}"

            if combined_hash in matched_hashes:
                print("⏩ Skipping duplicate match...")
                continue

            resume_input = None
            jd_input = None

            if "file_id" in resume:
                resume_content = get_file_content(resume["file_id"])
                if resume_content:
                    resume_input = (resume.get("filename", "resume.pdf"), resume_content)

            if "file_id" in jd:
                jd_content = get_file_content(jd["file_id"])
                if jd_content:
                    jd_input = (jd.get("filename", "jd.pdf"), jd_content)

            if not (resume_input and jd_input):
                print("❌ Missing content for resume or JD. Skipping.")
                continue

            result = process_matching_single(resume_input, jd_input)
            if not result:
                continue

            matches_collection.insert_one({
                "resume_id": resume["_id"],
                "jd_id": jd["_id"],
                "match_result": result,
                "timestamp": time.time(),
                "email_status": "Pending",
                "interview_status": "NOT_SORT_LISTED_YET",
                "interview_details": {"datetime": "NA"}
            })

            matched_hashes.add(combined_hash)
            print(f"✅ Stored match: {resume.get('filename')} ↔ {jd.get('filename')} (Score: {result['score']})")
