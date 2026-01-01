import os
import shutil
import re
from fastapi import HTTPException, UploadFile, File, status

UPLOAD_DIR = "app/public"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by replacing invalid characters with underscores.
    
    Removes/replaces: /, \, :, *, ?, ", <, >, |
    """
    # Replace invalid filename characters with underscore
    invalid_chars = r'[/\\:*?"<>|]'
    sanitized = re.sub(invalid_chars, '_', filename)
    return sanitized


def handle_upload(
    new_filename: str,
    file: UploadFile = File(...),
    type: str = "contact",
):
    try:
        directory_path = os.path.join(UPLOAD_DIR, type)
        os.makedirs(directory_path, exist_ok=True)
        save_path = os.path.join(directory_path, new_filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file.file.close()
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload file: {str(e)}",
        )


def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
