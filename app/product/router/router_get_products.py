from typing import List
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product.product_service import ProductService, get_product_service
from app.product.schema import Product

from . import router


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[Product],
)
def get_products(
    svc: ProductService = Depends(get_product_service),
) -> List[Product]:
    product_data = svc.repository.get_products()
    if not product_data:
        error_message = "No Products Found. Please create new product"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        product_data = [Product(**product) for product in product_data]
        return product_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
