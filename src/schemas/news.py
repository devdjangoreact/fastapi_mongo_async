from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ArticleDataSchema(BaseModel):
    title: str
    content_body: str
    image_urls: List[str]
    published_at: datetime
    author: Optional[str] = None
    views: Optional[int] = None
    comments: List[str] = []
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    video_url: Optional[str] = None


class NewsItemSchema(BaseModel):
    url: str
    article_data: ArticleDataSchema


class NewsResponse(BaseModel):
    items: List[NewsItemSchema]


class NewsQueryParams(BaseModel):
    url: str
    until_date: datetime
    client: Optional[str] = Field(None, pattern="^(http|browser)$")


class ClientType(str, Enum):
    """Available client types for news parsing"""

    HTTP = "http"
    BROWSER = "browser"
