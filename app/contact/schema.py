from datetime import datetime, timezone
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId, Branch
from app.utils import AppModel


class Contact(AppModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    personal_number: str
    office_number: Optional[str] = Field(default="")
    gstin: Optional[str] = Field(default="")
    email: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")
    pincode: Optional[str] = Field(default="")
    address_proof: Optional[str] = Field(default="")
    company_name: Optional[str] = Field(default="")
    remarks: str = Field(default="")
    branch: Branch = Field(default=Branch.PADUR)
    created_at: datetime = Field(
        default_factory=(lambda _: datetime.now(tz=timezone.utc))
    )
    # Aadhaar eKYC fields
    aadhaar_verified: bool = Field(default=False)
    aadhaar_masked_uid: Optional[str] = Field(default=None)
    aadhaar_name: Optional[str] = Field(default=None)
    aadhaar_dob: Optional[str] = Field(default=None)
    aadhaar_gender: Optional[str] = Field(default=None)
    aadhaar_address: Optional[str] = Field(default=None)
    aadhaar_data_encrypted: Optional[str] = Field(default=None)


class ContactResponse(Contact):
    id: Optional[str] = Field(default=None, alias="_id")
