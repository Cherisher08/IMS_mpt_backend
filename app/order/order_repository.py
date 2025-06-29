from bson.objectid import ObjectId
from pymongo.database import Database

from app.order.schema import RentalOrder, SalesOrder, ServiceOrder


class OrderRepository:
    def __init__(self, database: Database):
        self.database = database

    # ----------------------------
    # RENTAL ORDERS
    # ----------------------------

    def create_rental_order(self, order: RentalOrder):
        payload = {}
        result = self.database["rental_orders"].insert_one(payload)
        return self.get_rental_order_by_id(order_id=result.inserted_id)

    def update_rental_order(self, order_id: str, order: RentalOrder):
        payload = {}
        self.database["rental_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_rental_order_by_id(order_id=order_id)

    def get_rental_order_by_id(self, order_id: str):
        return self.database["rental_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_rental_order_by_id(self, order_id: str):
        result = self.database["rental_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_rental_orders(self):
        return list(self.database["rental_orders"].find({}))

    # ----------------------------
    # SALES ORDERS
    # ----------------------------

    def create_sales_order(self, order: SalesOrder):
        payload = {}
        result = self.database["sales_orders"].insert_one(payload)
        return self.get_sales_order_by_id(order_id=result.inserted_id)

    def update_sales_order(self, order_id: str, order: SalesOrder):
        payload = {}
        self.database["sales_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_sales_order_by_id(order_id=order_id)

    def get_sales_order_by_id(self, order_id: str):
        return self.database["sales_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_sales_order_by_id(self, order_id: str):
        result = self.database["sales_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_sales_orders(self):
        return list(self.database["sales_orders"].find({}))

    # ----------------------------
    # SERVICE ORDERS
    # ----------------------------

    def create_service_order(self, order: ServiceOrder):
        payload = {}
        result = self.database["service_orders"].insert_one(payload)
        return self.get_service_order_by_id(order_id=result.inserted_id)

    def update_service_order(self, order_id: str, order: ServiceOrder):
        payload = {}
        self.database["service_orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": payload}
        )
        return self.get_service_order_by_id(order_id=order_id)

    def get_service_order_by_id(self, order_id: str):
        return self.database["service_orders"].find_one({"_id": ObjectId(order_id)})

    def delete_service_order_by_id(self, order_id: str):
        result = self.database["service_orders"].delete_one({"_id": ObjectId(order_id)})
        return result.deleted_count

    def get_service_orders(self):
        return list(self.database["service_orders"].find({}))
