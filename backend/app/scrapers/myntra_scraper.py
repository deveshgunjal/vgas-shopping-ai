"""
Myntra Scraper for VGAS Shopping AI
Developed by: Vikas Gunjal (VGAS)
"""

import re
import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MyntraScraper:
    """Scraper for Myntra.com (Fashion)"""

    BASE_URL = "https://www.myntra.com"
    SEARCH_URL = "https://www.myntra.com/{query}?rawQuery={query}&sort=price_asc"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Referer": "https://www.myntra.com/",
    }

    def __init__(self):
        self.affiliate_tag = "vgas-myntra-affiliate"

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        """Search fashion products on Myntra"""
        try:
            import aiohttp

            url = self.SEARCH_URL.format(query=query.replace(" ", "-").lower())
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    html = await response.text()
                    return self._parse_results(html, limit)
        except Exception as e:
            logger.error(f"Myntra search error: {e}")
            return []

    def _parse_results(self, html: str, limit: int) -> list:
        """Parse Myntra search results"""
        try:
            soup = BeautifulSoup(html, "lxml")
            products = []
            cards = soup.select("li.product-base")[:limit]

            for card in cards:
                try:
                    name_el = card.select_one("h3.product-brand, h4.product-product")
                    price_el = card.select_one(
                        "span.product-discountedPrice, div.product-price strong"
                    )
                    orig_el = card.select_one("span.product-strike")
                    disc_el = card.select_one("span.product-discountPercentage")
                    img_el = card.select_one("img.img-responsive, picture source")
                    link_el = card.select_one("a")
                    rating_el = card.select_one("div.product-ratingsContainer span")

                    if not name_el:
                        continue

                    name = name_el.get_text(strip=True)
                    price = float(
                        re.sub(
                            r"[^\d.]", "", price_el.get_text() if price_el else "1999"
                        )
                        or 1999
                    )
                    orig = float(
                        re.sub(
                            r"[^\d.]", "", orig_el.get_text() if orig_el else str(price)
                        )
                        or price
                    )
                    disc = int(
                        re.sub(r"[^\d]", "", disc_el.get_text() if disc_el else "0")
                        or 0
                    )
                    img = img_el.get("src", "") if img_el else ""
                    href = link_el.get("href", "") if link_el else ""
                    link = (
                        f"{self.BASE_URL}/{href}"
                        if not href.startswith("http")
                        else href
                    )
                    rating = (
                        float(rating_el.get_text(strip=True) if rating_el else "0")
                        or 4.0
                    )

                    products.append(
                        {
                            "name": name,
                            "price": price,
                            "original_price": orig,
                            "discount_percentage": disc,
                            "image": img,
                            "url": self._affiliate_link(link),
                            "store": "myntra.com",
                            "rating": rating,
                            "currency": "INR",
                            "in_stock": True,
                            "category": "Fashion",
                        }
                    )
                except Exception:
                    continue

            return products if products else []
        except Exception as e:
            logger.error(f"Myntra parse error: {e}")
            return []

    def _affiliate_link(self, url: str) -> str:
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}utm_source=VGAS&utm_medium=affiliate&utm_campaign=vgas2024"
