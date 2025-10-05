from fastapi import HTTPException, status, UploadFile, File, Form

from app.contact.utils import handle_upload
from app.order.utils import send_whatsapp_message_with_pdf, upload_media_to_whatsapp

from . import router


# ...existing imports...


@router.post(
    "/rentals/whatsapp-dc",
    status_code=status.HTTP_200_OK,
)
async def whatsapp_order_dc(
    mobile_number: str = Form(...),
    customer_name: str = Form(...),
    order_id: str = Form(...),
    pdf_file: UploadFile = File(...),
):
    file_name = f"temp_{pdf_file.filename}"
    handle_upload(new_filename=file_name, file=pdf_file, type="order")

    try:
        file_id = upload_media_to_whatsapp(file_name=file_name)
        print("file_id: ", file_id)

        if not mobile_number.startswith("+"):
            mobile_number = "91" + mobile_number

        send_whatsapp_message_with_pdf(
            mobile_number=mobile_number,
            customer_name=customer_name,
            order_id=order_id,
            file_id=file_id,
            file_name=file_name,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send WhatsApp message: {str(e)}",
        )

    return {"detail": "WhatsApp message sent successfully."}
