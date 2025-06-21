from bson.objectid import ObjectId
from pymongo.database import Database

from app.constants import ID
from app.contact.schema import Contact


class ContactRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_contact(self, contact: Contact):
        payload = {
            "name": contact.name,
            "personal": contact.personal,
            "office": contact.office,
            "gstin": contact.gstin,
            "email": contact.email,
            "address": contact.address,
            "pincode": contact.pincode,
            "address_proof": contact.address_proof,
            "created_at": contact.created_at,
        }

        result = self.database["contacts"].insert_one(payload)
        return self.get_contact_by_id(contact_id=result.inserted_id)

    def get_contacts(self):
        result = self.database["contacts"].find({}).to_list()
        return result

    def get_contact_by_id(self, contact_id: str):
        result = self.database["contacts"].find_one({"_id": ObjectId(contact_id)})
        return result

    def update_contact(self, contact_id: str, contact: Contact):
        payload = {
            "name": contact.name,
            "personal": contact.personal,
            "office": contact.office,
            "gstin": contact.gstin,
            "email": contact.email,
            "address": contact.address,
            "pincode": contact.pincode,
            "address_proof": contact.address_proof,
            "created_at": contact.created_at,
        }

        self.database["contacts"].update_one(
            {ID: ObjectId(contact_id)}, update={"$set": payload}
        )
        return self.get_contact_by_id(contact_id=contact_id)

    def delete_contact(self, contact_id: str):
        result = self.database["contacts"].delete_one({ID: ObjectId(contact_id)})
        return result.deleted_count
