from datetime import datetime
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId
from app.utils import AppModel, get_current_utc_time


class Unit(AppModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    created_at: datetime = Field(default_factory=get_current_utc_time)
    
class UnitResponse(Unit):
    id: str = Field(default=None, alias="_id")
