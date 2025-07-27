from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from pydantic import ValidationError
from app.order.schema import (
    Deposit,
    PatchOperation,
    ProductDetails,
    RentalOrder,
)
from app.order.order_service import OrderService, get_order_service
from app.order.utils import apply_patch_operation

from . import router


@router.patch(
    "/rentals/{id}",
    status_code=status.HTTP_200_OK,
    response_model=RentalOrder,
)
def patch_rental_order(
    id: str,
    operations: List[PatchOperation],
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    # Step 1: Get the existing order
    existing_order = svc.repository.get_rental_order_by_id(id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Rental Order not found.")

    for op in operations:
        apply_patch_operation(existing_order, op)
        
    try:
        existing_order["product_details"] = [
            ProductDetails(**product_detail)
            for product_detail in existing_order["product_details"]
        ]
        existing_order["deposits"] = [
            Deposit(**deposit) for deposit in existing_order["deposits"]
        ]
        print('existing_order["deposits"]: ', existing_order["deposits"])
        order = RentalOrder(**existing_order)
    except ValidationError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )

    updated_order = svc.repository.update_rental_order(
        order_id=id, order=order
    )
    if not updated_order:
        raise HTTPException(status_code=404, detail="Failed to update rental order.")

    try:
        updated_order["product_details"] = [
            ProductDetails(**pd) for pd in updated_order.get("product_details", [])
        ]
        updated_order["deposits"] = [
            Deposit(**dp) for dp in updated_order.get("deposits", [])
        ]
        return RentalOrder(**updated_order)
    except ValidationError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please contact the admin or developer.",
        )
