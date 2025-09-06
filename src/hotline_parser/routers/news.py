from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import ParsingException, TimeoutException
from ..schemas.news import NewsQueryParams, NewsResponse
from ..services.news_parser import news_parser_factory

router = APIRouter()


@router.get("/source", response_model=NewsResponse)
async def get_news(
    url: str = Query(..., description="News source URL"),
    until_date: datetime = Query(..., description="Limit date for news"),
    client: Optional[str] = Query(None, pattern="^(http|browser)$"),
):
    try:
        parser = news_parser_factory.get_parser(url)
        items = await parser.parse_news(url, until_date, client or "http")
        return NewsResponse(items=items)
    except TimeoutException as e:
        raise HTTPException(status_code=408, detail=str(e))
    except ParsingException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
