from typing import List
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.order.order_service import OrderService, get_order_service
from app.order.schema import (
    Deposit,
    ProductDetails,
    RentalOrder,
    SalesOrder,
    ServiceOrder,
)
from app.product.schema import ProductResponse

from . import router


@router.get(
    "/rentals/{id}",
    status_code=status.HTTP_200_OK,
    response_model=RentalOrder,
)
def get_rental_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    order_data = svc.repository.get_rental_order_by_id(order_id=id)
    if not order_data:
        error_message = "No Rental Order Found. Please create new rental order"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data["product_details"] = [
            ProductDetails(**product_detail)
            for product_detail in order_data["product_details"]
        ]
        order_data["deposits"] = [
            Deposit(**product_detail) for product_detail in order_data["deposits"]
        ]
        return RentalOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.get(
    "/sales/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SalesOrder,
)
def get_sales_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
) -> SalesOrder:
    order_data = svc.repository.get_sales_order_by_id(order_id=id)
    if not order_data:
        error_message = "No Sales Order Found. Please create new sales order"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data["product"] = [
            ProductResponse(**product) for product in order_data["product"]
        ]
        return SalesOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.get(
    "/service/{id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ServiceOrder],
)
def get_service_order(
    id: str,
    svc: OrderService = Depends(get_order_service),
) -> List[ServiceOrder]:
    order_data = svc.repository.get_service_order_by_id(order_id=id)
    if not order_data:
        error_message = "No Service Order Found. Please create new service order"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        return ServiceOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
