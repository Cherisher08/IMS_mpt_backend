from bson.objectid import ObjectId
from pymongo.database import Database
from typing import Dict, Any, Optional

from app.petty_cash.schema import PettyCash


class PettyCashRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_petty_cash(self, petty_cash: PettyCash):
        payload = petty_cash.model_dump(exclude=["id"], by_alias=True)
        result = self.database["petty_cash"].insert_one(payload)
        return self.get_petty_cash_by_id(petty_cash_id=result.inserted_id)

    def update_petty_cash(self, petty_cash_id: str, petty_cash: PettyCash):
        payload = petty_cash.model_dump(exclude=["id"], by_alias=True)
        self.database["petty_cash"].update_one(
            {"_id": ObjectId(petty_cash_id)}, {"$set": payload}
        )
        return self.get_petty_cash_by_id(petty_cash_id=petty_cash_id)

    def get_petty_cash_by_id(self, petty_cash_id: str):
        return self.database["petty_cash"].find_one({"_id": ObjectId(petty_cash_id)})

    def delete_petty_cash_by_id(self, petty_cash_id: str):
        result = self.database["petty_cash"].delete_one({"_id": ObjectId(petty_cash_id)})
        return result.deleted_count

    def get_petty_cash_entries(self, filters: Optional[Dict[str, Any]] = None, sort_spec: Optional[list] = None, skip: int = 0, limit: int = 1000):
        """Get petty cash entries with filtering, sorting and pagination. limit=0 means retrieve all."""
        query = filters or {}
        cursor = self.database["petty_cash"].find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
