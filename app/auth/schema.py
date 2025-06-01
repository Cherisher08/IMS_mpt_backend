from enum import Enum

from bson import ObjectId
from pydantic import Field
from app.utils import AppModel


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class RegisterUserRequest(AppModel):
    email: str
    password: str
    name: str
    role: Role = Field(default="user")


class RegisterUserResponse(AppModel):
    id: ObjectId = Field(alias="_id")
    email: str
    password: str
    name: str
    role: Role