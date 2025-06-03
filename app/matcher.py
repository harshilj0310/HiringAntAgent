import time
import threading
import hashlib
from app.utils import process_matching_single
from app.db import resumes_collection, jds_collection, matches_collection, fs
from bson.objectid import ObjectId

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
        # Make sure file_id is ObjectId type
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        grid_out = fs.get(file_id)  # fs = your GridFS instance
        return grid_out.read()
    except Exception as e:
        print(f"Failed to read file from GridFS for id {file_id}: {e}")
        return None

def background_match_worker():
    while True:
        try:
            print("running the background function.....")
            resumes = list(resumes_collection.find())
            jds = list(jds_collection.find())

            for resume in resumes:
                for jd in jds:
                    resume_hash = generate_resume_hash(resume)
                    jd_hash = generate_jd_hash(jd)
                    combined_hash = f"{resume_hash}:{jd_hash}"

                    if combined_hash in matched_hashes:
                        print("Duplicate match detected....")
                        continue

                    resume_input = None
                    jd_input = None

                    if "file_id" in resume:
                        resume_content = get_file_content(resume["file_id"])
                        if resume_content is not None:
                            resume_input = (resume["filename"], resume_content)

                    if "file_id" in jd:
                        jd_content = get_file_content(jd["file_id"])
                        if jd_content is not None:
                            jd_input = (jd["filename"], jd_content)

                    if resume_input and jd_input:
                        result = process_matching_single(resume_input, jd_input)
                    else:
                        print("Missing file content for resume or JD")

                    if not result:
                        continue

                    matches_collection.insert_one({
                        "resume_id": resume["_id"],
                        "jd_id": jd["_id"],
                        "match_result": result,
                        "timestamp": time.time()
                    })

                    matched_hashes.add(combined_hash)
                    print(f"✅ Stored match: {resume['filename']} ↔ {jd['filename']} (Score: {result['score']})")

        except Exception as e:
            print(f"[ERROR] Background matcher failed: {e}")

        time.sleep(10)  # Polling interval

def start_background_matcher():
    thread = threading.Thread(target=background_match_worker, daemon=True)
    thread.start()
