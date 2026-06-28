import os
import time
from typing import List
from fastapi import File, UploadFile, status

from app.contact.utils import handle_upload
from app.utils import env
from . import router


@router.post(
    "/rentals/upload-site-images",
    status_code=status.HTTP_200_OK,
)
def upload_site_images(
    files: List[UploadFile] = File(...),
):
    saved_urls = []
    unix_time = int(time.time())
    for index, file in enumerate(files):
        _, ext = os.path.splitext(file.filename or "")
        filename = f"site_image_{unix_time}_{index}{ext}"
        # Save to public/order directory
        handle_upload(new_filename=filename, file=file, type="order")
        # Generate full URL
        saved_urls.append(f"{env.image_domain}/public/order/{filename}")
    return {"urls": saved_urls}
