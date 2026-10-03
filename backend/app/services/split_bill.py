"""Split the Bill - Viral Referral Feature"""
from typing import Dict
import hashlib

class SplitBill:
    """Viral split bill feature for deal sharing"""
    
    def __init__(self):
        self.shares = []
    
    def create_share_link(self, product_url: str, user_id: int) -> Dict:
        """Create a shareable deal link"""
        slug = hashlib.md5(f"{product_url}{user_id}".encode()).hexdigest()[:8]
        share_url = f"http://localhost:8000/share/{slug}"
        
        share = {
            "slug": slug,
            "original_url": product_url,
            "user_id": user_id,
            "share_url": share_url,
            "clicks": 0,
            "conversions": 0,
        }
        self.shares.append(share)
        
        return share
    
    def track_click(self, slug: str, referrer_ip: str) -> Dict:
        """Track click on shared link"""
        for share in self.shares:
            if share["slug"] == slug:
                share["clicks"] += 1
                return {"status": "tracked", "original_url": share["original_url"]}
        return {"status": "not_found"}
    
    def track_conversion(self, slug: str) -> Dict:
        """Track when friend makes a purchase"""
        for share in self.shares:
            if share["slug"] == slug:
                share["conversions"] += 1
                # Both referrer and referee get cashback
                return {
                    "status": "conversion",
                    "referrer_reward": 50,
                    "referee_reward": 50,
                    "total_payout": 100,
                }
        return {"status": "not_found"}

split_bill = SplitBill()
