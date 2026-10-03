"""
Base Scraper class for VGAS Shopping AI
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError
from bs4 import BeautifulSoup
import asyncio
import re
import json
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base scraper class with common functionality"""
    
    def __init__(self, name: str = "Generic", country: str = "in", currency: str = "INR"):
        self.name = name
        self.country = country
        self.currency = currency
        self.base_url = ""
        self.timeout = settings.SCRAPER_TIMEOUT * 1000  # Convert to milliseconds
        self.user_agent = settings.USER_AGENT
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def init_browser(self) -> Browser:
        """Initialize Playwright browser"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        
        if self.browser is None:
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--single-process",
                    "--no-zygote",
                ]
            )
        return self.browser
    
    async def get_page(self) -> Page:
        """Get a new browser page"""
        await self.init_browser()
        
        if self.context is None:
            self.context = await self.browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True,
                ignore_https_errors=True,
                bypass_csp=True,
            )
            
            # Set cookies and local storage
            await self.context.add_cookies([])
        
        self.page = await self.context.new_page()
        await self.page.set_extra_http_headers(self.headers)
        
        return self.page
    
    async def close(self):
        """Close browser resources"""
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    async def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc.lower()
    
    async def is_whitelisted(self, url: str) -> bool:
        """Check if URL is from whitelisted domain"""
        domain = await self.extract_domain(url)
        return domain in settings.WHITELISTED_DOMAINS
    
    async def normalize_url(self, url: str) -> str:
        """Normalize URL (preserve case - some sites serve 404 for lowercased paths)"""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url
    
    async def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object from URL"""
        try:
            page = await self.get_page()
            await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
            html = await page.content()
            return BeautifulSoup(html, "lxml")
        except TimeoutError:
            logger.warning(f"Timeout while loading {url}")
            return None
        except Exception as e:
            logger.error(f"Error loading {url}: {e}")
            return None
    
    async def extract_product_from_url(self, url: str) -> Optional[Dict]:
        """Extract product information from URL (to be overridden by specific scrapers)"""
        soup = await self.get_soup(url)
        if not soup:
            return None
        
        return {
            "url": url,
            "scraped_at": datetime.utcnow().isoformat(),
            "scraper": self.name
        }
    
    async def search_products(self, query: str, page: int = 1, limit: int = 20) -> Dict:
        """Search products by name (to be overridden by specific scrapers)"""
        return {
            "query": query,
            "page": page,
            "limit": limit,
            "results": [],
            "total": 0,
            "scraper": self.name
        }
    
    async def detect_fake_discount(self, product_data: Dict) -> Dict:
        """Detect if discount is fake by checking price history"""
        result = {
            "is_fake_discount": False,
            "fake_reason": None,
            "confidence": 0.0,
            "price_history": [],
            "recommendation": "This appears to be a genuine discount"
        }
        
        try:
            # Check cache for price history
            cache_key = CacheKeys.PRICE_HISTORY.format(product_data.get("id", ""))
            price_history = await get_cache(cache_key)
            
            if price_history:
                result["price_history"] = price_history
                
                # Analyze price pattern
                if len(price_history) >= 3:
                    # Get recent prices
                    recent_prices = [ph["price"] for ph in price_history[:10]]
                    current_price = product_data.get("current_price", 0)
                    original_price = product_data.get("original_price", 0)
                    
                    # Check if original price was recently lower
                    if original_price > 0:
                        min_recent = min(recent_prices)
                        avg_recent = sum(recent_prices) / len(recent_prices)
                        
                        # If original price is higher than recent prices, it might be fake
                        if original_price > avg_recent * 1.1:  # More than 10% higher
                            result["is_fake_discount"] = True
                            result["fake_reason"] = "Original price was recently lower"
                            result["confidence"] = 0.85
                            result["recommendation"] = "⚠️ This discount might be fake! Original price was recently lower than current price."
                        
                        # Check if price was artificially inflated before sale
                        if original_price > max(recent_prices) * 1.05:
                            result["is_fake_discount"] = True
                            result["fake_reason"] = "Price was artificially inflated before sale"
                            result["confidence"] = 0.95
                            result["recommendation"] = "⚠️ FAKE DISCOUNT DETECTED! Price was increased just before this sale."
                    
                    # Check if discount percentage is too high
                    discount_pct = product_data.get("discount_percentage", 0)
                    if discount_pct > 80:
                        result["is_fake_discount"] = True
                        result["fake_reason"] = "Suspiciously high discount percentage"
                        result["confidence"] = 0.7
                        result["recommendation"] = "⚠️ Be cautious! Discount percentage seems too good to be true."
                        
        except Exception as e:
            logger.error(f"Error detecting fake discount: {e}")
        
        return result
    
    async def generate_affiliate_link(self, product_url: str) -> str:
        """Generate affiliate link (to be overridden by specific scrapers)"""
        return product_url
    
    async def get_price_history(self, product_id: str) -> List[Dict]:
        """Get price history for a product"""
        cache_key = CacheKeys.PRICE_HISTORY.format(product_id)
        price_history = await get_cache(cache_key)
        return price_history if price_history else []
    
    async def extract_currency(self, price_text: str) -> Tuple[str, float]:
        """Extract currency and amount from price text"""
        # Common currency symbols
        currency_symbols = {
            "₹": "INR",
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
            "AED": "AED",
            "AED": "AED",
            "SAR": "SAR",
            "QAR": "QAR",
            "CAD": "CAD",
            "AUD": "AUD",
            "SGD": "SGD"
        }
        
        price_text = price_text.strip()
        
        # Check for currency symbols
        for symbol, currency in currency_symbols.items():
            if symbol in price_text:
                price_text = price_text.replace(symbol, "").strip()
                try:
                    amount = float(re.sub(r"[^\d.]", "", price_text))
                    return currency, amount
                except:
                    pass
        
        # Try to extract amount
        try:
            amount = float(re.sub(r"[^\d.]", "", price_text))
            return self.currency, amount
        except:
            return self.currency, 0.0
    
    async def extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        return [float(num) for num in re.findall(r"\d+\.?\d*", text)]
    
    async def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)
        return text
    
    async def extract_json_ld(self, soup: BeautifulSoup, type_name: str = "Product") -> Optional[Dict]:
        """Extract JSON-LD data from page"""
        scripts = soup.find_all("script", {"type": "application/ld+json"})
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == type_name:
                            return item
                elif data.get("@type") == type_name:
                    return data
            except:
                continue
        return None
