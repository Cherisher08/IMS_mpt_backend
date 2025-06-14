from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schema import AuthorizeUserRequest
from app.utils import AppModel

from ..service import Service, get_service
from ..utils.security import check_password
from . import router


class AuthorizeUserResponse(AppModel):
    access_token: str
    token_type: str = "Bearer"
    
class OauthUserRequest(AppModel):
    username: str
    password: str 
    
@router.post("/users/tokens", response_model=AuthorizeUserResponse)
def authorize_user_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    svc: Service = Depends(get_service),
) -> AuthorizeUserResponse:
    user = svc.repository.get_user_by_email(form_data.username)

    if not user:
        error_message = f"User with email {form_data.username} not found"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )

    if not check_password(form_data.password, user["password"]):
        error_message = "Entered Password is incorrect"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )


    return AuthorizeUserResponse(
        access_token=svc.jwt_svc.create_access_token(user=user),
    )
