from datetime import datetime, timedelta, timezone

from bson.objectid import ObjectId
from pymongo.database import Database

from app.auth.schema import (
    OtpResponse,
    PyObjectId,
    RegisterUserRequest,
    RegisterUserResponse,
)

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

    def update_user(self, user: RegisterUserResponse):
        payload = {
            "id": user.id,
            "email": user.email,
            "password": hash_password(user.password),
            "name": user.name,
            "role": user.role.value,
            "created_at": datetime.now(tz=timezone.utc),
        }

        result = self.database["users"].update_one({"id": user.id}, payload)
        return self.get_user_by_id(result.inserted_id)

    def get_user_by_id(self, user_id: str) -> RegisterUserResponse:
        user = self.database["users"].find_one(
            {
                "_id": ObjectId(user_id),
            }
        )
        return RegisterUserResponse(**user)

    def get_user_by_email(self, email: str) -> RegisterUserResponse:
        user = self.database["users"].find_one(
            {
                "email": email,
            }
        )
        return user

    def create_otp_for_user(self, otp: str, id: PyObjectId) -> OtpResponse:
        payload = {
            "otp": otp,
            "user_id": id,
            "created_at": datetime.now(tz=timezone.utc),
            "expiration_time": datetime.now(tz=timezone.utc) + timedelta(minutes=15),
        }
        result = self.database["otp"].insert_one(payload)
        return result.inserted_id

    def delete_otp_for_user(self, id: PyObjectId) -> int:
        result = self.database["otp"].delete_one({"id": id})
        return result.deleted_count

    def get_otp_for_user(self, id: PyObjectId) -> OtpResponse:
        otp = self.database["otp"].find_one({"user_id": id})
        return otp
