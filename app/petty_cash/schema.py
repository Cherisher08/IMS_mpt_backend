from datetime import datetime
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId
from app.contact.schema import ContactResponse
from app.order.schema import PaymentMode, RepaymentMode
from app.utils import AppModel, get_current_utc_time


class PettyCash(AppModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_date: datetime = Field(default_factory=get_current_utc_time)
    customer: ContactResponse
    balance_paid: float
    balance_paid_mode: PaymentMode = Field(default=PaymentMode.NULL)
    payment_mode: RepaymentMode = Field(default=RepaymentMode.NULL)
    repay_amount: float
