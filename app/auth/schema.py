from datetime import datetime
from enum import Enum

from bson import ObjectId
from pydantic import GetCoreSchemaHandler, Field
from pydantic_core import core_schema
from app.utils import AppModel

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        return core_schema.json_schema(
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    def __str__(self):
        return str(super())


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class RegisterUserRequest(AppModel):
    email: str
    password: str
    name: str
    role: Role = Field(default="user")


class RegisterUserResponse(AppModel):
    id: PyObjectId = Field(alias="_id")
    email: str
    password: str
    name: str
    role: Role
    
class AuthorizeUserRequest(AppModel):
    email: str
    password: str
    
class OtpResponse(AppModel):
    id: PyObjectId = Field(alias="_id")
    otp: str
    user_id: PyObjectId
    expiration_time: datetime
    created_at: datetime
    
class ResetPasswordResponse(AppModel):
    detail: str