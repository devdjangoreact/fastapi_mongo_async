import asyncio
import json
import os
import re
from datetime import datetime
from typing import Any, List, Optional

import lxml.html
from bs4 import BeautifulSoup
from lxml import etree

from ..core.exceptions import ParsingException, TimeoutException
from ..core.logger import log
from ..repositories.product_repository import product_repository
from ..schemas.product import OfferSchema, ProductResponse
from .browser_client import browser_client


class HotlineProductParser:
    def __init__(self):
        self.mock_data = self._load_mock_data()

    def _load_mock_data(self) -> dict:
        """Load mock data from JSON file"""
        try:
            mock_file = os.path.join("mock_data", "product_mock_data.json")
            with open(mock_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading mock data: {e}")
            return {}

    def _create_product_objects_from_json(
        self, json_data: List[dict]
    ) -> List[ProductResponse]:
        """Create ProductResponse objects from JSON data"""
        products = []

        for product_data in json_data.get("products", []):
            try:
                # Convert string dates to datetime objects
                product_data["created_at"] = datetime.fromisoformat(
                    product_data["created_at"].replace("Z", "+00:00")
                )
                product_data["updated_at"] = datetime.fromisoformat(
                    product_data["updated_at"].replace("Z", "+00:00")
                )

                # Create schema objects
                offers = [
                    OfferSchema(**offer) for offer in product_data.get("offers", [])
                ]

                product = ProductResponse(
                    url=product_data["url"],
                    offers=offers,
                    created_at=product_data["created_at"],
                    updated_at=product_data["updated_at"],
                )
                products.append(product)
            except Exception as e:
                print(f"Error creating product object: {e}")
                continue

        return products

    async def parse_product(
        self,
        url: str,
        timeout_limit: Optional[int] = None,
        count_limit: Optional[int] = None,
        price_sort: Optional[str] = None,
    ) -> ProductResponse:

        async def start_loading_page():
            await page.goto(url, wait_until="load")

            # Get initial page height
            total_height = await page.evaluate("document.body.scrollHeight")
            current_position = 0
            scroll_step = await page.evaluate(
                "window.innerHeight"
            )  # Scroll by one viewport height

            while current_position < total_height:
                # Scroll by one viewport height
                current_position += scroll_step
                await page.evaluate(f"window.scrollTo(0, {current_position})")

                # Wait for content to load
                await asyncio.sleep(0.3)

                # Check if page height changed (new content loaded)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height > total_height:
                    total_height = new_height

                # Stop if we reached the bottom
                if current_position >= total_height:
                    break

        try:
            log.info(f"Starting product parsing: {url}")

            # Check if we have mock data for this URL
            # mock_products = self._create_product_objects_from_json(self.mock_data)
            # for product in mock_products:
            #     # Create a simple product object with only required fields
            #     simple_product = ProductResponse(
            #         url=str(product.url), offers=product.offers
            #     )
            #     # Save each mock product to database using repository
            #     await product_repository.save_or_update_product(simple_product)

            # for product in mock_products:
            #     if product.url == url:
            #         log.info(f"Using mock data for product: {url}")
            #         return product

            offers = []
            async with browser_client.start_context_manager() as browser:
                context = await browser.new_context()
                page = await context.new_page()
                try:
                    if timeout_limit:
                        async with asyncio.timeout(timeout_limit):
                            await start_loading_page()
                    else:
                        await start_loading_page()

                except Exception as e:
                    log.error(f"Error getting page content: {e}")
                finally:
                    # Get page content
                    page_content = await page.content()
                    offers = await self._parse_offers(page_content)
                    await context.close()

            # Apply sorting
            if price_sort:
                reverse = price_sort.lower() == "desc"
                offers.sort(key=lambda x: x.price, reverse=reverse)

            # Apply count limit
            if count_limit:
                offers = offers[:count_limit]

            result = ProductResponse(url=url, offers=offers)
            await product_repository.save_or_update_product(result)
            log.success(f"Product parsed successfully: {url}, offers: {len(offers)}")
            return result

        except asyncio.TimeoutError:
            log.error(f"Product parsing timeout: {url}")
            raise TimeoutException("Product parsing timeout")
        except Exception as e:
            log.error(f"Failed to parse product {url}: {str(e)}")
            raise ParsingException(f"Failed to parse product: {str(e)}")

    async def _parse_offers(self, page_content: str) -> List[OfferSchema]:

        soup = BeautifulSoup(page_content, "html.parser")
        _offers = []
        offers = []

        # Конвертуємо BeautifulSoup об'єкт у lxml для XPath
        root = lxml.html.fromstring(str(soup))

        # Знаходимо всі елементи пропозицій за допомогою XPath
        offer_elements = root.xpath(
            "//div[@id='productOffersListContainer']/div[2]/div"
        )

        for element in offer_elements:
            try:
                # URL
                url_element = element.xpath('.//a[contains(@href, "/go/price/")]')
                url = (
                    f"https://hotline.ua{url_element[0].get('href')}"
                    if url_element
                    else ""
                )
                original_url = url_element[0].get("href") if url_element else ""

                # shop
                shop_element = element.xpath(
                    './/a[contains(@href, "/go/price/")]/text()'
                )
                shop = shop_element[0].strip() if shop_element else ""

                # title
                title_element = element.xpath(
                    './/div[contains(@class, "html-clamp")]//text()'
                )
                full_title = " ".join(title_element).strip() if title_element else ""
                text_ignore = ["Oплата", "карткою", "розрахунок", "післяплата", "..."]
                _title = [
                    text.strip()
                    for text in title_element
                    if text.strip()
                    and not any(
                        ignore_word in text.lower() for ignore_word in text_ignore
                    )
                ]
                title = " ".join(_title).strip()
                # price
                # price = self._extract_price_from_element(element)
                full_text = element.xpath('.//a[contains(@href, "/go/price/")]')
                price_elements = element.xpath(
                    './/span[contains(@class, "_2FyrEE_quFxElmhGj53m")]'
                )
                price = 0

                if price_elements and price_elements[0].text:
                    price_text = price_elements[0].text.strip()
                    if price_text:
                        print(price_text)
                        try:
                            price = float(
                                price_text.replace("\xa0", "")
                                .replace(" ", "")
                                .replace("​", "")
                            )
                        except ValueError:
                            price = 0
                is_used = (
                    "б/в" in full_title.lower()
                    or "б/y" in full_title.lower()
                    or "used" in full_title.lower()
                    or "вживаний" in full_title.lower()
                )

                offer = {
                    "url": url,
                    "original_url": original_url,
                    "title": title,
                    "shop": shop,
                    "price": price,
                    "is_used": is_used,
                }

                _offers.append(offer)

            except Exception as e:
                print(f"Error parsing offer: {e}")
                continue

        offers = [OfferSchema(**offer) for offer in _offers]
        return offers

    def _extract_price_from_element(self, element) -> Optional[float]:
        """
        Extract price from lxml element using relative XPath queries

        Args:
            element: lxml element representing a single offer

        Returns:
            Extracted price as float or None if not found
        """
        # Try multiple XPath patterns relative to the current element
        xpath_patterns = [
            './/a[contains(@class, "zrhvSTwrLmXpudZJHe9F")]//span[contains(@class, "_2FyrEE_quFxElmhGj53m")]//span//span',
            './/div[contains(@class, "_2hI96L2lvznnoUgTXaNE")]//a//span//span//span//span//span//span//span//span',
            './/span[contains(@class, "_2FyrEE_quFxElmhGj53m")]//span//span',
            './/*[contains(text(), "₴")]',  # Any element containing currency symbol
        ]
        price = None
        for xpath in xpath_patterns:
            try:
                price_elements = element.xpath(xpath)
                for price_element in price_elements:
                    if price_element.text:
                        price_text = price_element.text.strip()
                        price = self._clean_price_text(price_text)
                        if price:
                            return price
                    # Also check tail text for elements with mixed content
                    if price_element.tail:
                        price_text = price_element.tail.strip()
                        price = self._clean_price_text(price_text)
                        if price:
                            return price
            except Exception as e:
                print(f"XPath extraction error for pattern {xpath}: {e}")
                continue
        return price


product_parser = HotlineProductParser()
