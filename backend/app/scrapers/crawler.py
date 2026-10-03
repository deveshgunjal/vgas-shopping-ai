"""Main Price Crawler"""
import httpx
import re
import json
from typing import Dict, Optional
from datetime import datetime
from .proxy_manager import proxy_manager

class PriceCrawler:
    """Multi-store price crawler with anti-bot bypass"""
    
    def __init__(self):
        self.stores = {
            "amazon": self._crawl_amazon,
            "flipkart": self._crawl_flipkart,
            "ebay": self._crawl_ebay,
        }
    
    async def crawl(self, url: str) -> Optional[Dict]:
        """Crawl a product URL and return price data"""
        store = self._detect_store(url)
        if store and store in self.stores:
            return await self.stores[store](url)
        return await self._generic_crawl(url)
    
    def _detect_store(self, url: str) -> Optional[str]:
        """Detect which store the URL belongs to"""
        url_lower = url.lower()
        if "amazon" in url_lower:
            return "amazon"
        elif "flipkart" in url_lower:
            return "flipkart"
        elif "ebay" in url_lower:
            return "ebay"
        return None
    
    async def _crawl_amazon(self, url: str) -> Dict:
        """Crawl Amazon product"""
        headers = proxy_manager.get_headers()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=15)
                html = resp.text
                
                title = self._extract_between(html, '<span id="productTitle"', '</span>')
                price = self._extract_price(html)
                image = self._extract_between(html, '<img id="landingImage"', 'src="', '"')
                
                return {
                    "store": "amazon",
                    "title": self._clean_text(title),
                    "price": price,
                    "url": url,
                    "image_url": image,
                    "crawled_at": datetime.utcnow().isoformat(),
                    "currency": "INR",
                    "in_stock": price is not None,
                }
            except Exception as e:
                return {"store": "amazon", "error": str(e), "url": url}
    
    async def _crawl_flipkart(self, url: str) -> Dict:
        """Crawl Flipkart product"""
        headers = proxy_manager.get_headers()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=15)
                html = resp.text
                
                title = self._extract_between(html, '<span class="B_NuCI">', '</span>')
                price_match = re.search(r'\u20b9([\d,]+\.?\d*)', html)
                price = float(price_match.group(1).replace(',', '')) if price_match else None
                
                return {
                    "store": "flipkart",
                    "title": self._clean_text(title),
                    "price": price,
                    "url": url,
                    "currency": "INR",
                    "in_stock": price is not None,
                    "crawled_at": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                return {"store": "flipkart", "error": str(e), "url": url}
    
    async def _crawl_ebay(self, url: str) -> Dict:
        """Crawl eBay product"""
        headers = proxy_manager.get_headers()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=15)
                html = resp.text
                
                title = self._extract_between(html, '<h1 class="x-item-title__mainTitle">', '</h1>')
                price_match = re.search(r'US \$([\d,]+\.?\d*)', html)
                price = float(price_match.group(1).replace(',', '')) if price_match else None
                
                return {
                    "store": "ebay",
                    "title": self._clean_text(title),
                    "price": price,
                    "url": url,
                    "currency": "USD",
                    "in_stock": price is not None,
                    "crawled_at": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                return {"store": "ebay", "error": str(e), "url": url}
    
    async def _generic_crawl(self, url: str) -> Dict:
        """Generic crawl for unknown stores"""
        headers = proxy_manager.get_headers()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=15)
                price_match = re.search(r'\u20b9([\d,]+\.?\d*)|\$([\d,]+\.?\d*)', resp.text)
                price = None
                currency = "INR"
                if price_match:
                    if price_match.group(1):
                        price = float(price_match.group(1).replace(',', ''))
                    elif price_match.group(2):
                        price = float(price_match.group(2).replace(',', ''))
                        currency = "USD"
                
                return {
                    "store": "generic",
                    "price": price,
                    "url": url,
                    "currency": currency,
                    "in_stock": price is not None,
                    "crawled_at": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                return {"store": "generic", "error": str(e), "url": url}
    
    def _extract_between(self, html: str, start_marker: str, end_marker: str) -> str:
        try:
            start = html.find(start_marker)
            if start == -1:
                return ""
            start = html.find(">", start) + 1
            end = html.find(end_marker, start)
            if end == -1:
                return ""
            return html[start:end].strip()
        except:
            return ""
    
    def _extract_price(self, html: str) -> float:
        match = re.search(r'\u20b9([\d,]+\.?\d*)', html)
        if match:
            return float(match.group(1).replace(',', ''))
        return None
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()[:200]

crawler = PriceCrawler()
