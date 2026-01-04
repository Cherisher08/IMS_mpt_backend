from datetime import datetime, timezone

from bson.objectid import ObjectId
from pymongo.database import Database

from app.product.schema import ProductResponse


class ProductRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_product(self, product: ProductResponse):
        payload = {
            "name": product.name,
            "created_at": datetime.now(tz=timezone.utc),
            "quantity": product.quantity,
            "available_stock": product.available_stock,
            "repair_count": product.repair_count,
            "product_code": product.product_code,
            "category": str(product.category.id),
            "price": product.price,
            "type": product.type,
            "purchase_date": product.purchase_date,
            "unit": str(product.unit.id),
            "rent_per_unit": product.rent_per_unit,
            "discount": product.discount,
            "discount_type": product.discount_type,
        }

        result = self.database["products"].insert_one(payload)
        return self.get_product_by_id(product_id=result.inserted_id)

    def update_product(self, product_id: str, product: ProductResponse):
        payload = {
            "name": product.name,
            "created_at": datetime.now(tz=timezone.utc),
            "quantity": product.quantity,
            "available_stock": product.available_stock,
            "repair_count": product.repair_count,
            "product_code": product.product_code,
            "category": str(product.category.id),
            "price": product.price,
            "type": product.type,
            "purchase_date": product.purchase_date,
            "unit": str(product.unit.id),
            "rent_per_unit": product.rent_per_unit,
            "discount": product.discount,
            "discount_type": product.discount_type,
        }

        self.database["products"].update_one(
            {"_id": ObjectId(product_id)}, {"$set": {**payload}}
        )
        return self.get_product_by_id(product_id=product_id)

    def get_product_by_id(self, product_id: str):
        product = self.database["products"].find_one(
            {
                "_id": ObjectId(product_id),
            }
        )
        return product
    
    def delete_product_by_id(self, product_id: str):
        product = self.database["products"].delete_one(
            {
                "_id": ObjectId(product_id),
            }
        )
        return product.deleted_count

    def get_products(self):
        products = self.database["products"].find({}).to_list()
        return products
    
    def increment_product_quantity(self, product_id: str, quantity: int):
        """Increment product quantity and available_stock by the given amount."""
        self.database["products"].update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": quantity, "available_stock": quantity}}
        )
        return self.get_product_by_id(product_id=product_id)
    
    def create_product_from_purchase(self, name: str, product_code: str, category_id: str, 
                                     unit_id: str, type_str: str, rent_per_unit: float,
                                     quantity: int, price: float):
        """Create a new product from purchase order product data."""
        payload = {
            "name": name,
            "created_at": datetime.now(tz=timezone.utc),
            "quantity": quantity,
            "available_stock": quantity,
            "repair_count": 0,
            "product_code": product_code,
            "category": category_id,
            "price": price,
            "type": type_str,
            "purchase_date": datetime.now(tz=timezone.utc),
            "unit": unit_id,
            "rent_per_unit": rent_per_unit,
            "discount": 0,
            "discount_type": "rupees",
        }
        result = self.database["products"].insert_one(payload)
        return self.get_product_by_id(product_id=str(result.inserted_id))
