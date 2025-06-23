from copy import deepcopy
import logging
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
from werkzeug.utils import secure_filename

from app.db import resumes_collection, fs
from app.config import CONFIG

logger = logging.getLogger(__name__)
resume_router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@resume_router.post("/upload-resume")
async def upload_resume(
    resume: UploadFile = File(...),
    job_description_title: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    experience: str = Form(...),
    graduation: str = Form(...),
    college_name: str = Form(...),
    preferred_location: str = Form(...)
):
    if not resume.filename:
        logger.error("No resume file uploaded.")
        return JSONResponse(status_code=400, content={"error": "No file uploaded"})

    allowed_exts = CONFIG.get("allowed_extensions_resume", [])
    if '.' not in resume.filename or resume.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        logger.warning(f"Invalid resume file type: {resume.filename}")
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})

    filename = secure_filename(resume.filename)
    extension = filename.rsplit('.', 1)[1].lower()

    file_data = await resume.read()
    if len(file_data) > MAX_FILE_SIZE:
        logger.warning(f"Resume file too large: {filename}")
        return JSONResponse(status_code=400, content={"error": "File too large"})

    try:
        file_id = fs.put(file_data, filename=filename, content_type=resume.content_type)
        uploaded_time = datetime.utcnow()
        metadata = {
            "filename": filename,
            "uploaded_at": uploaded_time,
            "size_bytes": len(file_data),
            "extension": extension,
            "job_description_title": job_description_title,
            "email": email,
            "mobile": mobile,
            "experience": experience,
            "graduation": graduation,
            "college_name": college_name,
            "preferred_location": preferred_location,
            "file_id": file_id
        }

        result = resumes_collection.insert_one(metadata)

        # Now create a JSON-serializable copy
        response_metadata = deepcopy(metadata)
        response_metadata["_id"] = str(result.inserted_id)
        response_metadata["file_id"] = str(file_id)
        response_metadata["uploaded_at"] = uploaded_time.isoformat()

        return JSONResponse(status_code=201, content={
            "message": "Resume uploaded and stored in DB successfully",
            "resume_id": response_metadata["_id"],
            "metadata": response_metadata
        })

    except Exception as e:
        logger.exception("Error during resume upload.")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
