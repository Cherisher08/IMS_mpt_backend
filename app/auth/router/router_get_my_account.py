
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.auth.schema import RegisterUserResponse

from ..adapters.jwt_service import JWTData
from ..service import Service, get_service
from . import router
from .dependencies import parse_jwt_user_data


@router.get("/users/me", response_model=RegisterUserResponse)
def get_my_account(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
) -> RegisterUserResponse:
    user = svc.repository.get_user_by_id(jwt_data.user_id)
    try:
        user = RegisterUserResponse(**user)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
    return user
