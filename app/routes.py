from flask import Blueprint, request, jsonify
from app.utils import process_matching
import os
import tempfile

main_bp = Blueprint('main', __name__)

@main_bp.route('/match', methods=['POST'])
def match_endpoint():
    resumes = request.files.getlist('resumes')
    jds = request.files.getlist('jds')
    from_email = request.form.get('from_email')

    if not resumes or not jds:
        return jsonify({"error": "Both resumes and JDs must be uploaded."}), 400

    with tempfile.TemporaryDirectory() as tempdir:
        resume_paths = []
        jd_paths = []

        for file in resumes:
            path = os.path.join(tempdir, file.filename)
            file.save(path)
            resume_paths.append(path)

        for file in jds:
            path = os.path.join(tempdir, file.filename)
            file.save(path)
            jd_paths.append(path)

        try:
            matches = process_matching(resume_paths, jd_paths, from_email)
            return jsonify(matches), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
