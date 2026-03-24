import os
from fastapi import HTTPException
from app.contact.utils import UPLOAD_DIR
from app.order.schema import PatchOperation
from app.dependencies import env
import httpx
from pymongo.database import Database
from datetime import datetime

access_token = env.access_token
phone_number_id = env.phone_number_id
version = env.version


def apply_patch_operation(doc: dict, operation: PatchOperation):
    path_parts = [p for p in operation.path.strip("/").split("/") if p]

    def traverse(target, parts):
        """Navigate to the parent of the last key."""
        for i, part in enumerate(parts[:-1]):
            if isinstance(target, list):
                part = int(part)
            target = target[part]
        return target, parts[-1]

    try:
        parent, final_key = traverse(doc, path_parts)

        # Convert to int if the parent is a list
        if isinstance(parent, list):
            final_key = int(final_key)

            # Handle add operation
        if operation.op == "add":
            # Case: Adding to a list directly
            if isinstance(parent, list):
                if isinstance(final_key, int) and final_key <= len(parent):
                    parent.insert(final_key, operation.value)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid index '{final_key}' for list at path '{operation.path}'",
                    )

            # Case: Appending to list if path is e.g., /list and list exists
            elif isinstance(parent.get(final_key), list):
                parent[final_key].append(operation.value)

            # Case: Normal add to dict
            else:
                parent[final_key] = operation.value

        if operation.op == "replace":
            parent[final_key] = operation.value

        elif operation.op == "remove":
            if isinstance(parent, list):
                parent.pop(final_key)
            else:
                parent.pop(final_key, None)

    except (KeyError, IndexError, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error applying patch at path '{operation.path}': {str(e)}",
        )


def upload_media_to_whatsapp(file_name: str):
    if not access_token or not phone_number_id:
        raise ValueError("Missing WhatsApp configuration in environment variables.")

    url = f"https://graph.facebook.com/{version}/{phone_number_id}/media"
    file_path = os.path.join(UPLOAD_DIR, "order", file_name)
    with open(file_path, "rb") as f:
        headers = {"Authorization": f"Bearer {access_token}"}
        files = {"file": (file_name, f, "image/png")}
        data = {"messaging_product": "whatsapp"}
        response = httpx.post(url, headers=headers, data=data, files=files)
        print("response: ", response)
        response.raise_for_status()

    return response.json().get("id")  # Return media ID


def send_whatsapp_message_with_img(
    mobile_number: str, customer_name: str, order_id: str, file_id: str, bill_type: str
):
    if not access_token or not phone_number_id:
        raise ValueError("Missing WhatsApp configuration in environment variables.")

    media_url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": mobile_number,
        "type": "template",
        "template": {
            "name": "send_order_dc",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "parameter_name": "header_handle",
                            "image": {
                                "id": file_id,
                            },
                        },
                    ],
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "parameter_name": "customer_name",
                            "text": customer_name,
                        },
                        {
                            "type": "text",
                            "parameter_name": "bill",
                            "text": bill_type,
                        },
                        {
                            "type": "text",
                            "parameter_name": "order_id",
                            "text": order_id,
                        },
                    ],
                },
            ],
        },
    }

    media_response = httpx.post(
        media_url,
        headers=headers,
        json=data,
        timeout=60,
    )

    if media_response.status_code != 200:
        print("Request data: ", data)
        print("Headers: ", headers)
        print("URL: ", media_url)
    media_response.raise_for_status()

    return media_response.json()


def send_festive_message(
    mobile_number: str, customer_name: str, message_title: str, file_id: str
):
    """
    Send a festive wishes message with an image to a customer.

    Args:
        mobile_number: Customer's phone number with country code
        customer_name: Personalized customer name for the message
        message_title: Title/heading of the festive message
        file_id: WhatsApp media ID of the image to send
    """
    if not access_token or not phone_number_id:
        raise ValueError("Missing WhatsApp configuration in environment variables.")

    media_url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": mobile_number,
        "type": "template",
        "template": {
            "name": "festive_wishes",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "parameter_name": "header_handle",
                            "image": {
                                "id": file_id,
                            },
                        },
                    ],
                },
            ],
        },
    }

    media_response = httpx.post(
        media_url,
        headers=headers,
        json=data,
        timeout=60,
    )

    if media_response.status_code != 200:
        print("Request data: ", data)
        print("Headers: ", headers)
        print("URL: ", media_url)
    media_response.raise_for_status()

    return media_response.json()


def generate_invoice_id(db: Database) -> str:
    """
    Generate the next invoice ID based on existing invoices.

    Format: INV/{year}/{next_number}
    where year is the financial year starting year (April-based cycle)
    and next_number is 4-digit padded increment.

    Args:
        db: MongoDB database instance

    Returns:
        Next invoice ID as string
    """
    # Get current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Calculate financial year starting year (April to March)
    # If month < 4 (April), financial year starts in previous year
    financial_year = current_year - 1 if current_month < 4 else current_year

    # Query for existing invoices in the rental_orders collection
    # Look for invoice_ids that start with "INV/"
    collection = db["rental_orders"]
    orders_with_invoices = collection.find(
        {"invoice_id": {"$regex": "^INV/"}},
        {"invoice_id": 1, "_id": 0}
    )

    # Extract invoice numbers and find the latest
    max_invoice_num = 0
    latest_year = financial_year

    for order in orders_with_invoices:
        invoice_id = order.get("invoice_id")
        if not invoice_id:
            continue

        # Parse invoice_id format: INV/2024/0001
        parts = invoice_id.split("/")
        if len(parts) != 3:
            continue

        try:
            year = int(parts[1])
            invoice_num = int(parts[2])

            # Track the highest invoice number found
            if invoice_num > max_invoice_num:
                max_invoice_num = invoice_num
                latest_year = year
        except (ValueError, IndexError):
            # Skip invalid invoice IDs
            continue

    # Generate next invoice number
    next_invoice_num = max_invoice_num + 1

    # Use the latest year found, or current financial year if no invoices exist
    result_year = latest_year if max_invoice_num > 0 else financial_year

    # Format and return
    return f"INV/{result_year}/{next_invoice_num:04d}"
