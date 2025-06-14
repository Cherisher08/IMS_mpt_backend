from fastapi import Depends, HTTPException, status

from app.auth.schema import PyObjectId, RegisterUserResponse

from ..service import Service, get_service
from . import router


@router.put(
    "/users/{id}", status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponse
)
def update_user(
    id: PyObjectId,
    input: RegisterUserResponse,
    svc: Service = Depends(get_service),
) -> RegisterUserResponse:
    if not svc.repository.get_user_by_email(input.email):
        error_message = f"User with email {input.email} not found"
        print(error_message)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )

    updated_user = svc.repository.update_user(input)
    return updated_user
