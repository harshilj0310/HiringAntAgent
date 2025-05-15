import streamlit as st
import os
import sys
import tempfile

# Add root path to import tools
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.parse_resume import parse_resume
from tools.JD_parser import parse_job_description
from tools.jd_json_jobmatching import match_parsed_resume_to_job
from tools.send_email import send_email

THRESHOLD = 70
FIXED_EMAIL = "preetj0310@gmail.com"

st.title("HiringAnt Resume Matcher")
st.sidebar.header("Upload Files")

resume_files = st.sidebar.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)
jd_files = st.sidebar.file_uploader("Upload Job Descriptions (.txt or .json)", type=["txt", "json"], accept_multiple_files=True)

if resume_files and jd_files:
    st.success("Files uploaded. Matching resumes to JDs...")

    matches = []

    with tempfile.TemporaryDirectory() as tempdir:
        # Save and parse resumes
        resumes = []
        for file in resume_files:
            resume_path = os.path.join(tempdir, file.name)
            with open(resume_path, "wb") as f:
                f.write(file.read())
            parsed_resume = parse_resume(resume_path)
            resumes.append({"filename": file.name, "data": parsed_resume})

        # Save and parse JDs
        jds = []
        for file in jd_files:
            jd_path = os.path.join(tempdir, file.name)
            with open(jd_path, "wb") as f:
                f.write(file.read())
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_raw = f.read()
            parsed_jd = parse_job_description(jd_raw)
            jds.append({"filename": file.name, "data": parsed_jd})

        # Matching
        for resume in resumes:
            for jd in jds:
                result = match_parsed_resume_to_job(resume["data"], jd["data"])
                score = result.get("gpt_score", "N/A")
                explanation = result.get("gpt_explanation", "No explanation provided.")

                matches.append({
                    "resume": resume["filename"],
                    "job": jd["filename"],
                    "score": score,
                    "explanation": explanation,
                    "email": FIXED_EMAIL
                })

    # Display results and send emails
    for match in matches:
        st.subheader(f"Resume: {match['resume']} → JD: {match['job']}")
        st.write(f"**Score**: {match['score']}")
        st.write(f"**Explanation (Internal View)**: {match['explanation']}")

        if isinstance(match["score"], (int, float)):
            if match["score"] >= THRESHOLD:
                if st.button(f"Send Shortlist Email to {match['email']}", key=f"shortlist-{match['resume']}-{match['job']}"):
                    subject = f"Congratulations! You've been shortlisted for the position: {match['job']}"
                    body = f"""Dear Candidate,

We are pleased to inform you that you have been shortlisted for the role "{match['job']}" based on your application.

Our team will reach out to you soon regarding the next steps in the process.

Best regards,  
Hiring Team"""
                    send_email(match["email"], subject, body)
                    st.success(f"Shortlist email sent to {match['email']}!")
            else:
                if st.button(f"Send Rejection Email to {match['email']}", key=f"reject-{match['resume']}-{match['job']}"):
                    subject = f"Update on Your Application for: {match['job']}"
                    body = f"""Dear Candidate,

Thank you for applying to the position "{match['job']}". We appreciate the time and effort you put into your application.

After careful consideration, we regret to inform you that you have not been shortlisted for this role.

We wish you the very best in your future endeavors and encourage you to apply again for suitable opportunities with us.

Sincerely,  
Hiring Team"""
                    send_email(match["email"], subject, body)
                    st.success(f"Rejection email sent to {match['email']}!")
