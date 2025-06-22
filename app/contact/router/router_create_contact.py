import os
from fastapi import Depends, HTTPException, status, Form, File, UploadFile
from datetime import datetime, timezone
from pydantic_core import ValidationError
import time
from app.contact.contact_service import ContactService, get_contact_service
from app.contact.schema import Contact
from app.contact.utils import delete_file, handle_upload
from . import router


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Contact,
)
def create_contact(
    name: str = Form(...),
    personal: str = Form(...),
    office: str = Form(...),
    gstin: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    address_proof: UploadFile = File(...),
    svc: ContactService = Depends(get_contact_service),
) -> Contact:
    unix_time = int(time.time())
    _, ext = os.path.splitext(address_proof.filename)
    new_filename = f"image_{unix_time}{ext}"

    handle_upload(new_filename=new_filename, file=address_proof)

    payload = Contact(
        name=name,
        personal=personal,
        office=office,
        gstin=gstin,
        email=email,
        address=address,
        pincode=pincode,
        address_proof=new_filename,
        created_at=datetime.fromtimestamp(timestamp=unix_time, tz=timezone.utc),
    )
    contact_data = svc.repository.create_contact(contact=payload)

    if not contact_data:
        delete_file(filename=new_filename)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The Contact was not created"
        )

    try:
        contact_data = Contact(**contact_data)
        return contact_data
    except ValidationError:
        delete_file(filename=new_filename)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please contact the developer.",
        )
