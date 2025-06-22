from datetime import datetime, timezone

from bson.objectid import ObjectId
from pymongo.database import Database

from app.product.schema import Product


class ProductRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_product(self, product: Product):
        payload = {
            "name": product.name,
            "created_at": datetime.now(tz=timezone.utc),
            "quantity": product.quantity,
            "available_stock": product.available_stock,
            "product_code": product.product_code,
            "category": product.category,
            "price": product.price,
            "type": product.type,
            "purchase_date": product.purchase_date,
            "unit": product.unit,
            "rent_per_unit": product.rent_per_unit,
            "discount": product.discount,
            "discount_type": product.discount_type,
            "gst_percent": product.gst_percent,
        }

        result = self.database["products"].insert_one(payload)
        return self.get_product_by_id(product_id=result.inserted_id)

    def update_product(self, product_id: str, product: Product):
        payload = {
            "name": product.name,
            "created_at": datetime.now(tz=timezone.utc),
            "quantity": product.quantity,
            "available_stock": product.available_stock,
            "product_code": product.product_code,
            "category": product.category,
            "price": product.price,
            "type": product.type,
            "purchase_date": product.purchase_date,
            "unit": product.unit,
            "rent_per_unit": product.rent_per_unit,
            "discount": product.discount,
            "discount_type": product.discount_type,
            "gst_percent": product.gst_percent,
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
