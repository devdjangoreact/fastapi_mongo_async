from datetime import datetime
from typing import Annotated, List, Optional

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, HttpUrl

# Simple PyObjectId type using Annotated
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x))]


class Offer(BaseModel):
    url: HttpUrl
    original_url: HttpUrl
    title: str
    shop: str
    price: float
    is_used: bool


class Product(BaseModel):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    url: HttpUrl
    offers: List[Offer]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )
