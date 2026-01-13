from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from pydantic_core import ValidationError
from typing import Optional

from app.auth.schema import GeneralResponse, RegisterUserResponse
from app.utils import AppModel

from ..service import Service, get_service
from . import router


class OtpPayload(AppModel):
    otp: str
    email: Optional[EmailStr] = None


@router.post(
    "/users/otp",
    status_code=status.HTTP_201_CREATED,
    response_model=GeneralResponse,
)
def verify_otp(
    payload: OtpPayload,
    svc: Service = Depends(get_service),
) -> GeneralResponse:
    email = payload.email or "mptsoftwareotp842@gmail.com"
    user_data = svc.repository.get_user_by_email(email)
    if not user_data:
        error_message = f"User with email {email} not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        user_data = RegisterUserResponse(**user_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )

    otp_response = svc.repository.get_otp_for_user(id=user_data.id)
    if not otp_response:
        error_message = "There is no OTP for the user."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    if payload.otp != otp_response["otp"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Otp is Invalid"
        )
    return GeneralResponse(
        detail="Otp is verified successfully"
    )
