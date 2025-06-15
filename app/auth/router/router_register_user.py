from fastapi import Depends, HTTPException, status

from app.auth.schema import RegisterUserRequest, RegisterUserResponse

from ..service import Service, get_service
from . import router


@router.post(
    "/users", status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponse
)
def register_user(
    input: RegisterUserRequest,
    svc: Service = Depends(get_service),
) -> RegisterUserResponse:
    if svc.repository.get_user_by_email(input.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already taken.",
        )

    created_user = svc.repository.create_user(input)
    return created_user
