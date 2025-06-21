import os
import shutil
from fastapi import UploadFile, File

UPLOAD_DIR = "app/public/contact"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def handle_upload(
    new_filename: str,
    file: UploadFile = File(...),
):
    save_path = os.path.join(UPLOAD_DIR, new_filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file.file.close()


def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
