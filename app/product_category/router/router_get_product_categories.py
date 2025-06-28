from typing import List
from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product_category.product_category_service import ProductCategoryService, get_product_category_service
from app.product_category.schema import ProductCategory


from . import router


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[ProductCategory],
)
def get_product_categories(
    svc: ProductCategoryService = Depends(get_product_category_service),
) -> List[ProductCategory]:
    product_category_data = svc.repository.get_product_categories()
    if not product_category_data:
        error_message = "No Product categories Found. Please create new product category"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        product_category_data = [ProductCategory(**product) for product in product_category_data]
        return product_category_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
