import os
from fastapi import HTTPException
from app.contact.utils import UPLOAD_DIR
from app.order.schema import PatchOperation, BillingMode
from app.dependencies import env
from app.auth.schema import Branch
import httpx
import re
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
            "name": "whatsapp_order_dc",
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


def generate_invoice_id(
    db: Database, branch: Branch = Branch.PADUR, billing_mode: BillingMode = BillingMode.B2B
) -> str:
    """
    Generate the next invoice ID based on existing invoices.

    Format: INV/{type_code}-{branch_code}/{fy}/{next_number}
    where type_code is the billing mode (B2B or B2C)
    branch_code is the branch code (e.g., PADUR-1, KLMBK-1, PUDPK-1)
    fy is the fiscal year starting year (April-based cycle)
    and next_number is 4-digit padded increment.

    Fiscal year runs from April to March:
    - If month < 4 (April), fiscal year is previous year to current year
    - If month >= 4 (April), fiscal year is current year to next year

    Branch and type-based numbering:
    - Each branch + billing type combination has its own sequential numbering
    - B2B and B2C invoices maintain separate counters (both start from 0001)
    - New format (with type and branch) applies to invoices created on or after April 1, 2026
    - Old format (without type/branch) applies to invoices created before April 1, 2026
    - Backward compatibility: Old invoices are not counted in new numbering

    Args:
        db: MongoDB database instance
        branch: Branch enum value (default: PADUR)
        billing_mode: BillingMode enum value (B2B or B2C, default: B2B)

    Returns:
        Next invoice ID as string in format: INV/B2B-PADUR-1/2025/0001
    """
    # Get current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Calculate financial year starting year (April to March)
    # If month < 4 (April), financial year starts in previous year
    financial_year = current_year - 1 if current_month < 4 else current_year

    # Check if we should use the new format (with branch)
    # New format starts from April 1, 2026
    new_format_start_date = datetime(2026, 4, 1)
    use_new_format = now >= new_format_start_date

    # Extract branch code from branch enum value
    # Branch values are like "PADUR-1", "KLMBK-1", "PUDPK-1"
    branch_code = branch.value
    
    # Extract billing mode code from enum
    # BillingMode values are "B2B" or "B2C"
    type_code = billing_mode.value

    # Query for existing invoices in the rental_orders collection
    collection = db["rental_orders"]

    if use_new_format:
        # New format with type: Query invoices for specific branch and billing mode
        # Format: INV/{type_code}-{branch_code}/ (e.g., INV/B2B-PADUR-1/)
        # This ensures B2B and B2C maintain separate numbering
        orders_with_invoices = collection.find(
            {
                "invoice_id": {"$regex": f"^INV/{type_code}-{branch_code}/"},
                "billing_mode": billing_mode.value,
            },
            {"invoice_id": 1, "_id": 0},
        )
    else:
        # Old format: Query all invoice_ids that start with "INV/"
        # Old invoices don't have type, so we don't filter by billing_mode
        orders_with_invoices = collection.find(
            {"invoice_id": {"$regex": "^INV/"}}, {"invoice_id": 1, "_id": 0}
        )

    # Extract invoice numbers and find the latest
    max_invoice_num = 0
    latest_year = financial_year

    for order in orders_with_invoices:
        invoice_id = order.get("invoice_id")
        if not invoice_id:
            continue

        if use_new_format:
            # Parse invoice_id format: INV/B2B-PADUR-1/2025/0001 or INV/PADUR-1/2024/0001 (transition)
            parts = invoice_id.split("/")
            
            # New format with type: 4 parts [INV, B2B-PADUR-1, 2025, 0001]
            # Transition format without type: 4 parts [INV, PADUR-1, 2024, 0001]
            if len(parts) == 4:
                # New format with type
                try:
                    type_branch_code = parts[1]  # e.g., "B2B-PADUR-1"
                    year = int(parts[2])
                    invoice_num = int(parts[3])

                    # Parse the type and branch from combined code
                    # Format: {type}-{branch}, e.g., "B2B-PADUR-1"
                    type_branch_parts = type_branch_code.split("-", 1)
                    if len(type_branch_parts) == 2:
                        invoice_type, invoice_branch_code = type_branch_parts
                        # Only consider invoices matching both type and branch
                        if invoice_type == type_code and invoice_branch_code == branch_code:
                            if invoice_num > max_invoice_num:
                                max_invoice_num = invoice_num
                                latest_year = year
                except (ValueError, IndexError):
                    continue
        else:
            # Old format: Parse invoice_id format: INV/2024/0001
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

    # Format and return with type code
    if use_new_format:
        return f"INV/{type_code}-{branch_code}/{result_year}/{next_invoice_num:04d}"
    else:
        return f"INV/{result_year}/{next_invoice_num:04d}"


