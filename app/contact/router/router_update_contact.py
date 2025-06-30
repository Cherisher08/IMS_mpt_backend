import os
import time
from typing import Optional
from fastapi import Depends, Form, UploadFile, File, HTTPException, status
from pydantic_core import ValidationError

from app.contact.contact_service import ContactService, get_contact_service
from app.contact.schema import Contact
from app.contact.utils import handle_upload
from . import router


@router.put(
    "/{id}",
    response_model=Contact,
)
async def update_contact(
    id: str,
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
):
    if file:
        unix_time = int(time.time())
        _, ext = os.path.splitext(file.filename)
        filename = f"image_{unix_time}{ext}"
        handle_upload(new_filename=filename, file=file)
    else:
        filename = address_proof

    payload = Contact(
        name=name,
        personal_number=personal_number,
        office_number=office_number,
        gstin=gstin,
        email=email,
        address=address,
        pincode=pincode,
        company_name=company_name,
        address_proof=filename,
    )

    contact_data = svc.repository.update_contact(contact_id=id, contact=payload)

    if not contact_data:
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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please contact the developer.",
        )
    

