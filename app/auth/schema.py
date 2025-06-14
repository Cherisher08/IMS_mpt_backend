from datetime import datetime
from enum import Enum
from typing import Any, Callable

from bson import ObjectId
from pydantic import Field
from pydantic_core import core_schema
from app.utils import AppModel

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            return ObjectId(input_value)

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

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
    
class GeneralResponse(AppModel):
    detail: str