import os
import shutil
from fastapi import UploadFile, File

UPLOAD_DIR = "app/public"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def handle_upload(
    new_filename: str,
    file: UploadFile = File(...),
    type: str = "contact",
):
    directory_path = os.path.join(UPLOAD_DIR, type)
    os.makedirs(directory_path, exist_ok=True)
    save_path = os.path.join(directory_path, new_filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file.file.close()


def delete_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
