import json
import os
from apiclient import discovery
from apiclient.http import MediaFileUpload
from google.oauth2 import service_account


class DriveClient:
    def __init__(self):
        sa = open("./service_account.json")
        creds_json = json.load(sa, strict=False)
        scopes_list = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
        ]
        credentials = service_account.Credentials.from_service_account_info(
            creds_json, scopes=scopes_list
        )
        self.service = discovery.build(
            "drive", "v3", credentials=credentials, cache_discovery=False
        )
        self.google_drive_folder_id = os.environ.get(
            "GOOGLE_DRIVE_FOLDER_ID", "<shared_folder_id>"
        )

    def upload_file(
        self,
        file_name_with_path,
        file_name,
        upload_folder,
        mime_type,
        leaf_folder_existed,
    ):
        print(f"leaf_folder_existed before upload: {leaf_folder_existed}")
        folder_id, folder_existed = self.__touch_folders(upload_folder)
        folder_existed = folder_existed and leaf_folder_existed
        if folder_existed:
            return True

        media_body = MediaFileUpload(file_name_with_path, mimetype=mime_type)
        body = {
            "name": file_name,
            "title": file_name,
            "description": file_name,
            "mimeType": mime_type,
            "parents": [folder_id],
        }

        self.service.files().create(
            supportsAllDrives=True, body=body, media_body=media_body
        ).execute()

        return False

    def __touch_folders(self, upload_folder):
        folders = upload_folder.split("/")
        folder_id = self.google_drive_folder_id
        existed = False
        for folder in folders:
            exst_folders = (
                self.service.files()
                .list(
                    supportsAllDrives=True,
                    q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'",
                )
                .execute()
                .get("files", [])
            )
            exst_folders = list(filter(lambda f: f["name"] == folder, exst_folders))
            print(f"exst_folders: {exst_folders}")
            if not exst_folders:
                folder_id = self.__create_folder(folder, folder_id)
                existed = False
            else:
                folder_id = exst_folders[0]["id"]
                existed = True
        return folder_id, existed

    def __create_folder(self, folder, folder_id):
        body = {
            "name": folder,
            "title": folder,
            "description": folder,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [folder_id],
        }

        created_folder = (
            self.service.files().create(supportsAllDrives=True, body=body).execute()
        )
        print(f"created_folder: {created_folder}")
        return created_folder["id"]
