import importlib
import pkgutil
from datetime import datetime
from zoneinfo import ZoneInfo
from bson.objectid import ObjectId
from pydantic import BaseModel


def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class AppModel(BaseModel):
    class Config:
        json_encoders = {datetime: convert_datetime_to_gmt, ObjectId: str}
        arbitrary_types_allowed = True
        validate_by_name = True


def import_routers(package_name):
    package = importlib.import_module(package_name)
    prefix = package.__name__ + "."

    for _, module_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        if not module_name.startswith(prefix + "router_"):
            continue

        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Failed to import {module_name}, error: {e}")
