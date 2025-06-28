from app.config import database
from app.product_category.repository.product_category_repository import ProductCategoryRepository


class ProductCategoryService:
    def __init__(self, product_category_repository: ProductCategoryRepository):
        self.repository = product_category_repository


def get_product_category_service():
    product_category_repository = ProductCategoryRepository(database=database)
    svc = ProductCategoryService(
        product_category_repository=product_category_repository
    )
    return svc
