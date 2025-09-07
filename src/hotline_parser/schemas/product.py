from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OfferSchema(BaseModel):
    url: str
    original_url: str
    title: str
    shop: str
    price: float
    is_used: bool


class ProductResponse(BaseModel):
    url: str
    offers: List[OfferSchema]


class ProductQueryParams(BaseModel):
    url: str
    timeout_limit: Optional[int] = Field(None, ge=1, le=30)
    count_limit: Optional[int] = Field(None, ge=1, le=100)
    price_sort: Optional[str] = Field(None, pattern="^(asc|desc)$")
