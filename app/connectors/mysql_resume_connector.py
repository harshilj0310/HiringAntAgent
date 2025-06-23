from app.connectors.base_resume_connector import ResumeConnector
from sqlalchemy import create_engine, text
import os

class MySQLResumeConnector(ResumeConnector):
    def __init__(self):
        self.engine = create_engine(os.getenv("MYSQL_URI"))

    def get_all_resumes(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM resumes"))
            resumes = [dict(row._mapping) for row in result]
        return resumes
