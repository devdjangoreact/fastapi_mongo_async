from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from ..core.database import get_database
from ..models.product import Offer, Product
from ..schemas.product import OfferSchema, ProductResponse


class ProductRepository:
    def __init__(self):
        self.collection: AsyncIOMotorCollection = get_database().products

    async def create_product(self, product_data: ProductResponse) -> str:
        """Save product to database and return product ID"""
        product_dict = {
            "url": str(product_data.url),
            "offers": [offer.dict() for offer in product_data.offers],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await self.collection.insert_one(product_dict)
        return str(result.inserted_id)

    async def get_product_by_url(self, url: str) -> Optional[Product]:
        """Get product from database by URL"""
        product_data = await self.collection.find_one({"url": url})
        if product_data:
            return Product(**product_data)
        return None

    async def update_product(
        self, query: dict, update_data: dict, upsert: bool = False
    ) -> bool:
        """Update existing product in database"""
        result = await self.collection.update_one(query, update_data, upsert=upsert)
        return result.modified_count > 0 or result.upserted_id is not None

    async def get_cached_product(
        self, url: str, cache_minutes: int = 30
    ) -> Optional[ProductResponse]:
        """Get product from cache if it's fresh enough"""
        product = await self.get_product_by_url(url)
        if product:
            # Check if cache is still valid
            cache_age = (datetime.utcnow() - product.updated_at).total_seconds() / 60
            if cache_age < cache_minutes:
                # Convert to response schema
                offers = [
                    OfferSchema(
                        url=offer.url,
                        original_url=offer.original_url,
                        title=offer.title,
                        shop=offer.shop,
                        price=offer.price,
                        is_used=offer.is_used,
                    )
                    for offer in product.offers
                ]
                return ProductResponse(url=product.url, offers=offers)
        return None

    async def save_or_update_product(self, product_data: ProductResponse) -> str:
        """Save new product or update existing one"""
        existing_product = await self.get_product_by_url(str(product_data.url))

        if existing_product:
            update_dict = {
                "$set": {
                    "offers": [offer.dict() for offer in product_data.offers],
                    "updated_at": datetime.utcnow(),
                }
            }
            await self.update_product({"url": str(product_data.url)}, update_dict)
            return str(existing_product.id)
        else:
            return await self.create_product(product_data)


product_repository = ProductRepository()
