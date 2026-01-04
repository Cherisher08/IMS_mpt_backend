from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId
from app.product_category.schema import ProductCategory
from app.unit.schema import Unit
from app.utils import AppModel


class ProductType(str, Enum):
    SALES = "sales"
    RENTAL = "rental"
    SERVICE = "service"
    PURCHASE = "purchase"
    

class DiscountType(str, Enum):
    PERCENT = "percent"
    RUPEES = "rupees"


class ProductDB(AppModel):
    id: Optional[PyObjectId] = Field(default=None,alias="_id")
    name: str
    created_at: datetime
    quantity: int
    available_stock: int
    repair_count: int
    product_code: str
    category: str
    price: int
    type: ProductType
    purchase_date: datetime
    unit: str
    rent_per_unit: float
    discount: float
    discount_type: DiscountType
    
class ProductResponse(AppModel):
    id: Optional[PyObjectId] = Field(default=None,alias="_id")
    name: str
    created_at: datetime
    quantity: int
    available_stock: int
    repair_count: int
    product_code: str
    category: ProductCategory
    price: int
    type: ProductType
    purchase_date: datetime
    unit: Unit
    rent_per_unit: float
    discount: float
    discount_type: DiscountType