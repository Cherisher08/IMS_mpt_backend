from typing import List, Optional
from fastapi import Depends, HTTPException, status, Query
from pydantic_core import ValidationError

from app.order.order_service import OrderService, get_order_service
from app.order.schema import Deposit, ProductDetails, RentalOrder, SalesOrder, ServiceOrder
from app.order.filters import FilterBuilder, SortBuilder
from app.product.schema import ProductResponse

from . import router


@router.get(
    "/rentals",
    status_code=status.HTTP_200_OK,
    response_model=List[RentalOrder],
)
def get_rental_orders(
    filter: Optional[List[str]] = Query(None, description="Filters as 'field:operator:value' or 'field:value'"),
    sort: Optional[List[str]] = Query(["order_id:desc"], description="Sort fields as 'field:asc' or 'field:desc'"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(1000, ge=0, le=1000, description="Number of documents to return (0 means all)"),
    svc: OrderService = Depends(get_order_service),
) -> List[RentalOrder]:
    # Build filters from query parameters
    filters = FilterBuilder.build_filters(filter) if filter else {}
    
    # Build sort specification from query parameters
    sort_spec = SortBuilder.build_sort(sort) if sort else None
    
    # Get paginated data
    order_data = svc.repository.get_rental_orders(filters=filters, sort_spec=sort_spec, skip=skip, limit=limit)
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
                Deposit(**product_detail)
                for product_detail in order["deposits"]
            ]
        order_data = [RentalOrder(**order) for order in order_data]
        return order_data
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error. Please Contact Admin or Developer. ${e}",
        )

@router.get(
    "/sales",
    status_code=status.HTTP_200_OK,
    response_model=List[SalesOrder],
)
def get_sales_orders(
    filter: Optional[List[str]] = Query(None, description="Filters as 'field:operator:value' or 'field:value'"),
    sort: Optional[List[str]] = Query(None, description="Sort fields as 'field:asc' or 'field:desc'"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(100, ge=0, le=1000, description="Number of documents to return (0 means all)"),
    svc: OrderService = Depends(get_order_service),
) -> List[SalesOrder]:
    # Build filters from query parameters
    filters = FilterBuilder.build_filters(filter) if filter else {}
    
    # Build sort specification from query parameters
    sort_spec = SortBuilder.build_sort(sort) if sort else None
    
    # Get paginated data
    order_data = svc.repository.get_sales_orders(filters=filters, sort_spec=sort_spec, skip=skip, limit=limit)
    if not order_data:
        error_message = "No Sales Order Found. Please create new sales order"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        for order in order_data:
            order["products"] = [
                ProductResponse(**product)
                for product in order["products"]
            ]
        order_data = [SalesOrder(**order) for order in order_data]
        return order_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
@router.get(
    "/service",
    status_code=status.HTTP_200_OK,
    response_model=List[ServiceOrder],
)
def get_service_orders(
    filter: Optional[List[str]] = Query(None, description="Filters as 'field:operator:value' or 'field:value'"),
    sort: Optional[List[str]] = Query(None, description="Sort fields as 'field:asc' or 'field:desc'"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(100, ge=0, le=1000, description="Number of documents to return (0 means all)"),
    svc: OrderService = Depends(get_order_service),
) -> List[ServiceOrder]:
    # Build filters from query parameters
    filters = FilterBuilder.build_filters(filter) if filter else {}
    
    # Build sort specification from query parameters
    sort_spec = SortBuilder.build_sort(sort) if sort else None
    
    # Get paginated data
    order_data = svc.repository.get_service_orders(filters=filters, sort_spec=sort_spec, skip=skip, limit=limit)
    if not order_data:
        error_message = "No Service Order Found. Please create new service order"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data = [ServiceOrder(**order) for order in order_data]
        return order_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
