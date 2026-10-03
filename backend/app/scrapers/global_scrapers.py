"""
Global Scrapers (Walmart, eBay, AliExpress, Noon) for VGAS Shopping AI
Developed by: Vikas Gunjal (VGAS)
"""

import re
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WalmartScraper:
    """Scraper for Walmart.com (USA)"""

    BASE_URL = "https://www.walmart.com"
    SEARCH_URL = "https://www.walmart.com/search?q={query}&sort=price_low"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        try:
            import aiohttp

            url = self.SEARCH_URL.format(query=query.replace(" ", "+"))
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    html = await response.text()
                    return self._parse(html, limit)
        except Exception as e:
            logger.error(f"Walmart error: {e}")
            return []

    def _parse(self, html: str, limit: int) -> list:
        try:
            soup = BeautifulSoup(html, "lxml")
            items = soup.select("div[data-item-id]")[:limit]
            products = []
            for item in items:
                name = item.select_one("span.normal.dark-gray")
                price = item.select_one(
                    "div.price-main span.visuallyhidden, span.w_iUH7"
                )
                img = item.select_one("img.db.absolute")
                link = item.select_one("a.absolute")
                if not name or not price:
                    continue
                price_val = float(re.sub(r"[^\d.]", "", price.get_text()) or 0)
                products.append(
                    {
                        "name": name.get_text(strip=True),
                        "price": price_val,
                        "original_price": price_val,
                        "discount_percentage": 0,
                        "image": img.get("src", "") if img else "",
                        "url": self.BASE_URL + (link.get("href", "") if link else ""),
                        "store": "walmart.com",
                        "currency": "USD",
                        "rating": 4.0,
                        "in_stock": True,
                    }
                )
            return products if products else []
        except Exception as e:
            return []


class EbayScraper:
    """Scraper for eBay.com"""

    SEARCH_URL = "https://www.ebay.com/sch/i.html?_nkw={query}&_sop=15"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        try:
            import aiohttp

            url = self.SEARCH_URL.format(query=query.replace(" ", "+"))
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    html = await response.text()
                    return self._parse(html, limit)
        except Exception as e:
            logger.error(f"eBay error: {e}")
            return []

    def _parse(self, html: str, limit: int) -> list:
        try:
            soup = BeautifulSoup(html, "lxml")
            items = soup.select("li.s-item")[: limit + 2]
            products = []
            for item in items:
                name = item.select_one("div.s-item__title")
                price = item.select_one("span.s-item__price")
                img = item.select_one("img.s-item__image-img")
                link = item.select_one("a.s-item__link")
                if not name or "results" in (name.get_text() or "").lower():
                    continue
                price_text = price.get_text() if price else "0"
                price_val = float(re.sub(r"[^\d.]", "", price_text.split("to")[0]) or 0)
                products.append(
                    {
                        "name": name.get_text(strip=True),
                        "price": price_val,
                        "original_price": price_val,
                        "discount_percentage": 0,
                        "image": img.get("src", "") if img else "",
                        "url": link.get("href", "") if link else "",
                        "store": "ebay.com",
                        "currency": "USD",
                        "rating": 4.0,
                        "in_stock": True,
                    }
                )
            return products[:limit] if products else []
        except Exception:
            return []


class AliExpressScraper:
    """Scraper for AliExpress.com"""

    SEARCH_URL = (
        "https://www.aliexpress.com/wholesale?SearchText={query}&SortType=price_asc"
    )
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        try:
            import aiohttp

            url = self.SEARCH_URL.format(query=query.replace(" ", "+"))
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=25)
                ) as response:
                    html = await response.text()
                    return self._parse(html, limit)
        except Exception as e:
            logger.error(f"AliExpress error: {e}")
            return []

    def _parse(self, html: str, limit: int) -> list:
        try:
            soup = BeautifulSoup(html, "lxml")
            items = soup.select("div.list--gallery--C2f2tvm")[:limit]
            if not items:
                items = soup.select("a.search-card-item")[:limit]
            products = []
            for item in items:
                name = item.select_one("h3, div.item-title")
                price = item.select_one(
                    "div.price--current--I3Zeidd, strong.price-original"
                )
                img = item.select_one("img.product-img")
                link = item.select_one("a") or item if item.name == "a" else None
                if not name:
                    continue
                price_val = float(
                    re.sub(r"[^\d.]", "", price.get_text() if price else "5") or 5
                )
                href = link.get("href", "") if link else ""
                url = f"https:{href}" if href.startswith("//") else href
                products.append(
                    {
                        "name": name.get_text(strip=True)[:100],
                        "price": price_val,
                        "original_price": price_val * 1.5,
                        "discount_percentage": 33,
                        "image": img.get("src", "") if img else "",
                        "url": url,
                        "store": "aliexpress.com",
                        "currency": "USD",
                        "rating": 4.3,
                        "in_stock": True,
                    }
                )
            return products if products else []
        except Exception:
            return []


class NoonScraper:
    """Scraper for Noon.com (UAE/Middle East)"""

    SEARCH_URL = (
        "https://www.noon.com/uae-en/search/?q={query}&sort[by]=price&sort[dir]=asc"
    )
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-AE,en;q=0.9",
    }

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        try:
            import aiohttp

            url = self.SEARCH_URL.format(query=query.replace(" ", "+"))
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    html = await response.text()
                    # Noon requires JS rendering; return empty result when not available.
                    return []
        except Exception as e:
            logger.error(f"Noon error: {e}")
            return []


class MeeshoScraper:
    """Scraper for Meesho.com (India)"""

    SEARCH_URL = "https://www.meesho.com/search?q={query}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    }

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        try:
            import aiohttp

            url = self.SEARCH_URL.format(query=query.replace(" ", "%20"))
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    html = await response.text()
                    # Meesho has heavy anti-bot protections; return empty results when unavailable.
                    return []
        except Exception as e:
            logger.error(f"Meesho error: {e}")
            return []


class GlobalScrapers:
    """Factory for global scrapers"""

    _scrapers = {
        "walmart": WalmartScraper,
        "ebay": EbayScraper,
        "aliexpress": AliExpressScraper,
        "noon": NoonScraper,
        "meesho": MeeshoScraper,
    }

    @classmethod
    def get_scraper(cls, name: str):
        scraper_class = cls._scrapers.get(name.lower())
        if scraper_class:
            return scraper_class()
        return None

    @classmethod
    def get_all_scrapers(cls) -> dict:
        return {name: cls() for name, cls in cls._scrapers.items()}
