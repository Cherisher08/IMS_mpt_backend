from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product_category.schema import ProductCategory
from app.product_category.product_category_service import (
    ProductCategoryService,
    get_product_category_service,
)

from . import router


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductCategory,
)
def get_product_category_by_id(
    id: str,
    svc: ProductCategoryService = Depends(get_product_category_service),
) -> ProductCategory:
    print("svc: ", svc)
    product_category_data = svc.repository.get_product_category_by_id(
        product_category_id=id
    )
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
