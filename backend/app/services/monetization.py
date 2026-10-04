"""Monetization Service for VGAS Shopping AI"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, AffiliateClick, Referral, Subscription
from app.core.redis_cache import get_cache, set_cache
from app.services.affiliate import affiliate_manager
import logging

logger = logging.getLogger(__name__)


class MonetizationService:
    """Handles all monetization: affiliate links, ads, premium, cashback"""

    def __init__(self):
        self.affiliate = affiliate_manager

    def generate_affiliate_link(self, product_url: str, store: str, user_id: int) -> str:
        """Generate monetized affiliate link"""
        affiliate_url = self.affiliate.inject_affiliate(product_url, store)
        tracking_url = self.affiliate.generate_tracking_url(product_url, user_id)
        
        # Log the click
        db = SessionLocal()
        try:
            click = AffiliateClick(
                user_id=user_id,
                product_id=0,
                store=store,
                clicked_at=datetime.utcnow(),
            )
            db.add(click)
            db.commit()
        finally:
            db.close()
        
        return tracking_url

    def get_ad_placement(self, page: str = "homepage") -> Dict:
        """Get ad configuration for a page.

        No ad network (AdMob / Google Ads) is integrated into this codebase, so
        there is nothing real to serve. Returning fabricated ad URLs here would
        make the UI render banners that lead nowhere, so placements stay empty
        and the UI must render its own "no ads" state.
        """
        return {
            "enabled": False,
            "reason": "No ad network is integrated — placements are intentionally empty.",
            "page": page,
            "placements": {},
        }

    def calculate_cashback(self, amount: float, user_id: int, plan: str = "free") -> Dict:
        """Compute the cashback rate for an amount.

        This is a rate calculation only. It is NOT a payout: no transfer is
        triggered here and no ledger row is written, so the result must not be
        presented to the user as money already owed to them.
        """
        base_rate = 2.0  # 2% base cashback rate (published rate)
        premium_bonus = 1.0 if plan in ["pro", "premium"] else 0.0
        total_rate = base_rate + premium_bonus

        cashback = amount * total_rate / 100

        return {
            "purchase_amount": amount,
            "cashback_rate": total_rate,
            "cashback_amount": round(cashback, 2),
            "currency": "INR",
            "payout_method": "UPI",
            "payout_status": "not_issued",
            "plan": plan,
            "note": "Rate estimate only. No payout system is connected and nothing has been transferred.",
        }

    def get_referral_stats(self, user_id: int, db: Session = None) -> Dict:
        """Get referral earnings statistics"""
        if db is None:
            db = SessionLocal()
        
        referrals = db.query(Referral).filter(Referral.referrer_id == user_id).all()
        total_referrals = len(referrals)
        total_earnings = sum(r.amount for r in referrals if r.status == "completed")
        pending = sum(1 for r in referrals if r.status == "pending")
        
        return {
            "total_referrals": total_referrals,
            "total_earnings": round(total_earnings, 2),
            "pending": pending,
            "completed": total_referrals - pending,
            "referral_code": "",
            "referral_url": f"https://vgas.ai/r/{user_id}",
        }

    def get_premium_features(self) -> Dict:
        """Get premium membership features"""
        return {
            "free": {
                "price": 0,
                "name": "Free",
                "features": ["5 product tracks", "6-hour scans", "Basic leaderboard", "Standard alerts"],
            },
            "pro": {
                "price": 99,
                "name": "Pro",
                "features": ["Unlimited tracks", "5-min scans", "Early alerts", "Ad-free", "Price history", "WhatsApp alerts"],
            },
            "premium": {
                "price": 299,
                "name": "Premium",
                "features": ["Everything in Pro", "API access", "White-label", "Priority support", "Instant UPI cashback", "Cashback on every purchase"],
            },
        }


monetization_service = MonetizationService()