def generate_order_id(db: Database, branch: Branch = Branch.PADUR) -> str:
    """
    Generate the next order ID based on existing rental orders.

    Format: RO/{branch_code}/{fy}/{next_number}
    where branch_code is the branch code (e.g., PADUR-1, KLMBK-1, PUDPK-1)
    fy is the fiscal year in format YY-YY (e.g., 25-26)
    and next_number is 4-digit padded increment.

    Fiscal year runs from April to March:
    - If month < 4 (April), fiscal year is previous year to current year
    - If month >= 4 (April), fiscal year is current year to next year

    Branch-based numbering:
    - Each branch has its own sequential numbering
    - New format (with branch) applies to orders created on or after April 1, 2026
    - Old format (without branch) applies to orders created before April 1, 2026
    
    Note: Order IDs may have suffixes like /A or trailing characters. The numeric
    part is extracted for comparison to find the latest order ID accurately.

    Args:
        db: MongoDB database instance
        branch: Branch enum value (default: PADUR)

    Returns:
        Next order ID as string
    """
    # Get current date
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Calculate fiscal year (April to March cycle)
    # If month < 4 (April), fiscal year is previous year to current year
    # If month >= 4 (April), fiscal year is current year to next year
    start_year = current_year - 1 if current_month < 4 else current_year
    end_year = start_year + 1
    fy = f"{str(start_year)[-2:]}-{str(end_year)[-2:]}"

    # Check if we should use the new format (with branch)
    # New format starts from April 1, 2026
    new_format_start_date = datetime(2026, 4, 1)
    use_new_format = now >= new_format_start_date

    # Extract branch code from branch enum value
    # Branch values are like "PADUR-1", "KLMBK-1", "PUDPK-1"
    branch_code = branch.value

    # Query for existing order IDs in the rental_orders collection
    collection = db["rental_orders"]

    if use_new_format:
        # New format: Query only orders for the specific branch
        # Look for order_ids that start with "RO/{branch_code}/"
        orders_with_ids = collection.find(
            {"order_id": {"$regex": f"^RO/{branch_code}/"}}, {"order_id": 1, "_id": 0}
        )
    else:
        # Old format: Query all order_ids that start with "RO/"
        orders_with_ids = collection.find(
            {"order_id": {"$regex": "^RO/"}}, {"order_id": 1, "_id": 0}
        )

    # Extract order numbers and find the latest
    max_order_num = 0
    latest_fy = fy

    for order in orders_with_ids:
        order_id = order.get("order_id")
        if not order_id:
            continue

        if use_new_format:
            # Parse order_id format: RO/PADUR-1/25-26/0001 or with suffixes like RO/PADUR-1/25-26/0001/A
            parts = order_id.split("/")
            if len(parts) < 4:
                continue

            try:
                order_branch_code = parts[1]
                order_fy = parts[2]
                # Extract numeric part from the order number (handles suffixes like /A)
                order_num_str = parts[3]
                
                # If there are more parts (e.g., 0001/A), join the remaining parts
                if len(parts) > 4:
                    order_num_str = "/".join(parts[3:])
                
                # Extract only the leading numeric digits
                numeric_match = re.match(r"^(\d+)", order_num_str)
                if not numeric_match:
                    continue
                
                order_num = int(numeric_match.group(1))

                # Only consider orders for the same branch
                if order_branch_code == branch_code:
                    # Track the highest order number found
                    if order_num > max_order_num:
                        max_order_num = order_num
                        latest_fy = order_fy
            except (ValueError, IndexError, AttributeError):
                # Skip invalid order IDs
                continue
        else:
            # Old format: Parse order_id format: RO/25-26/0001 or with suffixes like RO/25-26/0001/A
            parts = order_id.split("/")
            if len(parts) < 3:
                continue

            try:
                order_fy = parts[1]
                # Extract numeric part from the order number (handles suffixes like /A)
                order_num_str = parts[2]
                
                # If there are more parts (e.g., 0001/A), join the remaining parts
                if len(parts) > 3:
                    order_num_str = "/".join(parts[2:])
                
                # Extract only the leading numeric digits
                numeric_match = re.match(r"^(\d+)", order_num_str)
                if not numeric_match:
                    continue
                
                order_num = int(numeric_match.group(1))

                # Track the highest order number found
                if order_num > max_order_num:
                    max_order_num = order_num
                    latest_fy = order_fy
            except (ValueError, IndexError, AttributeError):
                # Skip invalid order IDs
                continue

    # Generate next order number
    next_order_num = max_order_num + 1

    # Use the latest fiscal year found, or current fiscal year if no orders exist
    result_fy = latest_fy if max_order_num > 0 else fy

    # Format and return
    if use_new_format:
        return f"RO/{branch_code}/{result_fy}/{next_order_num:04d}"
    else:
        return f"RO/{result_fy}/{next_order_num:04d}"


def calculate_final_amount(order: dict) -> float:
    """
    Calculate the final amount for a rental order.
    Mirrors the frontend calculateFinalAmount function.

    Formula:
    final_amount = (total_amount - discount + gst + round_off + eway_amount + damage_expenses) - balance_paid
    """
    # Calculate total amount from product details
    total_amount = 0.0
    for product in order.get("product_details", []):
        quantity = product.get("order_quantity", 0)
        duration = product.get("duration", 0)
        rent_per_unit = product.get("rent_per_unit", 0)
        total_amount += quantity * duration * rent_per_unit

    # Get other components
    discount = order.get("discount", 0)
    discount_type = order.get("discount_type", "RUPEES")
    gst_percentage = order.get("gst", 18) if order.get("gst") else 18
    round_off = order.get("round_off", 0)
    eway_amount = order.get("eway_amount", 0)
    damage_expenses = order.get("damage_expenses", 0)
    balance_paid = order.get("balance_paid", 0)
    billing_mode = order.get("billing_mode", "B2C")

    # Calculate discount amount
    if discount_type == "PERCENT":
        discount_amount = (total_amount * discount) / 100
    else:
        discount_amount = discount

    # Calculate GST (only for B2B)
    if billing_mode == "B2B":
        transport_for_tax = eway_amount
        gst_amount = ((total_amount + transport_for_tax - discount_amount) * gst_percentage) / 100
    else:
        gst_amount = 0

    # Calculate final amount
    final_amount = (total_amount - discount_amount + gst_amount + round_off + eway_amount + damage_expenses) - balance_paid

    return round(final_amount, 2)
