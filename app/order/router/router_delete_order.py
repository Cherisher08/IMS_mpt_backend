from fastapi import Depends, HTTPException, Response, status

from app.order.order_service import OrderService, get_order_service

from . import router


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rental_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
):
    order_data = svc.repository.delete_rental_order_by_id(order_id=id)
    if order_data != 1:
        error_message = "The Order was not deleted. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/{id}",
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
    "/{id}",
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
