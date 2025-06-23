from fastapi import FastAPI
from dotenv import load_dotenv

from app.routes.frontend_route import frontend_router
from app.routes.upload_resume import resume_router
from app.routes.upload_jd import jd_router
from app.routes.email_route import email_router
from app.routes.schedule_interviews import interview_router
from app.routes.matching_route import matching_router
from app.logs.logging_config import setup_logging

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
    app.include_router(matching_router)

    return app

app = create_app()
