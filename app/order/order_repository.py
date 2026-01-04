from bson.objectid import ObjectId
from pymongo.database import Database
from typing import Dict, Any, Optional

from app.order.schema import RentalOrder, SalesOrder, ServiceOrder, PurchaseOrder


class OrderRepository:
    def __init__(self, database: Database):
        self.database = database

    # ----------------------------
    # RENTAL ORDERS
    # ----------------------------

    def create_rental_order(self, order: RentalOrder):
        payload = order.model_dump(exclude=["id"], by_alias=True)
        result = self.database["rental_orders"].insert_one(payload)
        return self.get_rental_order_by_id(order_id=result.inserted_id)

    def update_rental_order(self, order_id: str, order: RentalOrder):
        payload = order.model_dump(exclude=["id"], by_alias=True)
        self.database["rental_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_rental_order_by_id(order_id=order_id)

    def get_rental_order_by_id(self, order_id: str):
        return self.database["rental_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_rental_order_by_id(self, order_id: str):
        result = self.database["rental_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_rental_orders(self, filters: Optional[Dict[str, Any]] = None, sort_spec: Optional[list] = None, skip: int = 0, limit: int = 1000):
        """Get rental orders with filtering, sorting and pagination. limit=0 means retrieve all."""
        query = filters or {}
        cursor = self.database["rental_orders"].find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_rental_orders_contact_info(self, contact_id: str, customer: object):
        self.database["rental_orders"].update_many(
            {"customer._id": contact_id},
            {
                "$set": {
                    "customer.name": customer.name,
                    "customer.personal_number": customer.personal_number,
                    "customer.office_number": customer.office_number,
                    "customer.gstin": customer.gstin,
                    "customer.email": customer.email,
                    "customer.address": customer.address,
                    "customer.pincode": customer.pincode,
                    "customer.company_name": customer.company_name,
                }
            },
        )

    # ----------------------------
    # SALES ORDERS
    # ----------------------------

    def create_sales_order(self, order: SalesOrder):
        payload = order.model_dump(exclude=["id"])
        result = self.database["sales_orders"].insert_one(payload)
        return self.get_sales_order_by_id(order_id=result.inserted_id)

    def update_sales_order(self, order_id: str, order: SalesOrder):
        payload = order.model_dump(exclude=["id"])
        self.database["sales_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_sales_order_by_id(order_id=order_id)

    def get_sales_order_by_id(self, order_id: str):
        return self.database["sales_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_sales_order_by_id(self, order_id: str):
        result = self.database["sales_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_sales_orders(self, filters: Optional[Dict[str, Any]] = None, sort_spec: Optional[list] = None, skip: int = 0, limit: int = 1000):
        """Get sales orders with filtering, sorting and pagination. limit=0 means retrieve all."""
        query = filters or {}
        cursor = self.database["sales_orders"].find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    # ----------------------------
    # SERVICE ORDERS
    # ----------------------------

    def create_service_order(self, order: ServiceOrder):
        payload = order.model_dump(exclude=["id"])
        result = self.database["service_orders"].insert_one(payload)
        return self.get_service_order_by_id(order_id=result.inserted_id)

    def update_service_order(self, order_id: str, order: ServiceOrder):
        payload = order.model_dump(exclude=["id"])
        self.database["service_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_service_order_by_id(order_id=order_id)

    def get_service_order_by_id(self, order_id: str):
        return self.database["service_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_service_order_by_id(self, order_id: str):
        result = self.database["service_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_service_orders(self, filters: Optional[Dict[str, Any]] = None, sort_spec: Optional[list] = None, skip: int = 0, limit: int = 1000):
        """Get service orders with filtering, sorting and pagination. limit=0 means retrieve all."""
        query = filters or {}
        cursor = self.database["service_orders"].find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    # ----------------------------
    # PURCHASE ORDERS
    # ----------------------------

    def create_purchase_order(self, order: "PurchaseOrder"):
        payload = order.model_dump(exclude=["id"], by_alias=True)
        result = self.database["purchase_orders"].insert_one(payload)
        return self.get_purchase_order_by_id(order_id=str(result.inserted_id))

    def update_purchase_order(self, order_id: str, order: "PurchaseOrder"):
        payload = order.model_dump(exclude=["id"], by_alias=True)
        self.database["purchase_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_purchase_order_by_id(order_id=order_id)

    def get_purchase_order_by_id(self, order_id: str):
        return self.database["purchase_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_purchase_order_by_id(self, order_id: str):
        result = self.database["purchase_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_purchase_orders(self, filters: Optional[Dict[str, Any]] = None, sort_spec: Optional[list] = None, skip: int = 0, limit: int = 1000):
        """Get purchase orders with filtering, sorting and pagination. limit=0 means retrieve all."""
        query = filters or {}
        cursor = self.database["purchase_orders"].find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
