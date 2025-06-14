from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from pydantic_core import ValidationError

from app.auth.schema import OtpResponse, RegisterUserResponse, GeneralResponse
from app.constants import OTP_EMAIL_BODY
from app.utils import AppModel, generate_otp, send_email

from ..service import Service, get_service
from . import router


class EmailPayload(AppModel):
    email: EmailStr


@router.post(
    "/users/reset",
    status_code=status.HTTP_201_CREATED,
    response_model=GeneralResponse,
)
def reset_password(
    payload: EmailPayload,
    svc: Service = Depends(get_service),
) -> GeneralResponse:
    email = payload.email
    user_data = svc.repository.get_user_by_email(email)
    if not user_data:
        error_message = f"User with email {email} not found"
        print(error_message)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        user_data = RegisterUserResponse(**user_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )

    existing_otp = svc.repository.get_otp_for_user(id=user_data.id)
    if existing_otp:
        try:
            existing_otp = OtpResponse(**existing_otp)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Pydantic Validation Error. Please Contact Admin or Developer.",
            )
            
        if existing_otp.expiration_time > datetime.now(tz=timezone.utc):
            return GeneralResponse(detail="Existing OTP is not yet expired")
        else:
            svc.repository.delete_otp_for_user(existing_otp.id)
    created_otp = generate_otp()
    svc.repository.create_otp_for_user(otp=created_otp, id=user_data.id)
    reset_otp_email_body = OTP_EMAIL_BODY.format(
        user_name=user_data.name, otp=created_otp
    )
    response = send_email(
        subject="Password Reset OTP", email=email, custom_message=reset_otp_email_body
    )
    return GeneralResponse(detail=response)
