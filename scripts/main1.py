import os
import sys
import tempfile
import logging

# Add root path to import tools and logging config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logs.logging_config import setup_logging
from tools.parse_resume import parse_resume
from tools.JD_parser import parse_job_description
from tools.jd_json_jobmatching import match_parsed_resume_to_job
from tools.email2 import send_email

# Initialize logger
setup_logging()
logger = logging.getLogger(__name__)

THRESHOLD = 70

def load_files_from_dir(directory, extensions):
    files = []
    try:
        for filename in os.listdir(directory):
            if any(filename.lower().endswith(ext) for ext in extensions):
                files.append(os.path.join(directory, filename))
        logger.info(f"Loaded {len(files)} files from {directory} with extensions {extensions}")
    except Exception as e:
        logger.exception(f"Error loading files from {directory}")
        print(f"❌ Failed to load files from {directory}")
    return files

def main():
    try:
        resumes_dir = input("Enter the path to the directory containing resume PDFs: ").strip()
        jds_dir = input("Enter the path to the directory containing JD (.txt or .json) files: ").strip()
        from_email = input("Enter the sender email address (your email): ").strip()
        logger.info(f"this is the entered path resume :{resumes_dir}, jd :{jds_dir}")
        
        logger.info("Starting resume-job matching pipeline.")
        resume_files = load_files_from_dir(resumes_dir, [".pdf"])
        jd_files = load_files_from_dir(jds_dir, [".txt", ".json"])

        if not resume_files or not jd_files:
            logger.warning("Missing resume or JD files.")
            print("❌ Please ensure both resume and JD directories contain valid files.")
            return

        matches = []

        with tempfile.TemporaryDirectory() as tempdir:
            resumes = []
            for path in resume_files:
                try:
                    filename = os.path.basename(path)
                    temp_path = os.path.join(tempdir, filename)
                    with open(path, "rb") as src, open(temp_path, "wb") as dst:
                        dst.write(src.read())
                    parsed_resume = parse_resume(temp_path)
                    logger.info(f"Parsed resume: {filename}")
                    to_email = parsed_resume.get("Contact Information", {}).get("Email", "")
                    resumes.append({"filename": filename, "data": parsed_resume, "email": to_email})
                except Exception as e:
                    logger.exception(f"Failed to parse resume {path}")
                    print(f"⚠️ Skipped resume: {filename}")

            jds = []
            for path in jd_files:
                try:
                    filename = os.path.basename(path)
                    with open(path, "r", encoding="utf-8") as f:
                        jd_raw = f.read()
                    parsed_jd = parse_job_description(jd_raw)
                    logger.info(f"Parsed JD: {filename}")
                    jds.append({"filename": filename, "data": parsed_jd})
                except Exception as e:
                    logger.exception(f"Failed to parse JD {path}")
                    print(f"⚠️ Skipped JD: {filename}")

            for resume in resumes:
                for jd in jds:
                    try:
                        result = match_parsed_resume_to_job(resume["data"], jd["data"])
                        score = result.get("gpt_score", "N/A")
                        explanation = result.get("gpt_explanation", "No explanation provided.")
                        matches.append({
                            "resume": resume["filename"],
                            "job": jd["filename"],
                            "score": score,
                            "explanation": explanation,
                            "email": resume["email"]
                        })
                        logger.info(f"Matched {resume['filename']} with {jd['filename']}, score: {score}")
                    except Exception as e:
                        logger.exception(f"Failed to match {resume['filename']} with {jd['filename']}")
                        print(f"⚠️ Matching failed for: {resume['filename']} → {jd['filename']}")

        for match in matches:
            try:
                print(f"\n--- Match: {match['resume']} → {match['job']} ---")
                print(f"Score: {match['score']}")
                print(f"Explanation: {match['explanation']}")

                if isinstance(match["score"], (int, float)) and match["email"]:
                    if match["score"] >= THRESHOLD:
                        send = input(f"Send SHORTLIST email to {match['email']}? (y/n): ").strip().lower()
                        if send == 'y':
                            subject = f"Congratulations! You've been shortlisted for the position: {match['job']}"
                            body = f"""Dear Candidate,

We are pleased to inform you that you have been shortlisted for the role "{match['job']}" based on your application.

Our team will reach out to you soon regarding the next steps in the process.

Best regards,  
Hiring Team"""
                            send_email(from_email, match["email"], subject, body)
                            logger.info(f"Shortlist email sent to {match['email']}")
                            print(f"✅ Shortlist email sent to {match['email']}")
                    else:
                        send = input(f"Send REJECTION email to {match['email']}? (y/n): ").strip().lower()
                        if send == 'y':
                            subject = f"Update on Your Application for: {match['job']}"
                            body = f"""Dear Candidate,

Thank you for applying to the position "{match['job']}". We appreciate the time and effort you put into your application.

After careful consideration, we regret to inform you that you have not been shortlisted for this role.

We wish you the very best in your future endeavors and encourage you to apply again for suitable opportunities with us.

Sincerely,  
Hiring Team"""
                            send_email(from_email, match["email"], subject, body)
                            logger.info(f"Rejection email sent to {match['email']}")
                            print(f"❌ Rejection email sent to {match['email']}")
                elif not match["email"]:
                    logger.warning(f"No email found in resume: {match['resume']}")
                    print(f"⚠️ No email found in parsed resume: {match['resume']}")
            except Exception as e:
                logger.exception(f"Failed during email decision or sending for {match['resume']}")
                print(f"⚠️ Email process failed for: {match['resume']}")

    except Exception as e:
        logger.exception("An unexpected error occurred during execution.")
        print(f"❌ A critical error occurred: {e}")

if __name__ == "__main__":
    main()
