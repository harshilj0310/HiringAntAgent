from flask import Blueprint, request, jsonify
import logging
from werkzeug.utils import secure_filename
from datetime import datetime
from app.db import jds_collection, fs
from app.config import CONFIG

logger = logging.getLogger(__name__)

jd_bp = Blueprint('jd', __name__)

@jd_bp.route('/upload-jd', methods=['POST'])
def upload_jd():
    file = request.files.get('jd')
    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    # Validate file extension
    allowed_exts = CONFIG.get("allowed_extensions_JD", [])
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        return jsonify({"error": "Invalid file type"}), 400

    # Secure and read the file
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    file_data = file.read()

    # Save file to GridFS
    file_id = fs.put(file_data, filename=filename)

    # Store metadata
    metadata = {
        "filename": filename,
        "uploaded_at": datetime.utcnow(),
        "size_bytes": len(file_data),
        "extension": extension,
        "file_id": file_id
    }

    result = jds_collection.insert_one(metadata)
    metadata["_id"] = str(result.inserted_id)
    metadata["file_id"] = str(file_id)

    return jsonify({
        "message": "JD uploaded and stored in DB successfully",
        "jd_id": str(result.inserted_id),
        "metadata": metadata
    }), 201