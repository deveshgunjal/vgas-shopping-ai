"""Stealth Crawler v2 - Anti-Bot Evasion"""
import asyncio
from typing import Dict, Optional
from datetime import datetime

class StealthCrawler:
    """Advanced anti-bot evasion crawler"""
    
    def __init__(self):
        self.browser = None
    
    async def init_browser(self):
        """Initialize stealth browser"""
        try:
            import undetected_chromedriver as uc
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.browser = uc.Chrome(options=options)
        except ImportError:
            pass
    
    async def crawl_with_stealth(self, url: str) -> Dict:
        """Crawl URL with anti-bot evasion"""
        try:
            if self.browser:
                self.browser.get(url)
                await asyncio.sleep(2)
                
                title = self.browser.title
                page_source = self.browser.page_source
                
                return {
                    "url": url,
                    "title": title,
                    "status": "success",
                    "method": "stealth_browser",
                }
            else:
                # Fallback to httpx
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, follow_redirects=True, timeout=15)
                    return {
                        "url": url,
                        "status": "success",
                        "method": "httpx_fallback",
                        "status_code": resp.status_code,
                    }
        except Exception as e:
            return {"url": url, "status": "error", "error": str(e)}
    
    async def extract_json_data(self, url: str) -> Optional[Dict]:
        """Extract hidden JSON data from DOM"""
        try:
            if self.browser:
                self.browser.get(url)
                await asyncio.sleep(2)
                
                # Try to find JSON-LD or embedded data
                scripts = self.browser.find_elements("css selector", 'script[type="application/ld+json"]')
                if scripts:
                    import json
                    return json.loads(scripts[0].get_attribute("innerHTML"))
        except Exception:
            pass
        return None

stealth_crawler = StealthCrawler()
