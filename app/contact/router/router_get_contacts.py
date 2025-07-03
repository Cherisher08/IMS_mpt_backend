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
    if not contact_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Contacts Found. Please create new contact",
        )

    for contact in contact_data:
        try:
            if contact["address_proof"]:
                contact["address_proof"] = (
                    f"http://localhost:8000/public/contact/{contact["address_proof"]}"
                )
            contact = Contact(**contact)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Pydantic Validation Error. Please Contact Admin or Developer. ${e}",
            )

    return contact_data
