from app.config import database
from app.order.order_repository import OrderRepository


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
    ):
        self.repository = order_repository


def get_order_service():
    order_repository = OrderRepository(database=database)
    svc = OrderService(
        order_repository=order_repository,
    )
    return svc
