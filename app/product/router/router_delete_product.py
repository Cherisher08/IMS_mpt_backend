from fastapi import Depends, HTTPException, Response, status

from app.product.product_service import ProductService, get_product_service

from . import router


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    id: str,
    svc: ProductService = Depends(get_product_service),
):
    product_data = svc.repository.delete_product_by_id(product_id=id)
    if product_data != 1:
        error_message = "The Product was not deleted. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
