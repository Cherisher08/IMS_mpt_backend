from fastapi import Depends, HTTPException, status

from app.order.order_service import OrderService, get_order_service
from app.order.schema import RentalOrder, Deposit, ProductDetails
from pydantic_core import ValidationError

from . import router


@router.post(
    "/rentals/{id}/sync-products",
    status_code=status.HTTP_200_OK,
    response_model=RentalOrder,
)
def sync_rental_order_products(
    id: str,
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    """Sync rental order product_details with latest product catalog data.

    Updates each product in the rental order with the latest data from the
    product catalog, while preserving order-specific fields like quantity,
    dates, and damage information.
    """
    order_data = svc.sync_rental_order_products(order_id=id)

    if not order_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental order not found or could not be synced",
        )

    try:
        # Validate and return the response
        order_data["product_details"] = [
            ProductDetails(**product_detail)
            for product_detail in order_data["product_details"]
        ]
        order_data["deposits"] = [
            Deposit(**deposit) for deposit in order_data.get("deposits", [])
        ]
        return RentalOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
