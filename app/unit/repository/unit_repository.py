from datetime import datetime, timezone

from bson.objectid import ObjectId
from pymongo.database import Database

from app.unit.schema import Unit


class UnitRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_unit(self, unit: Unit):
        payload = {
            "name": unit.name,
            "created_at": datetime.now(tz=timezone.utc),
        }

        result = self.database["units"].insert_one(payload)
        return self.get_product_category_by_id(unit=result.inserted_id)

    def get_unit_by_id(self, unit: str):
        unit = self.database["units"].find_one(
            {
                "_id": ObjectId(unit),
            }
        )
        return unit

    def get_units(self):
        units = self.database["units"].find({}).to_list()
        return units
