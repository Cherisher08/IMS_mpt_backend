from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.order.order_service import OrderService, get_order_service
from app.order.schema import (
    Deposit,
    PaymentStatus,
    ProductDetails,
    RentalOrder,
)

from . import router


@router.get(
    "/rentals/expired",
    status_code=status.HTTP_200_OK,
    response_model=List[RentalOrder],
)
def get_rental_orders(
    svc: OrderService = Depends(get_order_service),
) -> List[RentalOrder]:
    order_data = svc.repository.get_rental_orders()
    if not order_data:
        error_message = "No Rental Order Found. Please create new rental order"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        for order in order_data:
            order["product_details"] = [
                ProductDetails(**product_detail)
                for product_detail in order["product_details"]
            ]
            order["deposits"] = [
                Deposit(**product_detail) for product_detail in order["deposits"]
            ]
        order_data = [RentalOrder(**order) for order in order_data]

        now = datetime.now(timezone.utc)
        expired_orders = [
            order
            for order in order_data
            if order.out_date and (order.out_date + timedelta(days=order.rental_duration)) < now and order.status == PaymentStatus.PENDING
        ]

        if not expired_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No expired rental orders found.",
            )

        return expired_orders
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error. Please Contact Admin or Developer. ${e}",
        )
