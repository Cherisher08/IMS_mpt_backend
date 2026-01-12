from datetime import datetime, timezone
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId
from app.utils import AppModel


class Contact(AppModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    personal_number: str
    office_number: Optional[str]
    gstin: str
    email: str
    address: str
    pincode: str
    address_proof: str
    company_name: str
    created_at: datetime = Field(
        default_factory=(lambda _: datetime.now(tz=timezone.utc))
    )


class ContactResponse(Contact):
    id: Optional[str] = Field(default=None, alias="_id")
