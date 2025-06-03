from flask import Flask
from app.routes.frontend_route import frontend_bp
from app.routes.upload_resume import resume_bp
from app.routes.upload_jd import jd_bp
from app.routes.email_route import email_bp
from app.logs.logging_config import setup_logging
from dotenv import load_dotenv
from app.matcher import start_background_matcher
import os

def create_app():
    app = Flask(__name__)
    setup_logging()
    load_dotenv()

    app.register_blueprint(frontend_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(jd_bp)
    app.register_blueprint(email_bp)

    if os.environ.get("FLASK_RUN_FROM_CLI") != "true":
        start_background_matcher()

    return app


