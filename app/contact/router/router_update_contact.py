from datetime import datetime
import os
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
    personal: str = Form(...),
    office: str = Form(...),
    gstin: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    company_name: str = Form(...),
    created_at: str = Form(...),
    address_proof: UploadFile = File(...),
    svc: ContactService = Depends(get_contact_service),
):
    current_data = svc.repository.get_contact_by_id(contact_id=id)
    filename = current_data["address_proof"]
    handle_upload(new_filename=filename, file=address_proof)

    payload = Contact(
        name=name,
        personal=personal,
        office=office,
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
        contact_data = Contact(**contact_data)
        return contact_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please contact the developer.",
        )
