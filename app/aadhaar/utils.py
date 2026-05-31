"""
Aadhaar eKYC utilities:
- AES-256-GCM encryption / decryption of sensitive Aadhaar data
- Surepass REST API client wrappers (send OTP, verify OTP)
"""
import base64
import os
import json
from typing import Any

import httpx

from app.dependencies import env

# ---------------------------------------------------------------------------
# Encryption helpers (AES-256-GCM via cryptography library)
# ---------------------------------------------------------------------------
_ENCRYPT_KEY_AVAILABLE = False
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _raw_key = env.aadhaar_encrypt_key.encode()
    # Derive a 32-byte key via zero-padding or truncation (use PBKDF2 in prod)
    _AES_KEY = (_raw_key + b"\x00" * 32)[:32]
    _ENCRYPT_KEY_AVAILABLE = True
except Exception:
    _AES_KEY = None  # type: ignore


def encrypt_aadhaar_data(data: dict) -> str:
    """Encrypt a dict of Aadhaar data and return a base64-encoded string."""
    if not _ENCRYPT_KEY_AVAILABLE or _AES_KEY is None:
        return json.dumps(data)  # fallback: plaintext (dev only)
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    nonce = os.urandom(12)
    aesgcm = AESGCM(_AES_KEY)
    plaintext = json.dumps(data).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_aadhaar_data(token: str) -> dict:
    """Decrypt a base64-encoded AES-GCM token back to a dict."""
    if not _ENCRYPT_KEY_AVAILABLE or _AES_KEY is None:
        return json.loads(token)
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    raw = base64.b64decode(token.encode())
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(_AES_KEY)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())


# ---------------------------------------------------------------------------
# Surepass API client
# ---------------------------------------------------------------------------
SUREPASS_BASE = "https://kyc-api.surepass.io/api/v1"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {env.surepass_api_token}",
        "Content-Type": "application/json",
    }


def surepass_send_otp(aadhaar_number: str) -> dict[str, Any]:
    """
    Call Surepass to dispatch an OTP to the Aadhaar-linked mobile.
    Returns the full Surepass response dict.
    Raises httpx.HTTPStatusError on non-2xx.
    """
    url = f"{SUREPASS_BASE}/aadhaar-v2/generate-otp"
    payload = {"id_number": aadhaar_number}
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()


def surepass_verify_otp(client_id: str, otp: str) -> dict[str, Any]:
    """
    Submit the OTP received on the customer's phone to Surepass.
    Returns the Surepass response containing Aadhaar demographic data.
    Raises httpx.HTTPStatusError on non-2xx.
    """
    url = f"{SUREPASS_BASE}/aadhaar-v2/submit-otp"
    payload = {"client_id": client_id, "otp": otp}
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()
