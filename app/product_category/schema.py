from datetime import datetime
from typing import Optional
from pydantic import Field

from app.auth.schema import PyObjectId
from app.utils import AppModel


class ProductCategory(AppModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    created_at: datetime
