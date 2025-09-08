from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from ..core.database import get_collection
from ..core.logger import log
from ..models.news import ArticleData, NewsItem
from ..schemas.news import ArticleDataSchema, NewsItemSchema


class NewsRepository:
    def __init__(self):
        self.collection_name = "news"
        self._collection: Optional[AsyncIOMotorCollection] = None

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Lazy initialization of collection"""
        if self._collection is None:
            self._collection = get_collection(self.collection_name)
        return self._collection

    async def save_news_items(
        self, items: List[NewsItemSchema], source: str
    ) -> List[str]:
        """Save multiple news items to database"""
        if not items:
            return []

        news_dicts = []
        saved_count = 0

        for item in items:
            # Check if news already exists
            if not await self.news_exists(str(item.url)):
                news_dict = {
                    "url": str(item.url),
                    "article_data": item.article_data.model_dump(),
                    "source": source,
                    "created_at": datetime.utcnow(),
                }
                news_dicts.append(news_dict)
                saved_count += 1

        if news_dicts:
            try:
                result = await self.collection.insert_many(news_dicts)
                log.success(f"Saved {saved_count} news items from {source}")
                return [str(id) for id in result.inserted_ids]
            except Exception as e:
                log.error(f"Failed to save news items: {str(e)}")
                return []

        log.info(f"No new news items to save from {source}")
        return []

    async def get_news_by_source_and_date(
        self, url: str, until_date: datetime, limit: int = 100
    ) -> List[NewsItem]:
        """Get news from database by url and date"""
        try:
            cursor = (
                self.collection.find(
                    {
                        "url": url,
                        "article_data.published_at": {"$lte": until_date},
                    }
                )
                .sort("article_data.published_at", -1)
                .limit(limit)
            )

            news_items = []
            async for item in cursor:
                try:

                    if "_id" in item and isinstance(item["_id"], ObjectId):
                        item["_id"] = str(item["_id"])
                    news_items.append(NewsItem(**item))
                except Exception as e:
                    log.warning(f"Failed to parse news item from DB: {str(e)}")
                    continue

            log.debug(f"Retrieved {len(news_items)} news items from database for {url}")
            return news_items

        except Exception as e:
            log.error(f"Failed to get news from database: {str(e)}")
            return []

    # async def get_cached_news(
    #     self, source: str, until_date: datetime, cache_minutes: int = 15
    # ) -> Optional[List[NewsItemSchema]]:
    #     """Get news from cache if it's fresh enough"""
    #     try:
    #         # Check if we have recent data for this source
    #         latest_news = await self.collection.find_one(
    #             {"source": source}, sort=[("created_at", -1)]
    #         )

    #         if latest_news:
    #             cache_age = (
    #                 datetime.utcnow() - latest_news["created_at"]
    #             ).total_seconds() / 60
    #             if cache_age < cache_minutes:
    #                 # Return cached data
    #                 news_items = await self.get_news_by_source_and_date(
    #                     source, until_date
    #                 )
    #                 return [
    #                     NewsItemSchema(
    #                         url=item.url,
    #                         article_data=ArticleDataSchema(
    #                             **item.article_data.model_dump()
    #                         ),
    #                     )
    #                     for item in news_items
    #                 ]

    #         return None

    #     except Exception as e:
    #         log.error(f"Failed to check cache for {source}: {str(e)}")
    #         return None

    async def news_exists(self, url: str) -> bool:
        """Check if news item already exists in database"""
        try:
            count = await self.collection.count_documents({"url": url})
            return count > 0
        except Exception as e:
            log.error(f"Failed to check if news exists: {str(e)}")
            return False

    # async def cleanup_old_news(self, days: int = 7):
    #     """Cleanup news older than specified days"""
    #     try:
    #         cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
    #         result = await self.collection.delete_many(
    #             {"created_at": {"$lt": cutoff_date}}
    #         )
    #         log.info(f"Cleaned up {result.deleted_count} old news items")
    #         return result.deleted_count
    #     except Exception as e:
    #         log.error(f"Failed to cleanup old news: {str(e)}")
    #         return 0


# Create instance but don't initialize collection until needed
news_repository = NewsRepository()
