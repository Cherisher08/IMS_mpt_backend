from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field


class JWTData(BaseModel):
    user_id: str = Field(alias="sub")


class JwtService:
    def __init__(
        self,
        algorithm: str,
        secret: str,
        expiration: timedelta,
    ) -> None:
        self.algorithm = algorithm
        self.secret = secret
        self.expiration = expiration

    def create_access_token(
        self,
        user: dict,
    ) -> str:
        expires_delta = timedelta(days=self.expiration)

        jwt_data = {
            "sub": str(user["_id"]),
            "exp": datetime.now(tz=timezone.utc) + expires_delta,
        }

        return jwt.encode(jwt_data, self.secret, algorithm=self.algorithm)

    def parse_jwt_user_data(self, token: str) -> Optional[JWTData]:
        if not token:
            return None

        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access Token is Expired or Invalid. Please Login again"
            )

        return JWTData(**payload)


class AuthorizationFailed(Exception):
    pass


class InvalidToken(Exception):
    pass
