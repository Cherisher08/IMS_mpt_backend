from app.config import database
from app.contact.contact_repository import ContactRepository


class ContactService:
    def __init__(self, contact_repository: ContactRepository):
        self.repository = contact_repository


def get_contact_service():
    contact_repository = ContactRepository(database=database)
    svc = ContactService(contact_repository=contact_repository)
    return svc
