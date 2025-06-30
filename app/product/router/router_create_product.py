from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product.product_service import ProductService, get_product_service
from app.product.schema import ProductDB, ProductResponse
from app.product_category.product_category_service import get_product_category_service
from app.product_category.router.router_get_product_category import (
    get_product_category_by_id,
)
from app.unit.router.router_get_unit_by_id import get_unit_by_id
from app.unit.unit_service import get_unit_service

from . import router


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductResponse,
)
def create_product(
    payload: ProductResponse,
    svc: ProductService = Depends(get_product_service),
) -> ProductResponse:
    product_data = svc.repository.create_product(product=payload)
    if not product_data:
        error_message = "The Product is not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        product_data = ProductDB(**product_data)
        product_data.category = get_product_category_by_id(id=product_data.category, svc=get_product_category_service())
        product_data.unit = get_unit_by_id(id=product_data.unit, svc=get_unit_service())
        return product_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
