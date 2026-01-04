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


@router.post(
    "/rentals",
    status_code=status.HTTP_201_CREATED,
    response_model=RentalOrder,
)
def create_rental_order(
    payload: RentalOrder,
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    order_data = svc.repository.create_rental_order(order=payload)
    if not order_data:
        error_message = (
            "The Rental Order is not created properly or not Found. Please try again"
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
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error. Please Contact Admin or Developer.${e}",
        )


@router.post(
    "/sales",
    status_code=status.HTTP_201_CREATED,
    response_model=SalesOrder,
)
def create_sales_order(
    payload: SalesOrder,
    svc: OrderService = Depends(get_order_service),
) -> SalesOrder:
    order_data = svc.repository.create_sales_order(order=payload)
    if not order_data:
        error_message = (
            "The Sales Order is not created properly or not found. Please try again"
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


@router.post(
    "/service",
    status_code=status.HTTP_201_CREATED,
    response_model=ServiceOrder,
)
def create_service_order(
    payload: ServiceOrder,
    svc: OrderService = Depends(get_order_service),
) -> ServiceOrder:
    order_data = svc.repository.create_service_order(order=payload)
    if not order_data:
        error_message = "The Service order is not created properly. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        return ServiceOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.post(
    "/purchase",
    status_code=status.HTTP_201_CREATED,
    response_model=PurchaseOrder,
)
def create_purchase_order(
    payload: PurchaseOrder,
    svc: OrderService = Depends(get_order_service),
) -> PurchaseOrder:
    order_data = svc.repository.create_purchase_order(order=payload)
    if not order_data:
        error_message = "The Purchase order is not created properly. Please try again"
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
