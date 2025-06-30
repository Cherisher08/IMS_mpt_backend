from fastapi import Depends, HTTPException, Response, status

from app.contact.contact_service import ContactService, get_contact_service
from app.contact.utils import delete_file
from . import router


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(id: str, svc: ContactService = Depends(get_contact_service)):
    current_contact = svc.repository.get_contact_by_id(contact_id=id)

    delete_count = svc.repository.delete_contact(contact_id=id)
    if delete_count != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The Contact was not deleted. Please try again",
        )

    delete_file(filename=current_contact["address_proof"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
