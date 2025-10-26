from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from typing import Any, List, Literal, Optional
from enum import Enum

from app.auth.schema import PyObjectId
from app.contact.schema import ContactResponse
from app.product.schema import DiscountType, ProductResponse, ProductType
from app.unit.schema import UnitResponse
from app.utils import get_current_utc_time


def gen_object_id():
    return str(ObjectId())


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
    CANCELLED = "cancelled"
    NO_BILL = "no bill"


class PaymentMode(str, Enum):
    NULL = "-"
    CASH = "cash"
    UPI = "upi"
    ACCOUNT = "account"


class RepaymentMode(str, Enum):
    NULL = "-"
    CASHLESS = "cash less"
    UPILESS = "upi less"
    KVBLESS = "kvb less"


class TransportType(str, Enum):
    NULL = "-"
    UP = "Up"
    DOWN = "Down"
    BOTH = "Both"


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
    in_date: Optional[datetime] = None
    out_date: datetime
    order_repair_count: int
    order_quantity: int
    rent_per_unit: float
    product_code: str = Field(default="")
    duration: int = Field(default=0)
    damage: str = Field(default="")
    type: ProductType = Field(default=ProductType.RENTAL)

    @field_validator("in_date", mode="before")
    def empty_string_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class Deposit(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=gen_object_id, alias="_id")
    amount: float = Field(default=0)
    date: datetime
    product: Optional[ProductLite]
    mode: PaymentMode = Field(default=PaymentMode.CASH)


class Order(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    order_id: str
    customer: Optional[ContactResponse] = Field(
        default=None,
    )
    billing_mode: BillingMode = Field(default=BillingMode.B2B)
    discount: float = Field(default=0)
    discount_type: DiscountType = Field(default=DiscountType.RUPEES)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    remarks: str
    round_off: float = Field(default=0)
    payment_mode: RepaymentMode = Field(default=RepaymentMode.NULL)
    created_at: datetime = Field(default_factory=get_current_utc_time)
    gst: float


class RentalOrder(Order):
    type: ProductType = Field(default=ProductType.RENTAL)
    deposits: List[Deposit]
    out_date: datetime
    rental_duration: int = Field(default=0)
    in_date: Optional[datetime]
    product_details: List[ProductDetails]
    balance_paid_mode: PaymentMode = Field(default=PaymentMode.NULL)
    balance_paid: float = Field(default=0)
    repay_amount: float = Field(default=0)
    repay_date: Optional[datetime] = Field(default=None)
    balance_paid_date: Optional[datetime] = Field(default=None)
    eway_amount: float = Field(default=0)
    eway_type: TransportType = Field(default=TransportType.NULL)
    eway_mode: PaymentMode = Field(default=PaymentMode.CASH)
    event_address: str
    event_venue: str = Field(default="")
    event_name: str = Field(default="")
    invoice_id: Optional[str] = Field(default=None)


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
