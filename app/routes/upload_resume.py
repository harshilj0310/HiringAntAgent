from flask import request, jsonify, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime

from app.db import resumes_collection, fs
from app.config import CONFIG

# Max file size (optional limit)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files.get('resume')
    
    # Get form fields
    title_jd = request.form.get('job_description_title')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    experience = request.form.get('experience')
    graduation = request.form.get('graduation')
    college_name = request.form.get('college_name')
    preferred_location = request.form.get('preferred_location')

    # Validate file
    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    allowed_exts = CONFIG.get("allowed_extensions_resume", [])
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_exts:
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    
    file_data = file.read()
    if len(file_data) > MAX_FILE_SIZE:
        return jsonify({"error": "File too large"}), 400

    # Save to GridFS
    file_id = fs.put(file_data, filename=filename, content_type=file.mimetype)

    # Prepare metadata
    metadata = {
        "filename": filename,
        "uploaded_at": datetime.utcnow(),
        "size_bytes": len(file_data),
        "extension": extension,
        "job_description_title": title_jd,
        "email": email,
        "mobile": mobile,
        "experience": experience,
        "graduation": graduation,
        "college_name": college_name,
        "preferred_location": preferred_location,
        "file_id": file_id  # GridFS file ID
    }

    # Store metadata
    result = resumes_collection.insert_one(metadata)
    metadata["_id"] = str(result.inserted_id)
    metadata["file_id"] = str(file_id)

    return jsonify({
        "message": "Resume uploaded and stored in DB successfully",
        "resume_id": str(result.inserted_id),
        "metadata": metadata
    }), 201

