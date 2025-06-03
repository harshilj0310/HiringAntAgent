from flask import Blueprint, render_template, request

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/upload-resume/<job_title>', methods=['GET'])
def resume_form(job_title):
    return render_template('upload_resume.html', job_title=job_title)

@frontend_bp.route("/")
def index():
    return render_template("home.html")

@frontend_bp.route("/student")
def student_form():
    return render_template("student_form.html")

@frontend_bp.route("/provider")
def provider_form():
    return render_template("provider_form.html")