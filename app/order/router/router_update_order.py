from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.order.order_service import OrderService, get_order_service
from app.order.schema import (
    Deposit,
    ProductDetails,
    RentalOrder,
    SalesOrder,
    ServiceOrder,
    PurchaseOrder,
)
from app.product.schema import ProductResponse

from . import router


@router.put(
    "/rentals/{id}",
    status_code=status.HTTP_200_OK,
    response_model=RentalOrder,
)
def update_rental_order(
    id: str,
    payload: RentalOrder,
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    order_data = svc.repository.update_rental_order(order_id=id, order=payload)
    if not order_data:
        error_message = (
            "The Rental Order was not updated properly. Please verify and try again"
        )
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


@router.put(
    "/sales/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SalesOrder,
)
def update_sales_order(
    id: str,
    payload: SalesOrder,
    svc: OrderService = Depends(get_order_service),
) -> SalesOrder:
    order_data = svc.repository.update_sales_order(order_id=id, order=payload)
    if not order_data:
        error_message = (
            "The Sales Order was not updated properly. Please verify and try again"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data["products"] = [
            ProductResponse(**product) for product in order_data["products"]
        ]
        return SalesOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.put(
    "/service/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ServiceOrder,
)
def update_service_order(
    id: str,
    payload: ServiceOrder,
    svc: OrderService = Depends(get_order_service),
) -> ServiceOrder:
    order_data = svc.repository.update_service_order(order_id=id, order=payload)
    if not order_data:
        error_message = "The Service Order was not updated properly. Please verify and try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        return ServiceOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.put(
    "/purchase/{id}",
    status_code=status.HTTP_200_OK,
    response_model=PurchaseOrder,
)
def update_purchase_order(
    id: str,
    payload: PurchaseOrder,
    svc: OrderService = Depends(get_order_service),
) -> PurchaseOrder:
    order_data = svc.repository.update_purchase_order(order_id=id, order=payload)
    if not order_data:
        error_message = "The Purchase Order was not updated properly. Please verify and try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data["products"] = [
            ProductResponse(**product) for product in order_data["products"]
        ]
        return PurchaseOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
