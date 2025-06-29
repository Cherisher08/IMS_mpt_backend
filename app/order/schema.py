from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Union, Optional
from enum import Enum

from app.contact.schema import Contact
from app.product.schema import ProductResponse, ProductType
from app.unit.schema import Unit
from app.utils import get_current_utc_time


# Enums
class BillingMode(str, Enum):
    RETAIL = "Retail"
    BUSINESS = "Business"


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
    _id: str
    name: str


class ProductDetails(BaseModel):
    _id: str
    name: str
    category: str
    billing_unit: BillingUnit = Field(default=BillingUnit.DAYS)
    product_unit: Unit
    inDate: str
    outDate: str
    order_repair_count: int
    order_quantity: int
    rent_per_unit: float


class Deposit(BaseModel):
    amount: float = Field(default=0)
    date: datetime
    product: ProductLite
    mode: PaymentMode = Field(default=PaymentMode.CASH)


class Order(BaseModel):
    _id: str
    customer: Contact
    billing_mode: BillingMode = Field(default=BillingMode.BUSINESS)
    discount: float = Field(default=0)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    remarks: str
    round_off: float = Field(default=0)
    payment_mode: PaymentMode = Field(default=PaymentMode.CASH)
    created_At: datetime = Field(default_factory=get_current_utc_time)


class RentalOrder(Order):
    type: ProductType = Field(default=ProductType.RENTAL)
    deposits: List[Deposit]
    out_date: datetime
    expected_date: datetime
    in_date: Optional[datetime]
    product_details: List[ProductDetails]
    event_address: str
    event_pincode: str


class SalesOrder(Order):
    type: ProductType = Field(default=ProductType.SALES)
    bill_date: datetime = Field(default_factory=get_current_utc_time)
    productDetails: List[ProductResponse]


class ServiceOrder(Order):
    type: ProductType = Field(default=ProductType.SERVICE)
    in_date: datetime
    out_date: datetime
