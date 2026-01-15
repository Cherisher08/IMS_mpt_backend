from fastapi import HTTPException, status, UploadFile, File, Form
import re
import asyncio

from app.contact.utils import handle_upload, sanitize_filename
from app.contact.contact_repository import ContactRepository
from app.config import database
from app.order.utils import send_festive_message, upload_media_to_whatsapp

from . import router


@router.post(
    "/festive-wishes",
    status_code=status.HTTP_200_OK,
)
async def send_festive_wishes_to_all(
    customer_name_template: str = Form(...),
    message_title: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Send festive wishes with an image to all customers.
    
    Args:
        customer_name_template: Template for personalizing message (e.g., "Dear {name}")
        message_title: Title or heading for the festive message
        file: Image file to send with the message
    
    Returns:
        Summary of sent messages with success/failure counts
    """
    file_name = sanitize_filename(f"{file.filename}")
    handle_upload(new_filename=file_name, file=file, type="order")

    try:
        # Upload media to WhatsApp
        file_id = upload_media_to_whatsapp(file_name=file_name)
        print("file_id: ", file_id)

        # Get all contacts from database
        contact_repository = ContactRepository(database=database)
        contacts = contact_repository.get_contacts()

        if not contacts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No contacts found in the system",
            )

        # Send messages to all customers
        success_count = 0
        failed_count = 0
        failed_contacts = []

        for contact in contacts:
            try:
                mobile_number = contact.get("personal_number")
                
                if not mobile_number:
                    failed_count += 1
                    failed_contacts.append(
                        {
                            "name": contact.get("name"),
                            "reason": "No phone number available",
                        }
                    )
                    continue

                # Format mobile number
                if not mobile_number.startswith("+"):
                    mobile_number = "+91" + mobile_number

                # Personalize customer name
                customer_name = customer_name_template.format(
                    name=contact.get("name", "Valued Customer")
                )
                customer_name = re.sub(r"[\x00-\x1f\x7f]+", " ", customer_name)
                customer_name = re.sub(r"\s+", " ", customer_name).strip()

                send_festive_message(
                    mobile_number=mobile_number,
                    customer_name=customer_name,
                    message_title=message_title,
                    file_id=file_id,
                )

                success_count += 1

            except Exception as e:
                failed_count += 1
                failed_contacts.append(
                    {
                        "name": contact.get("name"),
                        "reason": str(e),
                    }
                )
                print(
                    f"Error sending message to {contact.get('name')}: {e}"
                )

        return {
            "detail": "Festive wishes campaign completed",
            "success_count": success_count,
            "failed_count": failed_count,
            "total_contacts": len(contacts),
            "failed_contacts": failed_contacts if failed_contacts else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in festive wishes campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send festive wishes: {str(e)}",
        )
