from fastapi import Depends, HTTPException, status

from app.auth.schema import ResetPasswordResponse

from ..service import Service, get_service
from . import router


@router.post(
    "/users/otp/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=ResetPasswordResponse,
)
def get_otp(
    id: str,
    svc: Service = Depends(get_service),
) -> ResetPasswordResponse:
    response = svc.repository.get_otp_for_user(id)
    if not response:
        error_message = "There is no OTP for the user."
        print(error_message)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
    return response
