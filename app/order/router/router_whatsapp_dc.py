from fastapi import HTTPException, status, UploadFile, File, Form
import re

from app.contact.utils import handle_upload, sanitize_filename
from app.order.utils import send_whatsapp_message_with_img, upload_media_to_whatsapp

from . import router


@router.post(
    "/rentals/whatsapp-dc",
    status_code=status.HTTP_200_OK,
)
async def whatsapp_order_dc(
    mobile_number: str = Form(...),
    customer_name: str = Form(...),
    bill_type: str = Form(...),
    order_id: str = Form(...),
    file: UploadFile = File(...),
):
    file_name = sanitize_filename(f"{file.filename}")
    handle_upload(new_filename=file_name, file=file, type="order")

    # sanitize customer name: remove control/escape characters and collapse whitespace
    # removes characters like \n, \r, \t and other control chars
    customer_name = re.sub(r"[\x00-\x1f\x7f]+", " ", customer_name)
    customer_name = re.sub(r"\s+", " ", customer_name).strip()

    try:
        file_id = upload_media_to_whatsapp(file_name=file_name)
        print("file_id: ", file_id)

        if not mobile_number.startswith("+"):
            mobile_number = "91" + mobile_number

        send_whatsapp_message_with_img(
            mobile_number=mobile_number,
            customer_name=customer_name,
            order_id=order_id,
            file_id=file_id,
            bill_type=bill_type,
        )
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send WhatsApp message: {str(e)}",
        )

    return {"detail": "WhatsApp message sent successfully."}
