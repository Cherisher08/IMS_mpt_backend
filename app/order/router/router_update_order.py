from typing import Optional
from fastapi import Depends, HTTPException, status, Form, File, UploadFile
from pydantic_core import ValidationError
import json
import os

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
from app.contact.schema import ContactResponse
from app.contact.utils import handle_upload, sanitize_filename
from app.utils import env

from . import router


@router.put(
    "/rentals/{id}",
    status_code=status.HTTP_200_OK,
    response_model=RentalOrder,
)
def update_rental_order(
    id: str,
    payload: RentalOrder,
    svc: OrderService = Depends(get_order_service),
) -> RentalOrder:
    order_data = svc.repository.update_rental_order(order_id=id, order=payload)
    if not order_data:
        error_message = (
            "The Rental Order was not updated properly. Please verify and try again"
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
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.put(
    "/sales/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SalesOrder,
)
def update_sales_order(
    id: str,
    payload: SalesOrder,
    svc: OrderService = Depends(get_order_service),
) -> SalesOrder:
    order_data = svc.repository.update_sales_order(order_id=id, order=payload)
    if not order_data:
        error_message = (
            "The Sales Order was not updated properly. Please verify and try again"
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


@router.put(
    "/service/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ServiceOrder,
)
def update_service_order(
    id: str,
    payload: ServiceOrder,
    svc: OrderService = Depends(get_order_service),
) -> ServiceOrder:
    order_data = svc.repository.update_service_order(order_id=id, order=payload)
    if not order_data:
        error_message = (
            "The Service Order was not updated properly. Please verify and try again"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

    try:
        return ServiceOrder(**order_data)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pydantic Validation Error. Please Contact Admin or Developer.",
        )


@router.put(
    "/purchase/{id}",
    status_code=status.HTTP_200_OK,
    response_model=PurchaseOrder,
)
def update_purchase_order(
    id: str,
    order_id: str = Form(...),
    supplier: Optional[str] = Form(None),
    purchase_date: str = Form(...),
    invoice_id: str = Form(default=""),
    products: str = Form(...),
    invoice_pdf: UploadFile = File(None),
    invoice_pdf_path: Optional[str] = Form(None),
    svc: OrderService = Depends(get_order_service),
) -> PurchaseOrder:
    """Update a purchase order with form data and optional PDF replacement."""
    try:
        # Parse products JSON
        products_data = json.loads(products)
        print('products_data: ', products_data)
        products = [PurchaseOrderProduct(**p) for p in products_data]
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid products JSON: {str(e)}",
        )

    # Parse supplier JSON if provided
    parsed_supplier = None
    if supplier and supplier != "null":
        try:
            supplier_data = json.loads(supplier)
            parsed_supplier = ContactResponse(**supplier_data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid supplier JSON: {str(e)}",
            )

    # Get existing order to preserve invoice_pdf if not updating
    existing_order = svc.repository.get_purchase_order_by_id(order_id=id)
    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found",
        )

    invoice_pdf_path = existing_order.get("invoice_pdf_path")

    # Handle new PDF upload if provided
    if invoice_pdf:
        try:
            # Delete old PDF if exists
            if invoice_pdf_path:
                old_file = os.path.join("app", invoice_pdf_path)
                if os.path.exists(old_file):
                    os.remove(old_file)

            # Upload new PDF
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

    # Build update payload
    payload_dict = {
        "order_id": order_id,
        "supplier": parsed_supplier,
        "purchase_date": purchase_date,
        "invoice_id": invoice_id,
        "products": [p.model_dump() for p in products],
        "invoice_pdf_path": invoice_pdf_path,
    }

    try:
        payload = PurchaseOrder(**payload_dict)

        # Get existing products to calculate quantity deltas
        old_products = existing_order.get("products", [])

        # Process product quantity changes
        svc.process_purchase_products_update(old_products, products)

        order_data = svc.repository.update_purchase_order(order_id=id, order=payload)
        if not order_data:
            error_message = "The Purchase Order was not updated properly. Please verify and try again"
            print('error_message: ', error_message)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_message
            )

        return PurchaseOrder(**order_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pydantic Validation Error: {str(e)}",
        )
