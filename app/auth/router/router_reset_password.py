from datetime import datetime
from fastapi import Depends, HTTPException, status

from app.auth.schema import ResetPasswordResponse
from app.constants import OTP_EMAIL_BODY
from app.utils import generate_otp, send_email

from ..service import Service, get_service
from . import router


@router.post(
    "/users/reset", status_code=status.HTTP_201_CREATED, response_model=ResetPasswordResponse
)
def reset_password(
    email: str,
    svc: Service = Depends(get_service),
) -> ResetPasswordResponse:
    user_data = svc.repository.get_user_by_email(input.email)
    if not user_data:
        error_message = f"User with email {input.email} not found"
        print(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )

    existing_otp = svc.repository.get_otp_for_user(id=user_data.id)
    if existing_otp:
        if existing_otp.expiration_time < datetime.now():
            return existing_otp
        else:
            svc.repository.delete_otp_for_user(existing_otp.id)
    created_otp = generate_otp()
    svc.repository.create_otp_for_user(otp=created_otp, id=user_data.id)
    reset_otp_email_body = OTP_EMAIL_BODY.format(user_name=user_data.name, otp=created_otp)
    response = send_email(subject="Password Reset OTP", email=email, custom_message= reset_otp_email_body)
    return ResetPasswordResponse(
        detail=response
    )
