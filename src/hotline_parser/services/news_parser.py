import asyncio
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

import httpx

from ..core.exceptions import ParsingException, TimeoutException
from ..schemas.news import ArticleDataSchema, NewsItemSchema


class BaseNewsParser:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)

    async def parse_news(
        self, url: str, until_date: datetime, client: str = "http"
    ) -> List[NewsItemSchema]:
        raise NotImplementedError

    async def _parse_article(self, article_url: str, client: str) -> ArticleDataSchema:
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()


class EpravdaParser(BaseNewsParser):
    async def parse_news(
        self, url: str, until_date: datetime, client: str = "http"
    ) -> List[NewsItemSchema]:
        # Implementation for epravda.com.ua
        pass


class PolitekaParser(BaseNewsParser):
    async def parse_news(
        self, url: str, until_date: datetime, client: str = "http"
    ) -> List[NewsItemSchema]:
        # Implementation for politeka.net
        pass


class PravdaParser(BaseNewsParser):
    async def parse_news(
        self, url: str, until_date: datetime, client: str = "http"
    ) -> List[NewsItemSchema]:
        # Implementation for pravda.com.ua
        pass


class NewsParserFactory:
    @staticmethod
    def get_parser(url: str) -> BaseNewsParser:
        domain = urlparse(url).netloc.lower()

        if "epravda.com.ua" in domain:
            return EpravdaParser()
        elif "politeka.net" in domain:
            return PolitekaParser()
        elif "pravda.com.ua" in domain:
            return PravdaParser()
        else:
            raise ParsingException(f"Unsupported news source: {domain}")


news_parser_factory = NewsParserFactory()
