# app/db.py
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["resume_jd_db"]

# Collections
resumes_collection = db["resumes"]
jds_collection = db["jds"]
matches_collection = db["matches"]
