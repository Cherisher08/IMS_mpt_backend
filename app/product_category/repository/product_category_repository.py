from datetime import datetime, timezone

from bson.objectid import ObjectId
from pymongo.database import Database

from app.product_category.schema import ProductCategory


class ProductCategoryRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_product_category(self, product_category: ProductCategory):
        payload = {
            "name": product_category.name,
            "created_at": datetime.now(tz=timezone.utc),
        }

        result = self.database["product_categories"].insert_one(payload)
        return self.get_product_category_by_id(product_category_id=result.inserted_id)

    def get_product_category_by_id(self, product_category_id: str):
        product_category = self.database["product_categories"].find_one(
            {
                "_id": ObjectId(product_category_id),
            }
        )
        return product_category

    def get_product_categories(self):
        product_categories = self.database["product_categories"].find({}).to_list()
        return product_categories
