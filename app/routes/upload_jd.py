import logging
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import datetime
from werkzeug.utils import secure_filename

from app.db import jds_collection, fs
from app.config import CONFIG

logger = logging.getLogger(__name__)
jd_router = APIRouter()

@jd_router.post("/upload-jd")
async def upload_jd(jd: UploadFile = File(...)):
    if not jd.filename:
        logger.error("No file uploaded.")
        return JSONResponse(status_code=400, content={"error": "No file uploaded"})

    allowed_exts = CONFIG.get("allowed_extensions_JD", [])
    if '.' not in jd.filename or jd.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        logger.warning(f"Invalid file type attempted: {jd.filename}")
        return JSONResponse(status_code=400, content={"error": "Invalid file type"})

    filename = secure_filename(jd.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    file_data = await jd.read()

    try:
        file_id = fs.put(file_data, filename=filename)

        metadata = {
            "filename": filename,
            "uploaded_at": datetime.utcnow(),
            "size_bytes": len(file_data),
            "extension": extension,
            "file_id": str(file_id)
        }

        result = jds_collection.insert_one(metadata)
        response_metadata = metadata.copy()
        response_metadata["_id"] = str(result.inserted_id)
        response_metadata["file_id"] = str(file_id)
        response_metadata["uploaded_at"] = metadata["uploaded_at"].isoformat()

        logger.info(f"JD uploaded: {filename}, ID: {response_metadata['_id']}")
        return JSONResponse(status_code=201, content={
            "message": "JD uploaded and stored in DB successfully",
            "jd_id": response_metadata["_id"],
            "metadata": response_metadata
        })

    except Exception as e:
        logger.exception("Error while uploading JD")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
    