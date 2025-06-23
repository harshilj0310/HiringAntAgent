from app.connectors.base_resume_connector import ResumeConnector
import boto3, json

class S3ResumeConnector(ResumeConnector):
    def __init__(self, bucket_name):
        self.s3 = boto3.client("s3")
        self.bucket = bucket_name

    def get_all_resumes(self):
        resumes = []
        objects = self.s3.list_objects_v2(Bucket=self.bucket).get("Contents", [])
        for obj in objects:
            key = obj["Key"]
            file = self.s3.get_object(Bucket=self.bucket, Key=key)
            resumes.append(json.loads(file["Body"].read()))
        return resumes
