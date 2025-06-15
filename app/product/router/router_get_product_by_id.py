from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product.product_service import ProductService, get_product_service
from app.product.schema import Product

from . import router


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Product,
)
def get_product_by_id(
    id: str,
    svc: ProductService = Depends(get_product_service),
) -> Product:
    product_data = svc.repository.get_product_by_id(product_id=id)
    if not product_data:
        error_message = "The Product is not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        product_data = Product(**product_data)
        return product_data
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )
