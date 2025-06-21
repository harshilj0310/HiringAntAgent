from fastapi import FastAPI
from app.routes.frontend_route import frontend_router
from app.routes.upload_resume import resume_router
from app.routes.upload_jd import jd_router
from app.routes.email_route import email_router
from app.routes.schedule_interviews import interview_router
from app.logs.logging_config import setup_logging
from dotenv import load_dotenv
from app.matcher import start_background_matcher
import os
import threading

def create_app():
    app = FastAPI()
    setup_logging()
    load_dotenv()

    # Include routers
    app.include_router(frontend_router)
    app.include_router(resume_router)
    app.include_router(jd_router)
    app.include_router(email_router)
    app.include_router(interview_router)

    # Start background matcher in separate thread
    if os.environ.get("RUN_MAIN", "true") == "true":
        threading.Thread(target=start_background_matcher, daemon=True).start()

    return app

app = create_app()