from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import env


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            request.url.path
            in [
                "/",
                "/docs",
                "/favicon.ico",
                "/openapi.json",
            ]
            or request.url.path.startswith("/auth/users")
            or request.url.path.startswith("/public")
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
            )

        token = auth_header.split("Bearer ")[1]

        try:
            jwt.decode(token, env.secret_key, algorithms="HS256")
        except JWTError:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": " Access Token is Expired or Invalid. Please Login again"
                },
            )

        response = await call_next(request)
        return response
