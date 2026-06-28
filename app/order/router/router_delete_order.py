import os
from fastapi import Depends, HTTPException, Response, status

from app.order.order_service import OrderService, get_order_service
from app.contact.utils import UPLOAD_DIR

from . import router


@router.delete(
    "/rentals/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rental_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
):
    current_order = svc.repository.get_rental_order_by_id(order_id=id)
    order_data = svc.repository.delete_rental_order_by_id(order_id=id)
    if order_data != 1:
        error_message = "The Order was not deleted. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    # Clean up associated site images from disk
    if current_order and "delivery_site_images" in current_order and current_order["delivery_site_images"]:
        for img in current_order["delivery_site_images"]:
            if img:
                filename = os.path.basename(img)
                file_path = os.path.join(UPLOAD_DIR, "order", filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Failed to delete site image {file_path}: {e}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/sales/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sales_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
):
    order_data = svc.repository.delete_sales_order_by_id(order_id=id)
    if order_data != 1:
        error_message = "The Order was not deleted. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/service/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
):
    order_data = svc.repository.delete_service_order_by_id(order_id=id)
    if order_data != 1:
        error_message = "The Order was not deleted. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/purchase/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_purchase_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
):
    order_data = svc.repository.delete_purchase_order_by_id(order_id=id)
    if order_data != 1:
        error_message = "The Order was not deleted. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
