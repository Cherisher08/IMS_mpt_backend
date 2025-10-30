from app.config import database
from app.contact.contact_repository import ContactRepository
from app.order.order_repository import OrderRepository


class ContactService:
    def __init__(
        self, contact_repository: ContactRepository, order_repository: OrderRepository
    ):
        self.repository = contact_repository
        self.order_repository = order_repository


def get_contact_service():
    contact_repository = ContactRepository(database=database)
    order_repository = OrderRepository(database=database)
    svc = ContactService(
        contact_repository=contact_repository, order_repository=order_repository
    )
    return svc
