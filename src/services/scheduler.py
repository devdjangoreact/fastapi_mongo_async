import asyncio
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlparse

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..core.logger import log
from ..models.news import NewsItem
from ..models.product import Product
from ..repositories import news_repository, product_repository
from .news_parser import news_parser_factory
from .product_parser import product_parser


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.product_repository = product_repository.ProductRepository()
        self.news_repository = news_repository.NewsRepository()
        self.product_urls = [
            "https://hotline.ua/bt-vyazalnye-mashiny/silver-reed-sk840srp60n",
            # Add more product URLs here
        ]
        self.news_sources = [
            "https://epravda.com.ua/news/",
            "https://politeka.net/uk/newsfeed",
            "https://www.pravda.com.ua/news/",
        ]

    async def start_scheduler(self):
        """Start the scheduler with periodic tasks"""
        # Schedule product parsing every 30 minutes
        self.scheduler.add_job(
            self.parse_all_products,
            trigger=IntervalTrigger(minutes=30),
            id="product_parsing",
            next_run_time=datetime.now(),  # Run immediately on start
        )

        # Schedule news parsing every 30 minutes
        self.scheduler.add_job(
            self.parse_all_news,
            trigger=IntervalTrigger(minutes=30),
            id="news_parsing",
            next_run_time=datetime.now(),  # Run immediately on start
        )

        self.scheduler.start()
        log.success("Scheduler started successfully")

    async def parse_all_products(self):
        """Parse all products and save to database"""
        log.info("Starting product parsing cycle")

        for url in self.product_urls:
            try:
                result = await product_parser.parse_product(url)

                # Save to database
                product_data = {
                    "url": url,
                    "offers": [offer.model_dump() for offer in result.offers],
                    "updated_at": datetime.utcnow(),
                }

                await self.product_repository.update_product(
                    {"url": url}, {"$set": product_data}, upsert=True
                )

                log.success(f"Product parsed and saved: {url}")

            except Exception as e:
                log.error(f"Failed to parse product {url}: {str(e)}")

    async def parse_all_news(self):
        """Parse all news sources and save to database"""
        log.info("Starting news parsing cycle")

        until_date = datetime.now() - timedelta(days=1)  # Last 24 hours

        for url in self.news_sources:
            try:
                parser = news_parser_factory.get_parser(url)
                news_items = await parser.parse_news(url, until_date)
                if news_items:
                    for item in news_items:
                        news_data = NewsItem(
                            url=item.url,
                            article_data=item.article_data,
                            source=urlparse(url).netloc,
                        )

                        await self.news_repository(
                            {"url": item.url},
                            {"$set": news_data.dict(by_alias=True, exclude={"id"})},
                            upsert=True,
                        )

                    log.success(f"News parsed and saved from: {url}")

            except Exception as e:
                log.error(f"Failed to parse news from {url}: {str(e)}")

    async def force_parse_products(self):
        """Force immediate product parsing"""
        log.info("Forcing product parsing")
        await self.parse_all_products()

    async def force_parse_news(self):
        """Force immediate news parsing"""
        log.info("Forcing news parsing")
        await self.parse_all_news()

    async def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        log.info("Scheduler stopped")


scheduler_service = SchedulerService()
