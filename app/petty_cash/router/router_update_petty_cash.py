from fastapi import Depends, HTTPException, status

from app.petty_cash.petty_cash_service import PettyCashService, get_petty_cash_service
from app.petty_cash.schema import PettyCash, PettyCashResponse

from . import router


@router.put(
    "/{petty_cash_id}",
    status_code=status.HTTP_200_OK,
    response_model=PettyCashResponse,
)
def update_petty_cash(
    petty_cash_id: str,
    petty_cash: PettyCash,
    svc: PettyCashService = Depends(get_petty_cash_service),
) -> PettyCashResponse:
    try:
        result = svc.repository.update_petty_cash(petty_cash_id, petty_cash)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Petty cash entry not found",
            )
        return PettyCashResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update petty cash entry: {str(e)}",
        )
