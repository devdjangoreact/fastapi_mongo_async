import json
import os
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

import httpx

from ..core.exceptions import ParsingException, TimeoutException
from ..schemas.news import ArticleDataSchema, ClientType, NewsItemSchema


class BaseNewsParser:
    def __init__(self):
        # Initialize HTTP client with timeout
        self.client = httpx.AsyncClient(timeout=30)
        self.mock_data = self._load_mock_data()

    def _load_mock_data(self) -> dict:
        """Load mock data from JSON file"""
        try:
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            mock_file = os.path.join("mock_data", "news_mock_data.json")

            with open(mock_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading mock data: {e}")
            return {}

    def _create_news_objects_from_json(
        self, json_data: List[dict]
    ) -> List[NewsItemSchema]:
        """Create NewsItemSchema objects from JSON data"""
        news_items = []

        for item in json_data:
            try:
                # Convert string dates to datetime objects
                item["article_data"]["published_at"] = datetime.fromisoformat(
                    item["article_data"]["published_at"].replace("Z", "+00:00")
                )
                item["created_at"] = datetime.fromisoformat(
                    item["created_at"].replace("Z", "+00:00")
                )

                # Create schema objects
                article_data = ArticleDataSchema(**item["article_data"])
                news_item = NewsItemSchema(
                    url=item["url"],
                    article_data=article_data,
                    source=item["source"],
                    created_at=item["created_at"],
                )
                news_items.append(news_item)
            except Exception as e:
                print(f"Error creating news object: {e}")
                continue

        return news_items

    async def parse_news(
        self, url: str, until_date: datetime, client: ClientType = ClientType.HTTP
    ) -> List[NewsItemSchema]:
        # Method should be implemented by child classes
        raise NotImplementedError

    async def _parse_article(
        self, article_url: str, client: ClientType
    ) -> ArticleDataSchema:
        # Method should be implemented by child classes
        raise NotImplementedError

    async def close(self):
        # Close HTTP client connection
        await self.client.aclose()


class EpravdaParser(BaseNewsParser):
    async def parse_news(
        self, url: str, until_date: datetime, client: ClientType = ClientType.HTTP
    ) -> List[NewsItemSchema]:
        # Return mock data for epravda.com.ua
        mock_news = self.mock_data.get("epravda", [])
        return self._create_news_objects_from_json(mock_news)


class PolitekaParser(BaseNewsParser):
    async def parse_news(
        self, url: str, until_date: datetime, client: ClientType = ClientType.HTTP
    ) -> List[NewsItemSchema]:
        # Return mock data for politeka.net
        mock_news = self.mock_data.get("politeka", [])
        return self._create_news_objects_from_json(mock_news)


class PravdaParser(BaseNewsParser):
    async def parse_news(
        self, url: str, until_date: datetime, client: ClientType = ClientType.HTTP
    ) -> List[NewsItemSchema]:
        # Return mock data for pravda.com.ua
        mock_news = self.mock_data.get("pravda", [])
        return self._create_news_objects_from_json(mock_news)


class NewsParserFactory:
    @staticmethod
    def get_parser(url: str) -> BaseNewsParser:
        # Factory method to get appropriate parser based on URL domain
        domain = urlparse(url).netloc.lower()

        if "epravda.com.ua" in domain:
            return EpravdaParser()
        elif "politeka.net" in domain:
            return PolitekaParser()
        elif "pravda.com.ua" in domain:
            return PravdaParser()
        else:
            raise ParsingException(f"Unsupported news source: {domain}")


# Global factory instance
news_parser_factory = NewsParserFactory()
