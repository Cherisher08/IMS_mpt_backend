from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId
from app.utils import AppModel


class Unit(AppModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    symbol: str


class ProductCategory(AppModel):
    id: PyObjectId = Field(alias="_id")
    name: str


class ProductType(Enum):
    SALES = "sales"
    RENTAL = "rental"
    SERVICE = "service"


class Product(AppModel):
    id: Optional[PyObjectId] = Field(default=None,alias="_id")
    name: str
    created_by: str
    created_at: datetime
    quantity: int
    product_code: str
    category: str
    price: int
    type: str
    purchase_date: datetime
    unit: str
    rent_per_unit: int
    discount: int
    discount_type: str
