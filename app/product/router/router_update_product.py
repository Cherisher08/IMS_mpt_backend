from fastapi import Depends, HTTPException, status
from pydantic_core import ValidationError

from app.product.product_service import ProductService, get_product_service
from app.product.schema import Product

from . import router


@router.post(
    "/{id}",
    status_code=status.HTTP_201_CREATED,
    response_model=Product,
)
def update_product(
    id: str,
    payload: Product,
    svc: ProductService = Depends(get_product_service),
) -> Product:
    product_data = svc.repository.update_product(product_id=id, product=payload)
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
