from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: Any
    ) -> Dict[str, Any]:
        json_schema = handler(schema)
        json_schema.update(type="string")
        return json_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class ArticleData(BaseModel):
    title: str
    content_body: str
    image_urls: List[HttpUrl]
    published_at: datetime
    author: Optional[str] = None
    views: Optional[int] = None
    comments: List[str] = []
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    video_url: Optional[HttpUrl] = None


class NewsItem(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    url: HttpUrl
    article_data: ArticleData
    source: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Pydantic v2 configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        populate_by_name=True,  # Allows using both alias and field name
    )
