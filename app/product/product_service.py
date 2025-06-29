from app.config import database
from app.product.product_repository import ProductRepository
from app.product_category.product_category_repository import (
    ProductCategoryRepository,
)
from app.unit.unit_repository import UnitRepository


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        product_category_repository: ProductCategoryRepository,
        unit_repository: UnitRepository,
    ):
        self.repository = product_repository
        self.product_category_repository = product_category_repository
        self.unit_repository = unit_repository


def get_product_service():
    product_repository = ProductRepository(database=database)
    product_category_repository = ProductCategoryRepository(database=database)
    unit_repository = UnitRepository(database=database)
    svc = ProductService(
        product_repository=product_repository,
        product_category_repository=product_category_repository,
        unit_repository=unit_repository,
    )
    return svc
