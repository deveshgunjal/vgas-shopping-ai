"""Affiliate Link Manager"""
import hashlib
from typing import Dict

AFFILIATE_TAGS = {
    "amazon": "vgas-21",
    "flipkart": "vgasflip-21",
    "ebay": "vgasebay-21",
}

class AffiliateManager:
    def __init__(self):
        self.tags = AFFILIATE_TAGS
    
    def inject_affiliate(self, url: str, store: str) -> str:
        """Inject affiliate tag into product URL"""
        tag = self.tags.get(store, "")
        if not tag:
            return url
        
        if "amazon" in url.lower():
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}tag={tag}"
        elif "flipkart" in url.lower():
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}affid={tag}"
        
        return url
    
    def generate_tracking_url(self, product_url: str, user_id: int) -> str:
        """Generate tracking URL for analytics"""
        slug = hashlib.md5(f"{product_url}{user_id}".encode()).hexdigest()[:8]
        return f"http://localhost:8000/r/{slug}"

affiliate_manager = AffiliateManager()
