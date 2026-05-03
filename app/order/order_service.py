from datetime import datetime, timezone
from bson import ObjectId

from app.config import database
from app.order.order_repository import OrderRepository
from app.order.schema import RentalOrder
from app.product.product_repository import ProductRepository
from app.product.schema import ProductResponse
from app.product_category.product_category_repository import ProductCategoryRepository
from app.product_category.schema import ProductCategory
from app.unit.schema import Unit, UnitResponse
from app.unit.unit_repository import UnitRepository
from fastapi import HTTPException


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository = None,
        product_category_repository=None,
        unit_repository=None,
    ):
        self.repository = order_repository
        self.product_repository = product_repository or ProductRepository(
            database=database
        )
        self.product_category_repository = (
            product_category_repository or ProductCategoryRepository(database=database)
        )
        self.unit_repository = unit_repository or UnitRepository(database=database)

    def process_purchase_products(self, purchase_products: list):
        """Process products in a purchase order.
        If product exists in database, increment its quantity.
        If product doesn't exist, create a new product.

        Args:
            purchase_products: List of PurchaseOrderProduct objects
        """
        for product in purchase_products:
            product_id = product.id
            quantity = int(product.quantity)

            if product_id:
                # Try to get the product from database
                existing_product = self.product_repository.get_product_by_id(
                    product_id=str(product_id)
                )
                if existing_product:
                    # Product exists, increment quantity
                    self.product_repository.increment_product_quantity(
                        product_id=str(product_id), quantity=quantity
                    )
                else:
                    # Product ID provided but doesn't exist, create it
                    self.product_repository.create_product_from_purchase(
                        name=product.name,
                        product_code=product.product_code,
                        category_id=str(product.category.id),
                        unit_id=str(product.unit.id),
                        type_str=product.type.value,
                        rent_per_unit=float(product.rent_per_unit),
                        quantity=quantity,
                        price=float(product.price),
                    )
            else:
                # New product, create it
                self.product_repository.create_product_from_purchase(
                    name=product.name,
                    product_code=product.product_code,
                    category_id=str(product.category.id),
                    unit_id=str(product.unit.id),
                    type_str=product.type.value,
                    rent_per_unit=float(product.rent_per_unit),
                    quantity=quantity,
                    price=float(product.price),
                )

    def process_purchase_products_update(self, old_products: list, new_products: list):
        """Process product quantity changes during purchase order update.
        Compare old and new products to calculate quantity deltas.

        Args:
            old_products: List of old product dicts from existing purchase order
            new_products: List of new PurchaseOrderProduct objects
        """
        # Create a map of old product IDs to quantities
        old_product_map = {}
        for old_product in old_products:
            product_id = str(old_product.get("_id") or old_product.get("id"))
            if product_id:
                old_product_map[product_id] = int(old_product.get("quantity", 0))

        # Process new products
        for new_product in new_products:
            product_id = str(new_product.id) if new_product.id else None
            new_quantity = int(new_product.quantity)

            if product_id:
                # Try to get the product from database
                existing_product = self.product_repository.get_product_by_id(
                    product_id=product_id
                )
                if existing_product:
                    # Product exists, calculate and apply quantity delta
                    old_quantity = old_product_map.get(product_id, 0)
                    quantity_delta = new_quantity - old_quantity
                    try:
                        if (
                            existing_product.get("gst_percentage") is None
                            or existing_product.get("gst_percentage")
                            != new_product.gst_percentage
                        ):
                            existing_product["gst_percentage"] = float(
                                new_product.gst_percentage
                            )
                            existing_product["category"] = ProductCategory(
                                **self.product_category_repository.get_product_category_by_id(
                                    product_category_id=existing_product["category"]
                                )
                            )
                            existing_product["unit"] = Unit(
                                **self.unit_repository.get_unit_by_id(
                                    unit_id=existing_product["unit"]
                                )
                            )
                            try:
                                self.product_repository.update_product(
                                    product_id=product_id,
                                    product=ProductResponse(**existing_product),
                                )
                            except Exception as e:
                                print(
                                    f"Failed to update product GST percentage: {str(e)}"
                                )

                        if quantity_delta > 0:
                            # Increase quantity
                            self.product_repository.increment_product_quantity(
                                product_id=product_id, quantity=quantity_delta
                            )
                        elif quantity_delta < 0:
                            # Decrease quantity
                            self.product_repository.increment_product_quantity(
                                product_id=product_id, quantity=quantity_delta
                            )
                        # If delta is 0, no change needed
                    except Exception as e:
                        print(f"Failed to update product quantity: {str(e)}")
                else:
                    # Product ID provided but doesn't exist, create it
                    self.product_repository.create_product_from_purchase(
                        name=new_product.name,
                        product_code=new_product.product_code,
                        category_id=str(new_product.category.id),
                        unit_id=str(new_product.unit.id),
                        type_str=new_product.type.value,
                        rent_per_unit=float(new_product.rent_per_unit),
                        quantity=new_quantity,
                        price=float(new_product.price),
                        gst_percentage=float(new_product.gst_percentage),
                        profit=float(new_product.profit),
                        profit_type=new_product.profit_type.value,
                        product_id=product_id,
                    )
            else:
                # New product, create it
                self.product_repository.create_product_from_purchase(
                    name=new_product.name,
                    product_code=new_product.product_code,
                    category_id=str(new_product.category.id),
                    unit_id=str(new_product.unit.id),
                    type_str=new_product.type.value,
                    rent_per_unit=float(new_product.rent_per_unit),
                    quantity=new_quantity,
                    price=float(new_product.price),
                    gst_percentage=float(new_product.gst_percentage),
                    profit=float(new_product.profit),
                    profit_type=new_product.profit_type.value,
                    product_id=str(new_product.id) if new_product.id else None,
                )

    def create_rental_order_with_invoice(self, order: RentalOrder):
        """Create rental order with automatic invoice ID generation for PAID status."""
        from app.order.utils import generate_invoice_id, generate_order_id
        from app.order.schema import PaymentStatus

        # Auto-generate order ID if it's empty or None
        if not order.order_id or order.order_id == "":
            order.order_id = generate_order_id(self.repository.database, order.branch)

        # Auto-generate invoice ID if status is PAID and no invoice ID is set
        if order.status == PaymentStatus.PAID and not order.invoice_id:
            order.invoice_id = generate_invoice_id(
                self.repository.database, order.branch, order.billing_mode
            )
            order.invoice_date = datetime.now(timezone.utc)

        # Proceed with normal order creation
        return self.repository.create_rental_order(order)

    def update_rental_order_with_invoice(self, order_id: str, order: RentalOrder):
        """Update rental order with automatic invoice ID generation when status changes to PAID 
        or when in_date is set with PAID status (indicating items returned and payment complete)."""
        from app.order.utils import generate_invoice_id
        from app.order.schema import PaymentStatus

        # Get existing order to check status change and in_date change
        existing_order = self.repository.get_rental_order_by_id(order_id)
        if existing_order:
            old_status = existing_order.get("status")
            old_in_date = existing_order.get("in_date")
            
            # Auto-generate invoice ID in two scenarios:
            # 1. Status changed to PAID
            # 2. in_date is now set (items returned) and status is PAID (payment complete)
            if not order.invoice_id and not existing_order.get("invoice_id", ""):
                # Case 1: Status changed to PAID
                if (
                    order.status == PaymentStatus.PAID
                    and old_status != PaymentStatus.PAID
                ):
                    order.invoice_id = generate_invoice_id(
                        self.repository.database, order.branch, order.billing_mode
                    )
                    order.invoice_date = datetime.now(timezone.utc)
                # Case 2: in_date is now set (items returned) and status is PAID (payment complete)
                elif (
                    order.status == PaymentStatus.PAID
                    and order.in_date
                    and not old_in_date
                ):
                    order.invoice_id = generate_invoice_id(
                        self.repository.database, order.branch, order.billing_mode
                    )
                    order.invoice_date = datetime.now(timezone.utc)
                elif order.status == PaymentStatus.PAID:
                    # Fallback: if status is PAID but no invoice_id was generated in Cases 1 & 2, generate now
                    order.invoice_id = generate_invoice_id(
                        self.repository.database, order.branch, order.billing_mode
                    )
                    order.invoice_date = datetime.now(timezone.utc)

        # Proceed with normal order update
        return self.repository.update_rental_order(order_id=order_id, order=order)

    def create_sales_order_with_invoice(self, order):
        """Create sales order with automatic invoice ID generation for PAID status."""
        from app.order.utils import generate_invoice_id
        from app.order.schema import PaymentStatus

        # Auto-generate invoice ID if status is PAID and no invoice ID is set
        if order.get("status") == PaymentStatus.PAID and not order.get("invoice_id"):
            # Extract branch and billing_mode from order
            order_branch = order.get("branch")
            order_billing_mode = order.get("billing_mode")
            order["invoice_id"] = generate_invoice_id(
                self.repository.database, order_branch, order_billing_mode
            )
            order["invoice_date"] = datetime.now(timezone.utc)

        # Proceed with normal order creation
        return self.repository.create_sales_order(order)

    def update_sales_order_with_invoice(self, order_id: str, order):
        """Update sales order with automatic invoice ID generation when status changes to PAID."""
        from app.order.utils import generate_invoice_id
        from app.order.schema import PaymentStatus

        # Get existing order to check status change
        existing_order = self.repository.get_sales_order_by_id(order_id)
        if existing_order:
            old_status = existing_order.get("status")
            # Auto-generate invoice ID if status changed to PAID and no invoice ID exists
            if (
                order.get("status") == PaymentStatus.PAID
                and old_status != PaymentStatus.PAID
                and not order.get("invoice_id")
                and not existing_order.get("invoice_id")
            ):
                # Extract branch and billing_mode from order
                order_branch = order.get("branch")
                order_billing_mode = order.get("billing_mode")
                order["invoice_id"] = generate_invoice_id(
                    self.repository.database, order_branch, order_billing_mode
                )
                order["invoice_date"] = datetime.now(timezone.utc)

        # Proceed with normal order update
        return self.repository.update_sales_order(order_id=order_id, order=order)

    def create_service_order_with_invoice(self, order):
        """Create service order with automatic invoice ID generation for PAID status."""
        from app.order.utils import generate_invoice_id
        from app.order.schema import PaymentStatus

        # Auto-generate invoice ID if status is PAID and no invoice ID is set
        if order.get("status") == PaymentStatus.PAID and not order.get("invoice_id"):
            # Extract branch and billing_mode from order
            order_branch = order.get("branch")
            order_billing_mode = order.get("billing_mode")
            order["invoice_id"] = generate_invoice_id(
                self.repository.database, order_branch, order_billing_mode
            )
            order["invoice_date"] = datetime.now(timezone.utc)

        # Proceed with normal order creation
        return self.repository.create_service_order(order)

    def update_service_order_with_invoice(self, order_id: str, order):
        """Update service order with automatic invoice ID generation when status changes to PAID 
        or when in_date is set with PAID status (indicating service completion and payment complete)."""
        from app.order.utils import generate_invoice_id
        from app.order.schema import PaymentStatus

        # Get existing order to check status change and in_date change
        existing_order = self.repository.get_service_order_by_id(order_id)
        if existing_order:
            old_status = existing_order.get("status")
            old_in_date = existing_order.get("in_date")
            
            # Auto-generate invoice ID in two scenarios:
            # 1. Status changed to PAID
            # 2. in_date is now set (service completed) and status is PAID (payment complete)
            if not order.get("invoice_id") and not existing_order.get("invoice_id"):
                # Case 1: Status changed to PAID
                if (
                    order.get("status") == PaymentStatus.PAID
                    and old_status != PaymentStatus.PAID
                ):
                    # Extract branch and billing_mode from order
                    order_branch = order.get("branch")
                    order_billing_mode = order.get("billing_mode")
                    order["invoice_id"] = generate_invoice_id(
                        self.repository.database, order_branch, order_billing_mode
                    )
                    order["invoice_date"] = datetime.now(timezone.utc)
                # Case 2: in_date is now set (service completed) and status is PAID (payment complete)
                elif (
                    order.get("status") == PaymentStatus.PAID
                    and order.get("in_date")
                    and not old_in_date
                ):
                    # Extract branch and billing_mode from order
                    order_branch = order.get("branch")
                    order_billing_mode = order.get("billing_mode")
                    order["invoice_id"] = generate_invoice_id(
                        self.repository.database, order_branch, order_billing_mode
                    )
                    order["invoice_date"] = datetime.now(timezone.utc)

        # Proceed with normal order update
        return self.repository.update_service_order(order_id=order_id, order=order)

    def _ensure_unit_response(self, unit_input):
        if isinstance(unit_input, UnitResponse):
            return unit_input

        if isinstance(unit_input, Unit):
            unit_data = unit_input.model_dump(by_alias=True)
            if "_id" in unit_data and isinstance(unit_data["_id"], ObjectId):
                unit_data["_id"] = str(unit_data["_id"])
            return UnitResponse(**unit_data)

        if isinstance(unit_input, dict):
            unit_dict = unit_input.copy()
            if "_id" in unit_dict and isinstance(unit_dict["_id"], ObjectId):
                unit_dict["_id"] = str(unit_dict["_id"])
            return UnitResponse(**unit_dict)

        if isinstance(unit_input, str):
            unit_data = self.unit_repository.get_unit_by_id(unit_id=unit_input)
            if unit_data:
                if "_id" in unit_data and isinstance(unit_data["_id"], ObjectId):
                    unit_data["_id"] = str(unit_data["_id"])
                return UnitResponse(**unit_data)

        raise HTTPException(
            status_code=422,
            detail=f"Invalid product_unit value: {unit_input}",
        )

    def _normalize_product_detail_unit(self, product_detail: dict):
        current_unit = product_detail.get("product_unit")
        if current_unit is None:
            raise HTTPException(
                status_code=422,
                detail="Missing product_unit on product_details item",
            )

        product_detail["product_unit"] = self._ensure_unit_response(current_unit)
        return product_detail

    def sync_rental_order_products(self, order_id: str):
        """Sync rental order product_details with latest product catalog data.

        For each product in the rental order's product_details:
        - Fetch the latest product from the database by product_id
        - Update product_details fields with latest catalog data
        - Preserve order-specific fields (order_quantity, dates, damage, etc.)

        Args:
            order_id: The ID of the rental order to sync

        Returns:
            The updated rental order with synced product_details

        Raises:
            HTTPException: If order not found
        """
        # Get the rental order
        rental_order = self.repository.get_rental_order_by_id(order_id)
        if not rental_order:
            raise HTTPException(status_code=404, detail="Rental order not found")

        # Sync each product in product_details
        updated_product_details = []
        for product_detail in rental_order.get("product_details", []):
            product_id = product_detail.get("_id")

            if product_id:
                # Fetch latest product from database
                latest_product = self.product_repository.get_product_by_id(product_id)

                if latest_product:
                    product_unit_source = latest_product.get("unit", product_detail.get("product_unit"))
                    updated_detail = {
                        **product_detail,  # Preserve all existing fields
                        "name": latest_product.get("name", product_detail.get("name")),
                        "rent_per_unit": latest_product.get("rent_per_unit", product_detail.get("rent_per_unit")),
                        "product_code": latest_product.get("product_code", product_detail.get("product_code", "")),
                        "category": latest_product.get("category", product_detail.get("category")),
                        "product_unit": self._ensure_unit_response(product_unit_source),
                        "type": latest_product.get("type", product_detail.get("type")),
                        "description": latest_product.get("description", product_detail.get("description", "")),
                    }
                    updated_product_details.append(updated_detail)
                else:
                    # Product not found in catalog, normalize existing product_unit and keep original
                    updated_product_details.append(self._normalize_product_detail_unit(product_detail))
            else:
                # No product_id, normalize product_unit and keep original
                updated_product_details.append(self._normalize_product_detail_unit(product_detail))

        # Update the rental order with synced product_details
        rental_order["product_details"] = updated_product_details
        updated_order = self.repository.update_rental_order(
            order_id=order_id,
            order=RentalOrder(**rental_order)
        )

        return updated_order


def get_order_service():
    order_repository = OrderRepository(database=database)
    svc = OrderService(
        order_repository=order_repository,
    )
    return svc
