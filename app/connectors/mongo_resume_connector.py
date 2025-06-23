from app.connectors.base_resume_connector import ResumeConnector
from app.db import resumes_collection

class MongoResumeConnector(ResumeConnector):
    def get_all_resumes(self):
        return list(resumes_collection.find())
