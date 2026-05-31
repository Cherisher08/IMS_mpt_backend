"""
POST /aadhaar/verify-otp

Submits the OTP entered by the customer to Surepass. On success:
  - Parses the returned demographic data (name, DOB, gender, masked UID, address)
  - Encrypts the raw payload with AES-256-GCM
  - Patches the contact document in MongoDB with all aadhaar_* fields
  - Returns the masked/safe demographic fields to the UI
"""
import httpx
from fastapi import Depends, HTTPException, status

from app.aadhaar.schema import VerifyOtpBody, VerifyOtpResponse
from app.aadhaar.utils import encrypt_aadhaar_data, surepass_verify_otp
from app.contact.contact_repository import ContactRepository
from app.config import database
from . import router


def get_contact_repository() -> ContactRepository:
    return ContactRepository(database=database)


@router.post(
    "/verify-otp",
    response_model=VerifyOtpResponse,
    status_code=status.HTTP_200_OK,
)
def verify_aadhaar_otp(
    body: VerifyOtpBody,
    repo: ContactRepository = Depends(get_contact_repository),
):
    """Verify the Aadhaar OTP, fetch demographics, and persist to the contact."""
    # Validate the contact exists
    contact = repo.get_contact_by_id(body.contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    try:
        result = surepass_verify_otp(client_id=body.client_id, otp=body.otp)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Surepass OTP verification failed: {exc.response.text}",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach Surepass API: {exc}",
        )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "OTP verification failed"),
        )

    # Parse Surepass response
    # Surepass data shape: result["data"] contains the demographic fields
    data = result.get("data", {})

    masked_uid: str = data.get("aadhaar_number", "")  # already masked by Surepass
    full_name: str = data.get("full_name", "")
    dob: str = data.get("dob", "")
    gender: str = data.get("gender", "")

    # Build address string from the address object
    addr_obj: dict = data.get("address", {}) or {}
    address_parts = [
        addr_obj.get("house", ""),
        addr_obj.get("street", ""),
        addr_obj.get("landmark", ""),
        addr_obj.get("loc", ""),
        addr_obj.get("vtc", ""),
        addr_obj.get("dist", ""),
        addr_obj.get("state", ""),
        addr_obj.get("country", ""),
        addr_obj.get("zip", ""),
    ]
    aadhaar_address = ", ".join(p for p in address_parts if p)

    # Encrypt and persist
    raw_payload = {
        "full_name": full_name,
        "dob": dob,
        "gender": gender,
        "masked_uid": masked_uid,
        "address": aadhaar_address,
        "raw": data,  # full Surepass data blob
    }
    encrypted_blob = encrypt_aadhaar_data(raw_payload)

    aadhaar_patch = {
        "aadhaar_verified": True,
        "aadhaar_masked_uid": masked_uid,
        "aadhaar_name": full_name,
        "aadhaar_dob": dob,
        "aadhaar_gender": gender,
        "aadhaar_address": aadhaar_address,
        "aadhaar_data_encrypted": encrypted_blob,
    }
    repo.patch_aadhaar_data(contact_id=body.contact_id, aadhaar_patch=aadhaar_patch)

    return VerifyOtpResponse(
        success=True,
        message="Aadhaar verified successfully",
        aadhaar_masked_uid=masked_uid,
        aadhaar_name=full_name,
        aadhaar_dob=dob,
        aadhaar_gender=gender,
        aadhaar_address=aadhaar_address,
    )
