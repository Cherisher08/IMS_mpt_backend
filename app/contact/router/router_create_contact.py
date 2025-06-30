import os
from typing import Optional
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
    personal_number: str = Form(...),
    office_number: str = Form(...),
    gstin: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    company_name: str = Form(...),
    address_proof: str = Form(...),
    file: Optional[UploadFile] = File(None),
    svc: ContactService = Depends(get_contact_service),
) -> Contact:
    
    if file: 
        unix_time = int(time.time())
        _, ext = os.path.splitext(file.filename)
        new_filename = f"image_{unix_time}{ext}"
        handle_upload(new_filename=new_filename, file=file)
    try:
        payload = Contact(
            name=name,
            personal_number=personal_number,
            office_number=office_number,
            gstin=gstin,
            email=email,
            address=address,
            pincode=pincode,
            company_name=company_name,
            address_proof=new_filename or "",
            created_at=datetime.fromtimestamp(timestamp=unix_time, tz=timezone.utc),
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please contact the developer.",
        )
    contact_data = svc.repository.create_contact(contact=payload)

    if not contact_data:
        delete_file(filename=new_filename)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="The Contact was not created"
        )

    try:
        contact_data["address_proof"] = (
            f"http://localhost:8000/public/contact/{contact_data["address_proof"]}"
        )
        contact_data = Contact(**contact_data)
        return contact_data
    except ValidationError:
        delete_file(filename=new_filename)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please contact the developer.",
        )
