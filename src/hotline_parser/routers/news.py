# routers/news.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.database import get_database
from ..core.logger import log
from ..schemas.news import NewsResponse

router = APIRouter()


@router.post("", response_model=NewsResponse)
async def get_news(
    url: str = Query(..., description="News source URL"),
    until_date: datetime = Query(..., description="Limit date for news"),
    client: Optional[str] = Query(None, description="Client identifier"),
):
    """
    Get news from specified source

    Parameters:
    - url: News source URL (required)
    - until_date: Limit date for news (required)
    - client: Client identifier (optional)
    """
    try:
        db = get_database()

        news_data = await db.news.find_one(
            {"source_url": url, "date": {"$lte": until_date}}
        )

        if not news_data:
            log.warning(f"No news found for source: {url}")
            raise HTTPException(status_code=404, detail="News not found")

        news_response = NewsResponse(**news_data)

        log.success(f"News retrieved successfully: {url}")
        return news_response

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve news from {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
