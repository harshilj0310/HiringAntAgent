import os
from app.connectors.mongo_resume_connector import MongoResumeConnector
from app.connectors.s3_resume_connector import S3ResumeConnector
from app.connectors.mysql_resume_connector import MySQLResumeConnector
from app.connectors.postgres_resume_connector import PostgresResumeConnector
from app.connectors.drive_resume_connector import GoogleDriveResumeConnector

def get_resume_connector():
    source = os.getenv("RESUME_SOURCE", "mongo").lower()

    if source == "mongo":
        return MongoResumeConnector()
    elif source == "s3":
        bucket = os.getenv("S3_BUCKET", "your-default-bucket")
        return S3ResumeConnector(bucket)
    elif source == "postgres":
        return PostgresResumeConnector(...)
    elif source == "mysql":
        return MySQLResumeConnector(...)
    elif source == "drive":
        return GoogleDriveResumeConnector(folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID"))
    else:
        raise ValueError(f"Unsupported resume source: {source}")
