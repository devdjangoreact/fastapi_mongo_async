from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ArticleDataSchema(BaseModel):
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


class NewsItemSchema(BaseModel):
    url: HttpUrl
    article_data: ArticleDataSchema


class NewsResponse(BaseModel):
    items: List[NewsItemSchema]


class NewsQueryParams(BaseModel):
    url: HttpUrl
    until_date: datetime
    client: Optional[str] = Field(None, pattern="^(http|browser)$")
