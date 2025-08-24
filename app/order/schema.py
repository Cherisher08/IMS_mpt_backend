from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional
from enum import Enum

from app.auth.schema import PyObjectId
from app.contact.schema import ContactResponse
from app.product.schema import ProductResponse, ProductType
from app.unit.schema import UnitResponse
from app.utils import get_current_utc_time


# Enums
class BillingMode(str, Enum):
    B2C = "B2C"
    B2B = "B2B"


class BillingUnit(str, Enum):
    SHIFT = "shift"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"


class PaymentMode(str, Enum):
    CASH = "cash"
    UPI = "upi"
    ACCOUNT = "account"


# Models
class ProductLite(BaseModel):
    id: str = Field(default=None, alias="_id")
    name: str


class ProductDetails(BaseModel):
    id: str = Field(alias="_id")
    name: str
    category: str
    billing_unit: BillingUnit = Field(default=BillingUnit.DAYS)
    product_unit: UnitResponse
    in_date: Optional[datetime]
    out_date: datetime
    order_repair_count: int
    order_quantity: int
    rent_per_unit: float
    product_code: str = Field(default="")
    duration: int = Field(default=0)


class Deposit(BaseModel):
    amount: float = Field(default=0)
    date: datetime
    product: Optional[ProductLite]
    mode: PaymentMode = Field(default=PaymentMode.CASH)


class Order(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    order_id: str
    customer: ContactResponse
    billing_mode: BillingMode = Field(default=BillingMode.B2B)
    discount: float = Field(default=0)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    remarks: str
    round_off: float = Field(default=0)
    payment_mode: PaymentMode = Field(default=PaymentMode.CASH)
    created_at: datetime = Field(default_factory=get_current_utc_time)
    gst: float


class RentalOrder(Order):
    type: ProductType = Field(default=ProductType.RENTAL)
    deposits: List[Deposit]
    out_date: datetime
    expected_date: datetime
    in_date: Optional[datetime]
    product_details: List[ProductDetails]
    eway_amount: float = Field(default=0)
    event_address: str
    event_venue: str = Field(default="")
    event_name: str = Field(default="")


class SalesOrder(Order):
    type: ProductType = Field(default=ProductType.SALES)
    bill_date: datetime = Field(default_factory=get_current_utc_time)
    products: List[ProductResponse]


class ServiceOrder(Order):
    type: ProductType = Field(default=ProductType.SERVICE)
    in_date: datetime
    out_date: datetime


class PatchOperation(BaseModel):
    op: Literal["add", "remove", "replace"]
    path: str
    value: Optional[Any] = None

    class Config:
        validate_by_name = True
