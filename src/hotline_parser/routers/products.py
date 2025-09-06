from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import ParsingException, TimeoutException
from ..schemas.product import ProductQueryParams, ProductResponse
from ..services.product_parser import product_parser

router = APIRouter()


@router.get("/offers", response_model=ProductResponse)
async def get_product_offers(
    url: str = Query(..., description="Product page URL"),
    timeout_limit: Optional[int] = Query(None, ge=1, le=30),
    count_limit: Optional[int] = Query(None, ge=1, le=100),
    price_sort: Optional[str] = Query(None, pattern="^(asc|desc)$"),
):
    try:
        result = await product_parser.parse_product(
            url=url,
            timeout_limit=timeout_limit,
            count_limit=count_limit,
            price_sort=price_sort,
        )
        return result
    except TimeoutException as e:
        raise HTTPException(status_code=408, detail=str(e))
    except ParsingException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
