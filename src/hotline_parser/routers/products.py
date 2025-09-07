from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import ParsingException, TimeoutException
from ..core.logger import log
from ..repositories.product_repository import product_repository
from ..schemas.product import ProductResponse
from ..services.product_parser import product_parser

router = APIRouter()


@router.post("", response_model=ProductResponse)
async def get_product_offers(
    url: str = Query(..., description="Product page URL"),
    timeout_limit: Optional[int] = Query(None, ge=1, le=30),
    count_limit: Optional[int] = Query(None, ge=1, le=100),
    price_sort: Optional[str] = Query(None, pattern="^(asc|desc)$"),
):
    try:
        # Get product from database
        product_data = await product_repository.get_product_by_url(url=url)

        if product_data:

            # Convert to response model
            product = ProductResponse(**product_data.model_dump())

            # Apply sorting if requested
            if price_sort:
                reverse = price_sort.lower() == "desc"
                product.offers.sort(key=lambda x: x.price, reverse=reverse)

            # Apply count limit if requested
            if count_limit:
                product.offers = product.offers[:count_limit]

            log.success(f"Product data retrieved from database: {url}")
            return product

        # If not found in database, use parser with mock data
        log.info(f"Product not found in database, using parser: {url}")
        product_data = await product_parser.parse_product(
            url=url,
            timeout_limit=timeout_limit,
            count_limit=count_limit,
            price_sort=price_sort,
        )

        if not product_data:
            log.warning(f"Product not found {url}")
            raise HTTPException(status_code=404, detail="Product not found")

        return product_data

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve product {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
