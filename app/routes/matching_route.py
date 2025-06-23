from fastapi import APIRouter
from app.matcher import perform_resume_jd_matching

matching_router = APIRouter()

@matching_router.post("/trigger-matching")
def trigger_resume_jd_matching():
    try:
        perform_resume_jd_matching()
        return {"status": "success", "message": "Matching completed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
