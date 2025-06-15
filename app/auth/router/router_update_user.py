from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from pydantic_core import ValidationError

from app.auth.schema import RegisterUserResponse
from app.utils import AppModel

from ..service import Service, get_service
from . import router


class UpdateUserPassword(AppModel):
    password: str
    email: EmailStr

@router.post(
    "/users/update", status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponse
)
def update_user_password(
    payload: UpdateUserPassword,
    svc: Service = Depends(get_service),
) -> RegisterUserResponse:
    user = svc.repository.get_user_by_email(payload.email)
    if not user:
        error_message = f"User with email {payload.email} not found"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )
        
    try:
        user = {**user, "password": payload.password}
        user = RegisterUserResponse(**user)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
    
    updated_user = svc.repository.update_user(user)
    print('updated_user: ', updated_user)
    try:
        updated_user = RegisterUserResponse(**updated_user)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
    return updated_user
