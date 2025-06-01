from datetime import datetime, timezone
from typing import Optional

from bson.objectid import ObjectId
from pymongo.database import Database

from app.auth.schema import RegisterUserRequest, RegisterUserResponse

from ..utils.security import hash_password


class AuthRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_user(self, user: RegisterUserRequest):
        payload = {
            "email": user.email,
            "password": hash_password(user.password),
            "name": user.name,
            "role": user.role.value,
            "created_at": datetime.now(tz=timezone.utc),
        }

        result = self.database["users"].insert_one(payload)
        return self.get_user_by_id(result.inserted_id)

    def get_user_by_id(self, user_id: str) -> RegisterUserResponse:
        user = self.database["users"].find_one(
            {
                "_id": ObjectId(user_id),
            }
        )
        return RegisterUserResponse(**user)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        user = self.database["users"].find_one(
            {
                "email": email,
            }
        )
        return user
