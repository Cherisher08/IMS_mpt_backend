from typing import Optional
from fastapi import Depends, HTTPException, status, Form, File, UploadFile
from pydantic_core import ValidationError
import json

from app.order.order_service import OrderService, get_order_service
from app.order.schema import (
    Deposit,
    ProductDetails,
    RentalOrder,
    SalesOrder,
    ServiceOrder,
    PurchaseOrder,
    PurchaseOrderProduct,
)
from app.product.schema import ProductResponse
from app.contact.utils import handle_upload, sanitize_filename
from app.utils import env

from . import router

@router.post(
    "/rentals",
    status_code=status.HTTP_201_CREATED,
    response_model=RentalOrder,
)
def create_rental_order(
    payload: RentalOrder,
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    order_data = svc.repository.create_rental_order(order=payload)
    if not order_data:
        error_message = (
            "The Rental Order is not created properly or not Found. Please try again"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data["product_details"] = [
            ProductDetails(**product_detail)
            for product_detail in order_data["product_details"]
        ]
        order_data["deposits"] = [
            Deposit(**product_detail) for product_detail in order_data["deposits"]
        ]
        return RentalOrder(**order_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error. Please Contact Admin or Developer.${e}",
        )


@router.post(
    "/sales",
    status_code=status.HTTP_201_CREATED,
    response_model=SalesOrder,
)
def create_sales_order(
    payload: SalesOrder,
    svc: OrderService = Depends(get_order_service),
) -> SalesOrder:
    order_data = svc.repository.create_sales_order(order=payload)
    if not order_data:
        error_message = (
            "The Sales Order is not created properly or not found. Please try again"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        order_data["products"] = [
            ProductResponse(**product) for product in order_data["products"]
        ]
        return SalesOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.post(
    "/service",
    status_code=status.HTTP_201_CREATED,
    response_model=ServiceOrder,
)
def create_service_order(
    payload: ServiceOrder,
    svc: OrderService = Depends(get_order_service),
) -> ServiceOrder:
    order_data = svc.repository.create_service_order(order=payload)
    if not order_data:
        error_message = "The Service order is not created properly. Please try again"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        return ServiceOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.post(
    "/purchase",
    status_code=status.HTTP_201_CREATED,
    response_model=PurchaseOrder,
)
def create_purchase_order(
    order_id: str = Form(...),
    purchase_date: str = Form(...),
    invoice_id: str = Form(default=""),
    products: str = Form(...),
    invoice_pdf: UploadFile = File(None),
    invoice_pdf_path: Optional[str] = Form(None),
    svc: OrderService = Depends(get_order_service),
    supplier: Optional[str] = Form(None),
) -> PurchaseOrder:
    """Create a purchase order with form data and optional PDF upload.

    products_json: JSON array of PurchaseOrderProduct objects
    """
    try:
        # Parse products JSON
        products_data = json.loads(products)
        products = [PurchaseOrderProduct(**p) for p in products_data]
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid products JSON: {str(e)}",
        )

    # Handle PDF upload
    invoice_pdf_path = None
    if invoice_pdf:
        try:
            pdf_filename = sanitize_filename(f"{order_id}.pdf")
            handle_upload(
                new_filename=pdf_filename,
                file=invoice_pdf,
                type="purchase",
            )
            invoice_pdf_path = f"{env.image_domain}/public/purchase/{pdf_filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to upload PDF: {str(e)}",
            )

    # Build purchase order payload
    payload_dict = {
        "order_id": order_id,
        "supplier": supplier,
        "purchase_date": purchase_date,
        "invoice_id": invoice_id,
        "products": [p.model_dump() for p in products],
        "invoice_pdf_path": invoice_pdf_path,
    }

    try:
        payload = PurchaseOrder(**payload_dict)
        
        # Process products - create new ones or increment existing
        svc.process_purchase_products(products)
        
        order_data = svc.repository.create_purchase_order(order=payload)
        if not order_data:
            error_message = (
                "The Purchase order is not created properly. Please try again"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_message
            )


        return PurchaseOrder(**order_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error: {str(e)}",
        )
