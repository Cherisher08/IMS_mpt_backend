from pydantic import BaseModel


class RequestOtpBody(BaseModel):
    aadhaar_number: str
    contact_id: str


class RequestOtpResponse(BaseModel):
    client_id: str   # Surepass transaction ID to pass back for OTP submission
    message: str


class VerifyOtpBody(BaseModel):
    client_id: str   # same token returned by request-otp
    otp: str
    contact_id: str


class VerifyOtpResponse(BaseModel):
    success: bool
    message: str
    aadhaar_masked_uid: str | None = None
    aadhaar_name: str | None = None
    aadhaar_dob: str | None = None
    aadhaar_gender: str | None = None
    aadhaar_address: str | None = None
