from app.config import database
from app.product.repository.product_repository import ProductRepository

class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.repository = product_repository


def get_product_service():
    product_repository = ProductRepository(database=database)
    svc = ProductService(product_repository=product_repository)
    return svc
