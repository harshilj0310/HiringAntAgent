import os
import logging
import yaml
from io import BytesIO

from app.tools.parse_resume import parse_resume
from app.tools.JD_parser import parse_job_description
from app.tools.jd_json_jobmatching import match_parsed_resume_to_job

# Load YAML config
with open("app/config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)

THRESHOLD = CONFIG.get("threshold", 0.6)
logger = logging.getLogger(__name__)

def process_matching_single(resume_tuple, jd_tuple):
    """
    Matches a single resume with a single job description.

    Args:
        resume_tuple: (filename, content_bytes)
        jd_tuple: (filename, content_bytes)

    Returns:
        Match result dict or None
    """
    resume_filename, resume_bytes = resume_tuple
    jd_filename, jd_bytes = jd_tuple

    try:
        resume_parsed = parse_resume(resume_bytes)
        jd_parsed = parse_job_description(jd_bytes)

        result = match_parsed_resume_to_job(resume_parsed, jd_parsed)
        score = result.get("gpt_score", 0)
        explanation = result.get("gpt_explanation", "No explanation provided.")
        email = resume_parsed.get("Contact Information", {}).get("Email", "")

        return {
            "resume": resume_filename,
            "job": jd_filename,
            "score": score,
            "explanation": explanation,
            "email": email
        }
    except Exception as e:
        logger.error(f"❌ Failed to match {resume_filename} to {jd_filename}: {e}")
        return None
