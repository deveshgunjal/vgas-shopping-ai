"""
Flipkart Scraper - VGAS Shopping AI
SAM Upgraded: Crawl4AI + Scrapling + Anti-Bot Bypass
"""

import re
import json
import asyncio
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class FlipkartScraper:
    BASE_URL = "https://www.flipkart.com"
    SEARCH_URL = "https://www.flipkart.com/search?q={query}&sort=price_asc"
    AFFILIATE_TAG = "vgas2024"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.flipkart.com/",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
    }

    # SAM-detected CSS selectors (Crawl4AI scan 2025)
    PRICE_SELECTORS = [
        "div._1psv1ze2c", "div.css-g5y9jx", "div.Nx9bqj._4b5DiR",
        "div.Nx9bqj", "div._30jeq3._16Jk6d", "div._30jeq3",
    ]
    NAME_SELECTORS = [
        "span.VU-ZEz", "span.B_NuCI", "h1.yhB1nd", "h1._6EBuvT",
        "div._4rR01T", "a.s1Q9rs", "div.KzDlHZ", "h1",
    ]
    ORIG_SELECTORS = [
        "div._1psv1zekc", "div.yRaY8j", "div._3I9_wc._2p6lqe", "div._2p6lqe",
    ]
    DISC_SELECTORS = [
        "div.UkUFwK span", "div._3Ay6Sb span", "div.UOCQB1",
    ]
    RATING_SELECTORS = [
        "div.XQDdHH", "div._3LWZlK", "div.ipqd2A",
    ]
    IMG_SELECTORS = [
        "img._396cs4", "img.DByuf4", "img._2r_T1I", "div._3kidJX img",
    ]

    async def get_product_details(self, url: str) -> Dict[str, Any]:
        """Get product details - tries Crawl4AI first, falls back to aiohttp"""
        result = await self._scrape_with_crawl4ai(url)
        if result and result.get("name") and result["name"] != "Unknown":
            return result
        logger.info("Crawl4AI fallback -> aiohttp scraper")
        return await self._scrape_with_aiohttp(url)

    async def extract_product_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        return await self.get_product_details(url)

    async def _scrape_with_crawl4ai(self, url: str) -> Dict[str, Any]:
        """Use Crawl4AI with stealth mode"""
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

            browser_cfg = BrowserConfig(
                headless=True,
                verbose=False,
                extra_args=["--disable-blink-features=AutomationControlled"],
            )
            run_cfg = CrawlerRunConfig(
                wait_for="css:div.Nx9bqj, css:span.VU-ZEz, css:span.B_NuCI",
                page_timeout=25000,
                simulate_user=True,
                magic=True,
            )
            async with AsyncWebCrawler(config=browser_cfg) as crawler:
                res = await crawler.arun(url=url, config=run_cfg)
                if res.success and res.html:
                    return self._parse_html(res.html, url)
        except Exception as e:
            logger.warning(f"Crawl4AI error: {e}")
        return {}

    async def _scrape_with_aiohttp(self, url: str) -> Dict[str, Any]:
        """Fallback: aiohttp with updated headers"""
        try:
            import aiohttp
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=20), allow_redirects=True) as r:
                    html = await r.text()
                    return self._parse_html(html, url)
        except Exception as e:
            logger.error(f"aiohttp error: {e}")
            return {"error": str(e), "url": url}

    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse Flipkart HTML with multiple selector fallbacks"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            name = self._extract_text(soup, self.NAME_SELECTORS) or self._extract_from_title(soup)
            price_text = self._extract_text(soup, self.PRICE_SELECTORS)
            orig_text = self._extract_text(soup, self.ORIG_SELECTORS)
            disc_text = self._extract_text(soup, self.DISC_SELECTORS)
            rating_text = self._extract_text(soup, self.RATING_SELECTORS)
            img = self._extract_attr(soup, self.IMG_SELECTORS, "src")

            price = self._to_float(price_text)
            orig = self._to_float(orig_text) or price

            # Fallback: scan all elements for rupee prices
            if not price:
                rupee_els = [(el.get("class"), el.get_text(strip=True))
                             for el in soup.find_all(["div","span"], class_=True)
                             if "\u20b9" in el.get_text(strip=True) and len(el.get_text(strip=True)) < 15]
                prices_sorted = sorted(rupee_els, key=lambda x: self._to_float(x[1]))
                if prices_sorted:
                    price = self._to_float(prices_sorted[0][1])
                    orig = self._to_float(prices_sorted[-1][1]) if len(prices_sorted) > 1 else price
            disc = self._to_int(disc_text)

            # Recalculate discount if missing
            if not disc and orig > price > 0:
                disc = round(((orig - price) / orig) * 100)

            specs = self._extract_specs(soup)

            return {
                "name": name or "Unknown",
                "price": price,
                "original_price": orig,
                "discount_percentage": disc,
                "image": img,
                "url": self._to_affiliate_link(url),
                "store": "flipkart.com",
                "rating": self._to_float(rating_text),
                "currency": "INR",
                "in_stock": self._check_stock(soup),
                "specifications": specs,
                "fake_discount": self._detect_fake_discount(price, orig, disc),
                "fake_discount_recommendation": self._fake_disc_msg(price, orig, disc),
            }
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return {"error": str(e), "url": url}

    def _extract_text(self, soup, selectors: list) -> str:
        for sel in selectors:
            try:
                el = soup.select_one(sel)
                if el:
                    t = el.get_text(strip=True)
                    if t:
                        return t
            except Exception:
                continue
        return ""

    def _extract_attr(self, soup, selectors: list, attr: str) -> str:
        for sel in selectors:
            try:
                el = soup.select_one(sel)
                if el and el.get(attr):
                    return el[attr]
            except Exception:
                continue
        return ""

    def _extract_from_title(self, soup) -> str:
        if soup.title:
            t = soup.title.text
            return t.split(" - ")[0].split(" | ")[0].strip()
        return ""

    def _extract_specs(self, soup) -> dict:
        specs = {}
        try:
            rows = soup.select("tr.WJdYP6, div._2TUkqQ, tr._1s_Smc, div._14cfVK")
            for row in rows[:20]:
                key = row.select_one("td.col-3-12, td._1UhVsV, td:first-child")
                val = row.select_one("td.col-9-12, td._1bK22P, td:last-child")
                if key and val:
                    specs[key.get_text(strip=True)] = val.get_text(strip=True)
        except Exception:
            pass
        return specs

    def _check_stock(self, soup) -> bool:
        oos = soup.select_one("div._16FRp0, div.Z8JjpR, [class*='out-of-stock']")
        return oos is None

    def _to_float(self, text: str) -> float:
        try:
            return float(re.sub(r"[^\d.]", "", text) or 0)
        except Exception:
            return 0.0

    def _to_int(self, text: str) -> int:
        try:
            return int(re.sub(r"[^\d]", "", text) or 0)
        except Exception:
            return 0

    def _to_affiliate_link(self, url: str) -> str:
        if not url:
            return url
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}affid={self.AFFILIATE_TAG}&affExtParam1=VGAS-VIKAS"

    def _detect_fake_discount(self, price: float, orig: float, disc: int) -> bool:
        if orig <= 0 or price <= 0:
            return False
        actual = round(((orig - price) / orig) * 100)
        return abs(actual - disc) > 10

    def _fake_disc_msg(self, price: float, orig: float, disc: int) -> str:
        if self._detect_fake_discount(price, orig, disc):
            actual = round(((orig - price) / orig) * 100)
            return f"⚠️ Fake Discount! Claimed {disc}% but actual is {actual}%"
        return "✅ Discount appears genuine"

    async def search_products(self, query: str, page: int = 1, limit: int = 10) -> list:
        """Search Flipkart products"""
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            search_url = self.SEARCH_URL.format(query=query.replace(" ", "+"))
            async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=20)) as r:
                    html = await r.text()
                    return self._parse_search(html, limit)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def _parse_search(self, html: str, limit: int) -> list:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            products = []
            cards = soup.select("div[data-id]")[:limit]
            for card in cards:
                try:
                    name = self._extract_text(card, self.NAME_SELECTORS)
                    price = self._to_float(self._extract_text(card, self.PRICE_SELECTORS))
                    orig = self._to_float(self._extract_text(card, self.ORIG_SELECTORS)) or price
                    disc = self._to_int(self._extract_text(card, self.DISC_SELECTORS))
                    img = self._extract_attr(card, self.IMG_SELECTORS, "src")
                    link_el = card.select_one("a._1fQZEK, a.s1Q9rs, a.IRpwTa, a[href*='/p/']")
                    link = self.BASE_URL + link_el["href"] if link_el else ""
                    rating = self._to_float(self._extract_text(card, self.RATING_SELECTORS))
                    if not name or not price:
                        continue
                    products.append({
                        "name": name, "price": price, "original_price": orig,
                        "discount_percentage": disc, "image": img,
                        "url": self._to_affiliate_link(link),
                        "store": "flipkart.com", "rating": rating,
                        "currency": "INR", "in_stock": True,
                    })
                except Exception:
                    continue
            return products
        except Exception as e:
            logger.error(f"Search parse error: {e}")
            return []
