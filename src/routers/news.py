from datetime import date, datetime
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query

from ..core.logger import log
from ..repositories.news_repository import news_repository
from ..schemas.news import ArticleDataSchema, ClientType, NewsItemSchema, NewsResponse
from ..services.news_parser import news_parser_factory

router = APIRouter()

# List of supported domains
SUPPORTED_DOMAINS = ["epravda.com.ua", "politeka.net", "pravda.com.ua"]


@router.post(
    "",
    response_model=NewsResponse,
    responses={
        400: {"description": "Unsupported news source"},
        404: {"description": "News not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_news(
    url: str = Query(..., description="News source URL"),
    until_date: date = Query(
        ..., description="Limit date for news", example="2024-01-15"
    ),
    client: ClientType = Query(None, description="Client identifier"),
):
    """
    Get news from specified source

    Parameters:
    - url: News source URL (required)
    - until_date: Limit date for news (required)
    - client: Client identifier (optional)
    """
    try:

        domain = urlparse(url).netloc.lower()
        is_supported = any(
            supported_domain in domain for supported_domain in SUPPORTED_DOMAINS
        )

        if not is_supported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported news source. Supported domains: {', '.join(SUPPORTED_DOMAINS)}",
            )
        # Convert date to datetime for database query
        until_datetime = datetime.combine(until_date, datetime.min.time())

        # First try to get data from database
        db_news = await news_repository.get_news_by_source_and_date(
            url=url, until_date=until_datetime
        )

        if db_news:
            log.success(f"Found {len(db_news)} news items in database for {url}")
            # Convert database models to response schema
            news_items = [
                NewsItemSchema(
                    url=item.url,
                    article_data=ArticleDataSchema(**item.article_data.model_dump()),
                    source=item.source,
                    created_at=item.created_at,
                )
                for item in db_news
            ]
            return NewsResponse(items=news_items, source=url, from_cache=True)

        # If no data in database, use parser
        log.info(f"No data in database for {url}, starting parser...")
        parser = news_parser_factory.get_parser(url)

        try:
            news_items = await parser.parse_news(url, until_datetime, client)

            # Save parsed news to database
            if news_items:
                source_domain = urlparse(url).netloc
                await news_repository.save_news_items(news_items, source_domain)
                log.success(f"Parsed and saved {len(news_items)} news items from {url}")

            return NewsResponse(items=news_items, source=url, from_cache=False)

        finally:
            await parser.close()

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve news from {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
