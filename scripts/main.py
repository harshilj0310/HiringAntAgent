import os
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.resume_parser import parse_resume
from tools.jd_parser import parse_job_description
from tools.matcher import evaluate_match
from tools.email_sender import send_email

def load_files_from_dir(directory, valid_extensions):
    return [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if os.path.splitext(filename)[1].lower() in valid_extensions
    ]

def main():
    resumes_dir = input("Enter the path to the directory containing resume PDFs: ").strip()
    jd_dir = input("Enter the path to the directory containing JD (.txt or .json) files: ").strip()

    resume_files = load_files_from_dir(resumes_dir, [".pdf"])
    jd_files = load_files_from_dir(jd_dir, [".txt", ".json"])

    resumes = []
    for resume_path in resume_files:
        parsed_resume = parse_resume(resume_path)
        email = parsed_resume.get("Contact Information", {}).get("Email")

        if not email:
            print(f"⚠️ Email not found in {os.path.basename(resume_path)}, skipping.")
            continue

        resumes.append({
            "filename": os.path.basename(resume_path),
            "data": parsed_resume,
            "email": email
        })

    job_descriptions = []
    for jd_path in jd_files:
        parsed_jd = parse_job_description(jd_path)
        job_descriptions.append({
            "filename": os.path.basename(jd_path),
            "data": parsed_jd
        })

    matches = []
    for resume in resumes:
        for jd in job_descriptions:
            result = evaluate_match(resume["data"], jd["data"])
            score = result.get("score", 0)
            explanation = result.get("explanation", "No explanation provided")

            matches.append({
                "resume": resume["filename"],
                "job": jd["filename"],
                "score": score,
                "explanation": explanation,
                "email": resume["email"]
            })

    threshold = 70
    for match in matches:
        if match["score"] >= threshold:
            subject = f"Shortlisted for {match['job']}"
            body = (
                f"Congratulations! Based on our analysis, you have been shortlisted "
                f"for the role described in {match['job']} with a score of {match['score']}.\n\n"
                f"Explanation: {match['explanation']}"
            )
            print(f"✅ Sending email to {match['email']} for {match['resume']} matched with {match['job']}")
            send_email(match["email"], subject, body)
        else:
            print(f"❌ {match['resume']} not shortlisted for {match['job']} (score: {match['score']})")

if __name__ == "__main__":
    main()
