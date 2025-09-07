from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.database import get_database
from ..core.exceptions import ParsingException, TimeoutException
from ..core.logger import log
from ..schemas.product import ProductResponse

router = APIRouter()


@router.post("", response_model=ProductResponse)
async def get_product_offers(
    url: str = Query(..., description="Product page URL"),
    timeout_limit: Optional[int] = Query(None, ge=1, le=30),
    count_limit: Optional[int] = Query(None, ge=1, le=100),
    price_sort: Optional[str] = Query(None, pattern="^(asc|desc)$"),
):
    try:
        db = get_database()

        # Get product from database
        product_data = await db.products.find_one({"url": url})

        if not product_data:
            log.warning(f"Product not found in database: {url}")
            raise HTTPException(status_code=404, detail="Product not found")

        # Convert to response model
        product = ProductResponse(**product_data)

        # Apply sorting if requested
        if price_sort:
            reverse = price_sort.lower() == "desc"
            product.offers.sort(key=lambda x: x.price, reverse=reverse)

        # Apply count limit if requested
        if count_limit:
            product.offers = product.offers[:count_limit]

        log.success(f"Product data retrieved from database: {url}")
        return product

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve product {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
