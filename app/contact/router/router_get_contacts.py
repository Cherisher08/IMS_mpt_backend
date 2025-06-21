from typing import List
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.contact.schema import Contact
from app.contact.contact_service import ContactService, get_contact_service
from . import router

@router.get("", status_code=status.HTTP_200_OK, response_model=List[Contact])
def get_contacts(
    svc: ContactService = Depends(get_contact_service),
) -> List[Contact]:
    contact_data = svc.repository.get_contacts()
    for contact in contact_data:
        try:
            contact = Contact(**contact)
            contact.address_proof = (
                f"http://localhost:8000/public/contact/{contact.address_proof}"
            )
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pydantic Validation Error. Please Contact Admin or Developer.",
            )

    if not contact_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Contacts Found. Please create new contact",
        )

    try:
        contact_data = [Contact(**contact) for contact in contact_data]
        return contact_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
