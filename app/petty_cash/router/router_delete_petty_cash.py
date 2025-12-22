from fastapi import Depends, HTTPException, Response, status

from app.petty_cash.petty_cash_service import PettyCashService, get_petty_cash_service

from . import router


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_petty_cash(id: str, svc: PettyCashService = Depends(get_petty_cash_service)):
    delete_count = svc.delete_petty_cash(petty_cash_id=id)
    if delete_count != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The Petty Cash entry was not deleted. Please try again",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
