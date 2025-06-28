from typing import List
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


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[ProductResponse],
)
def get_products(
    svc: ProductService = Depends(get_product_service),
) -> List[ProductResponse]:
    product_data = svc.repository.get_products()
    if not product_data:
        error_message = "No Products Found. Please create new product"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        product_data = [ProductDB(**product) for product in product_data]
        print('product_data: ', product_data)
        for product in product_data:
            product.category = get_product_category_by_id(id=product.category, svc=get_product_category_service())
            product.unit = get_unit_by_id(id=product.unit, svc=get_unit_service())
        return product_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
