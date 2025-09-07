from datetime import datetime
from typing import Annotated, List, Optional

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Simple PyObjectId type using Annotated
PyObjectId = Annotated[str, BeforeValidator(lambda x: str(x))]


class Offer(BaseModel):
    url: str
    original_url: str
    title: str
    shop: str
    price: float
    is_used: bool


class Product(BaseModel):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    url: str
    offers: List[Offer]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )
