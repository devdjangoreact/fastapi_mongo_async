import asyncio
from typing import List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from ..core.exceptions import ParsingException, TimeoutException
from ..schemas.product import OfferSchema, ProductResponse
from .browser_client import browser_client


class HotlineProductParser:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30)

    async def parse_product(
        self,
        url: str,
        timeout_limit: Optional[int] = None,
        count_limit: Optional[int] = None,
        price_sort: Optional[str] = None,
    ) -> ProductResponse:
        try:
            # Use browser client for JavaScript rendering
            content = await browser_client.get_page_content(
                url, timeout=timeout_limit or 30
            )
            soup = BeautifulSoup(content, "lxml")

            offers = await self._parse_offers(soup, url)

            # Apply sorting
            if price_sort:
                reverse = price_sort.lower() == "desc"
                offers.sort(key=lambda x: x.price, reverse=reverse)

            # Apply count limit
            if count_limit:
                offers = offers[:count_limit]

            return ProductResponse(url=url, offers=offers)

        except asyncio.TimeoutError:
            raise TimeoutException("Product parsing timeout")
        except Exception as e:
            raise ParsingException(f"Failed to parse product: {str(e)}")

    async def _parse_offers(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[OfferSchema]:
        offers = []

        # Parse offers from Hotline product page
        offer_elements = soup.select(".offer__item") or soup.select('[class*="offer"]')

        for offer in offer_elements[:20]:  # Limit to first 20 offers
            try:
                price_element = offer.select_one(".price__value") or offer.select_one(
                    '[class*="price"]'
                )
                shop_element = offer.select_one(".shop__name") or offer.select_one(
                    '[class*="shop"]'
                )
                link_element = offer.select_one("a") or offer.select_one("[href]")

                if not all([price_element, shop_element, link_element]):
                    continue

                price_text = price_element.get_text().strip()
                price = (
                    float("".join(filter(str.isdigit, price_text))) if price_text else 0
                )

                shop = shop_element.get_text().strip()
                offer_url = link_element.get("href", "")

                if offer_url and not offer_url.startswith("http"):
                    offer_url = f"https://hotline.ua{offer_url}"

                # Get original URL by following the redirect
                original_url = await self._get_original_url(offer_url)

                offers.append(
                    OfferSchema(
                        url=offer_url,
                        original_url=original_url or offer_url,
                        title=f"Offer from {shop}",
                        shop=shop,
                        price=price,
                        is_used=False,  # You might need to parse this from the page
                    )
                )

            except Exception:
                continue

        return offers

    async def _get_original_url(self, offer_url: str) -> Optional[str]:
        try:
            async with self.client:
                response = await self.client.get(offer_url, follow_redirects=True)
                return str(response.url)
        except Exception:
            return None

    async def close(self):
        await self.client.aclose()


product_parser = HotlineProductParser()
product_parser = HotlineProductParser()
