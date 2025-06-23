from app.connectors.base_resume_connector import ResumeConnector
from app.connectors.drive_auth import get_drive_service
import base64

class GoogleDriveResumeConnector(ResumeConnector):
    def __init__(self, folder_id: str):
        self.folder_id = folder_id
        self.service = get_drive_service()

    def get_all_resumes(self):
        query = f"'{self.folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
        results = self.service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        resumes = []

        for file in files:
            file_id = file['id']
            name = file['name']
            request = self.service.files().get_media(fileId=file_id)
            fh = bytearray()

            downloader = self.service._http.request("GET", f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media")
            if downloader.status == 200:
                file_bytes = downloader.data
                resumes.append({
                    "filename": name,
                    "file_id": file_id,
                    "content": file_bytes
                })
            else:
                print(f"[ERROR] Failed to fetch file {name}")

        return resumes
