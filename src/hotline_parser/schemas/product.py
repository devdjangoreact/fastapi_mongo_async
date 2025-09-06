from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class OfferSchema(BaseModel):
    url: HttpUrl
    original_url: HttpUrl
    title: str
    shop: str
    price: float
    is_used: bool


class ProductResponse(BaseModel):
    url: HttpUrl
    offers: List[OfferSchema]


class ProductQueryParams(BaseModel):
    url: HttpUrl
    timeout_limit: Optional[int] = Field(None, ge=1, le=30)
    count_limit: Optional[int] = Field(None, ge=1, le=100)
    price_sort: Optional[str] = Field(None, pattern="^(asc|desc)$")
