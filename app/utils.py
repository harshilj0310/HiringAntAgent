import os
from tools.parse_resume import parse_resume
from tools.JD_parser import parse_job_description
from tools.jd_json_jobmatching import match_parsed_resume_to_job
from tools.email2 import send_email
import logging
import yaml

# Load YAML config
with open("config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)

THRESHOLD = CONFIG["threshold"]

logger = logging.getLogger(__name__)

def process_matching(resume_paths, jd_paths, from_email):
    resumes = []
    for path in resume_paths:
        parsed = parse_resume(path)
        resumes.append({
            "filename": os.path.basename(path),
            "data": parsed,
            "email": parsed.get("Contact Information", {}).get("Email", "")
        })

    jds = []
    for path in jd_paths:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        parsed = parse_job_description(content)
        jds.append({
            "filename": os.path.basename(path),
            "data": parsed
        })

    results = []
    for resume in resumes:
        for jd in jds:
            result = match_parsed_resume_to_job(resume["data"], jd["data"])
            score = result.get("gpt_score", 0)
            explanation = result.get("gpt_explanation", "No explanation provided.")

            match_info = {
                "resume": resume["filename"],
                "job": jd["filename"],
                "score": score,
                "explanation": explanation,
                "email": resume["email"]
            }

            results.append(match_info)

            # Only send emails if both from_email and candidate email are available
            if from_email and resume["email"]:
                job_title = jd["filename"]

                if score >= THRESHOLD:
                    subject = CONFIG["email_templates"]["shortlist"]["subject"].format(job=job_title)
                    body = CONFIG["email_templates"]["shortlist"]["body"].format(job=job_title)
                    send_email(from_email, resume["email"], subject, body)

                else:
                    subject = CONFIG["email_templates"]["rejection"]["subject"].format(job=job_title)
                    body = CONFIG["email_templates"]["rejection"]["body"].format(job=job_title)
                    send_email(from_email, resume["email"], subject, body)

    return results
