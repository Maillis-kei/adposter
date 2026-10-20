"""Google Drive Uploader Module (Google Cloud Service Account Integration).

Uploads rendered gospel posters to a designated Google Drive folder.
- Authenticates using Google Cloud Service Account JSON credentials
- Uploads PNG poster with metadata (date, theme, church name)
- Returns webViewLink and file ID for tracking
- Provides graceful fallback when credentials or folder ID are not configured
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

# Default Google Drive API scopes
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def upload_poster_to_drive(
    file_path: Path,
    folder_id: Optional[str] = None,
    service_account_path: Optional[Path] = None,
    custom_title: Optional[str] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """Uploads a poster image to Google Drive.

    Args:
        file_path: Local path to the rendered poster image.
        folder_id: Destination Google Drive folder ID.
        service_account_path: Path to the service account JSON key file.
        custom_title: Display name for the uploaded file in Drive.

    Returns:
        (success: bool, info: dict with 'file_id', 'web_view_link', 'message')
    """
    file_path = Path(file_path)
    if not file_path.exists():
        msg = f"Local file not found for Drive upload: {file_path}"
        logger.error(msg)
        return False, {"message": msg, "file_id": None, "web_view_link": None}

    # Resolve folder ID
    drive_folder_id = folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()

    # Resolve service account path
    sa_path = service_account_path or os.getenv(
        "SERVICE_ACCOUNT_JSON_PATH", "service_account.json"
    )
    sa_file = Path(sa_path)
    if not sa_file.is_absolute():
        sa_file = BASE_DIR / sa_file

    if not sa_file.exists():
        msg = (
            f"Google Cloud service account JSON not found at '{sa_file}'. "
            f"Skipping cloud upload. Poster remains safely saved locally at '{file_path}'."
        )
        logger.warning(msg)
        return True, {
            "uploaded": False,
            "message": msg,
            "file_id": "LOCAL_ONLY",
            "web_view_link": str(file_path),
        }

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        creds = service_account.Credentials.from_service_account_file(
            str(sa_file), scopes=SCOPES
        )
        service = build("drive", "v3", credentials=creds)

        file_title = custom_title or file_path.name
        file_metadata: Dict[str, Any] = {
            "name": file_title,
            "mimeType": "image/png",
        }

        if drive_folder_id:
            file_metadata["parents"] = [drive_folder_id]

        media = MediaFileUpload(
            str(file_path), mimetype="image/png", resumable=True
        )

        logger.info(
            f"Uploading {file_path.name} to Google Drive folder '{drive_folder_id or 'Root'}'..."
        )
        uploaded_file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, name, webViewLink, webContentLink",
            )
            .execute()
        )

        file_id = uploaded_file.get("id")
        web_link = uploaded_file.get("webViewLink")

        logger.info(
            f"Google Drive upload complete! ID: {file_id}, Link: {web_link}"
        )
        return True, {
            "uploaded": True,
            "file_id": file_id,
            "web_view_link": web_link,
            "message": f"Successfully uploaded to Google Drive as '{file_title}'",
        }

    except Exception as e:
        error_msg = f"Failed to upload {file_path.name} to Google Drive: {e}"
        logger.error(error_msg)
        return False, {
            "uploaded": False,
            "message": error_msg,
            "file_id": None,
            "web_view_link": None,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_file = BASE_DIR / "output" / "test_composed_poster.png"
    success, info = upload_poster_to_drive(test_file)
    print("Upload Test Result:", success, info)
