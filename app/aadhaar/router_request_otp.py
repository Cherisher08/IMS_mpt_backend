"""
POST /aadhaar/request-otp

Sends an Aadhaar OTP to the mobile number registered with UIDAI for the
given Aadhaar number. Uses the Surepass eKYC API.

Returns a `client_id` (Surepass transaction token) that the frontend
must supply when calling /aadhaar/verify-otp.
"""
import httpx
from fastapi import Depends, HTTPException, status

from app.aadhaar.schema import RequestOtpBody, RequestOtpResponse
from app.aadhaar.utils import surepass_send_otp
from app.contact.contact_repository import ContactRepository
from app.config import database
from . import router


def get_contact_repository() -> ContactRepository:
    return ContactRepository(database=database)


@router.post(
    "/request-otp",
    response_model=RequestOtpResponse,
    status_code=status.HTTP_200_OK,
)
def request_aadhaar_otp(
    body: RequestOtpBody,
    repo: ContactRepository = Depends(get_contact_repository),
):
    """Trigger an Aadhaar OTP for the customer's Aadhaar-linked mobile number."""
    # Validate the contact exists
    contact = repo.get_contact_by_id(body.contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    # Validate Aadhaar number format (12 digits)
    aadhaar = body.aadhaar_number.strip()
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Aadhaar number must be exactly 12 digits",
        )

    try:
        result = surepass_send_otp(aadhaar_number=aadhaar)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Surepass OTP request failed: {exc.response.text}",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach Surepass API: {exc}",
        )

    # Surepass returns: {"success": true, "data": {"client_id": "..."}, ...}
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "OTP request failed"),
        )

    client_id = result.get("data", {}).get("client_id", "")
    return RequestOtpResponse(
        client_id=client_id,
        message="OTP sent to the Aadhaar-linked mobile number",
    )
