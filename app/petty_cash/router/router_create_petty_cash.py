from fastapi import Depends, HTTPException, status

from app.petty_cash.petty_cash_service import PettyCashService, get_petty_cash_service
from app.petty_cash.schema import PettyCash

from . import router


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PettyCash,
)
def create_petty_cash(
    petty_cash: PettyCash,
    svc: PettyCashService = Depends(get_petty_cash_service),
) -> PettyCash:
    try:
        result = svc.repository.create_petty_cash(petty_cash)
        print("result: ", result)
        return PettyCash(**result)
    except Exception as e:
        print("Exception in creating petty cash: ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create petty cash entry: {str(e)}",
        )
