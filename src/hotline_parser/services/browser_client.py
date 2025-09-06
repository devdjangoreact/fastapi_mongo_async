import asyncio
from typing import Optional

from playwright.async_api import Browser, Page, async_playwright

from ..core.exceptions import TimeoutException


class BrowserClient:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_page_content(self, url: str, timeout: int = 30) -> str:
        if not self.browser:
            await self.start()

        context = await self.browser.new_context()
        page: Page = await context.new_page()

        try:
            await page.goto(url, timeout=timeout * 1000)
            content = await page.content()
            return content
        except asyncio.TimeoutError:
            raise TimeoutException("Browser timeout exceeded")
        finally:
            await context.close()


browser_client = BrowserClient()
