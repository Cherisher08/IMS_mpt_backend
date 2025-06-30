from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product_category.product_category_service import ProductCategoryService, get_product_category_service
from app.product_category.schema import ProductCategory

from . import router


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductCategory,
)
def create_product_category(
    payload: ProductCategory,
    svc: ProductCategoryService = Depends(get_product_category_service),
) -> ProductCategory:
    product_category_data = svc.repository.create_product_category(product_category=payload)
    if not product_category_data:
        error_message = "The Product Category is not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        product_category_data = ProductCategory(**product_category_data)
        return product_category_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
