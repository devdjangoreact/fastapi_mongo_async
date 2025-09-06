from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, HttpUrl


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Offer(BaseModel):
    url: HttpUrl
    original_url: HttpUrl
    title: str
    shop: str
    price: float
    is_used: bool


class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    url: HttpUrl
    offers: List[Offer]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
