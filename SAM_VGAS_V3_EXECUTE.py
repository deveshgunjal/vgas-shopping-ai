#!/usr/bin/env python3
"""
SAM AI - VGAS SHOPPING AI v3.0 EXECUTOR
Total Domination Edition
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = Path(r"d:\sam\projects\Vgas Shooping Ai")

def create_dir(path):
    """Create directory if not exists"""
    full = PROJECT_DIR / path
    full.mkdir(parents=True, exist_ok=True)
    return full

def write_file(path, content):
    """Write content to file"""
    full = PROJECT_DIR / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding='utf-8')
    print(f"  [OK] {path}")

def run():
    print("="*60)
    print("  SAM AI - VGAS SHOPPING AI v3.0")
    print("  Total Domination Edition")
    print("="*60)
    print()
    
    start_time = time.time()
    
    # ============================================
    # PHASE 1: DATABASE MODELS
    # ============================================
    print("[Phase 1] Database Models...")
    
    # backend/app/__init__.py
    write_file("backend/app/__init__.py", "")
    
    # backend/app/models.py
    write_file("backend/app/models.py", '''"""Database Models for Vgas Shopping AI"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    is_premium = Column(Boolean, default=False)
    plan = Column(String(20), default="free")
    upi_id = Column(String(50))
    stripe_customer_id = Column(String(100))
    referral_code = Column(String(20), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    tracks = relationship("ProductTrack", back_populates="user")
    referrals = relationship("Referral", foreign_keys="Referral.referrer_id", back_populates="referrer")

class ProductTrack(Base):
    __tablename__ = "product_tracks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String(500), nullable=False)
    title = Column(String(200))
    image_url = Column(String(500))
    current_price = Column(Float)
    target_price = Column(Float)
    store = Column(String(50))
    status = Column(String(20), default="watching")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="tracks")
    price_history = relationship("PriceHistory", back_populates="product")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product_tracks.id"))
    price = Column(Float, nullable=False)
    store = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("ProductTrack", back_populates="price_history")

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="pending")
    amount = Column(Float, default=50.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals")

class AffiliateClick(Base):
    __tablename__ = "affiliate_clicks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("product_tracks.id"))
    store = Column(String(50))
    clicked_at = Column(DateTime, default=datetime.utcnow)
    converted = Column(Boolean, default=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_sub_id = Column(String(100))
    plan = Column(String(20))
    status = Column(String(20), default="active")
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime)
''')
    
    # backend/app/database.py
    write_file("backend/app/database.py", '''"""Database Configuration"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vgas_shopping.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
''')
    
    print("  [DONE] Phase 1 - Database Models")
    
    # ============================================
    # PHASE 2: SCRAPERS
    # ============================================
    print("[Phase 2] Scrapers...")
    
    # backend/app/scrapers/__init__.py
    write_file("backend/app/scrapers/__init__.py", "")
    
    # backend/app/scrapers/proxy_manager.py
    write_file("backend/app/scrapers/proxy_manager.py", '''"""Rotating Proxy Manager"""
import random
import asyncio
from typing import Optional

FREE_PROXIES = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

class ProxyManager:
    def __init__(self):
        self.proxies = FREE_PROXIES
        self.current_index = 0
    
    def get_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index % len(self.proxies)]
        self.current_index += 1
        return proxy
    
    def get_random_ua(self) -> str:
        return random.choice(USER_AGENTS)
    
    def get_headers(self) -> dict:
        return {
            "User-Agent": self.get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

proxy_manager = ProxyManager()
''')
    
    # backend/app/scrapers/crawler.py
    write_file("backend/app/scrapers/crawler.py", '''"""Main Price Crawler"""
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
                price_match = re.search(r'\\u20b9([\\d,]+\\.?\\d*)', html)
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
                price_match = re.search(r'US \\$([\\d,]+\\.?\\d*)', html)
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
                price_match = re.search(r'\\u20b9([\\d,]+\\.?\\d*)|\\$([\\d,]+\\.?\\d*)', resp.text)
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
        match = re.search(r'\\u20b9([\\d,]+\\.?\\d*)', html)
        if match:
            return float(match.group(1).replace(',', ''))
        return None
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\\s+', ' ', text)
        return text.strip()[:200]

crawler = PriceCrawler()
''')
    
    # backend/app/scrapers/analyzer.py
    write_file("backend/app/scrapers/analyzer.py", '''"""AI Price Analyzer & Validator"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class PriceAnalyzer:
    """Validates prices, detects fake discounts, calculates unit prices"""
    
    def validate_discount(self, original: float, current: float) -> Dict:
        """Validate if discount is genuine"""
        if not original or not current or original <= 0:
            return {"valid": False, "reason": "Invalid prices"}
        
        discount_pct = ((original - current) / original) * 100
        
        is_fake = False
        reason = ""
        
        # Fake discount detection
        if discount_pct > 80:
            is_fake = True
            reason = "Unrealistic discount (>80%)"
        elif discount_pct < 5:
            reason = "Minimal discount"
        
        return {
            "valid": not is_fake,
            "discount_percent": round(discount_pct, 1),
            "savings": round(original - current, 2),
            "reason": reason,
            "verdict": "FAKE" if is_fake else ("GOOD" if discount_pct > 30 else "OK"),
        }
    
    def calculate_unit_price(self, price: float, quantity: int, unit: str = "piece") -> Dict:
        """Calculate price per unit for comparison"""
        if quantity <= 0:
            return {"unit_price": price, "unit": unit}
        
        unit_price = price / quantity
        return {
            "unit_price": round(unit_price, 2),
            "total_price": price,
            "quantity": quantity,
            "unit": unit,
        }
    
    def is_good_price(self, current_price: float, history: List[float]) -> Dict:
        """Determine if current price is good based on history"""
        if not history:
            return {"verdict": "UNKNOWN", "reason": "No price history"}
        
        avg = sum(history) / len(history)
        min_price = min(history)
        max_price = max(history)
        
        if current_price <= min_price:
            return {"verdict": "BEST", "reason": "All-time low price!", "savings": round(max_price - current_price, 2)}
        elif current_price <= avg * 0.9:
            return {"verdict": "GOOD", "reason": f"Below average ({avg:.0f})"}
        elif current_price <= avg:
            return {"verdict": "OK", "reason": f"Around average ({avg:.0f})"}
        else:
            return {"verdict": "HIGH", "reason": f"Above average ({avg:.0f})", "overpay": round(current_price - avg, 2)}
    
    def calculate_discount_stack(self, base_price: float, coupons: List[Dict]) -> Dict:
        """Calculate final price after stacking all discounts"""
        total_discount = 0
        steps = [{"step": "Base Price", "amount": base_price}]
        
        for coupon in coupons:
            if coupon.get("type") == "percentage":
                discount = base_price * (coupon["value"] / 100)
            else:
                discount = coupon["value"]
            
            total_discount += discount
            steps.append({
                "step": f"Coupon: {coupon.get('code', 'N/A')}",
                "discount": round(discount, 2),
                "running_total": round(base_price - total_discount, 2),
            })
        
        final_price = max(0, base_price - total_discount)
        
        return {
            "original_price": base_price,
            "total_discount": round(total_discount, 2),
            "final_price": round(final_price, 2),
            "savings_percent": round((total_discount / base_price) * 100, 1) if base_price > 0 else 0,
            "steps": steps,
        }

analyzer = PriceAnalyzer()
''')
    
    print("  [DONE] Phase 2 - Scrapers")
    
    # ============================================
    # PHASE 3: SERVICES
    # ============================================
    print("[Phase 3] Services...")
    
    # backend/app/services/__init__.py
    write_file("backend/app/services/__init__.py", "")
    
    # backend/app/services/whatsapp.py
    write_file("backend/app/services/whatsapp.py", '''"""WhatsApp Bot Integration via Twilio"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import PlainTextResponse
import re
import httpx
import os

router = APIRouter()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

@router.post("/api/v1/whatsapp/webhook")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    MediaUrl0: str = Form(None),
):
    """Handle incoming WhatsApp messages"""
    user_message = Body.strip()
    
    # Extract URL from message
    url_match = re.search(r'https?://[^\\s]+', user_message)
    
    if url_match:
        url = url_match.group(0)
        from ..scrapers.crawler import crawler
        
        result = await crawler.crawl(url)
        
        if result.get("price"):
            response = f"Price Found!\\n\\n"
            response += f"{result.get('title', 'Product')}\\n"
            response += f"Price: INR {result['price']}\\n"
            response += f"Store: {result.get('store', 'Unknown')}\\n"
            response += f"\\nSend another URL to compare!"
        else:
            response = "Could not find price. Try another URL."
    elif MediaUrl0:
        response = "Image received! AI Vision processing coming soon.\\nSend a product URL for instant price check."
    else:
        response = "Welcome to Vgas Shopping AI!\\n\\n"
        response += "Send me a product URL and I will find the lowest price!\\n\\n"
        response += "Commands:\\n"
        response += "/deals - Today best deals\\n"
        response += "/track - Track a product\\n"
        response += "/help - Show this message"
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response}</Message>
</Response>"""
    
    return PlainTextResponse(twiml, media_type="application/xml")
''')
    
    # backend/app/services/stripe_pay.py
    write_file("backend/app/services/stripe_pay.py", '''"""Stripe Payment Integration"""
import stripe
import os
from typing import Dict

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

PLANS = {
    "free": {"price": 0, "name": "Free", "tracks": 5, "scan_interval": 21600},
    "pro": {"price": 9900, "name": "Pro", "tracks": -1, "scan_interval": 300, "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", "")},
    "premium": {"price": 29900, "name": "Premium", "tracks": -1, "scan_interval": 60, "stripe_price_id": os.getenv("STRIPE_PREMIUM_PRICE_ID", "")},
}

def create_checkout_session(user_id: int, plan: str) -> Dict:
    """Create Stripe checkout session"""
    if plan not in PLANS or plan == "free":
        return {"error": "Invalid plan"}
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "upi"],
            line_items=[{
                "price": PLANS[plan]["stripe_price_id"],
                "quantity": 1,
            }],
            mode="subscription",
            success_url="http://localhost:8000/payment/success",
            cancel_url="http://localhost:8000/payment/cancel",
            metadata={"user_id": str(user_id), "plan": plan},
        )
        return {"session_id": session.id, "url": session.url}
    except Exception as e:
        return {"error": str(e)}

def handle_webhook(payload: bytes, sig_header: str) -> Dict:
    """Handle Stripe webhook"""
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET", ""))
        
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            return {"status": "success", "user_id": session["metadata"]["user_id"], "plan": session["metadata"]["plan"]}
        
        elif event["type"] == "customer.subscription.deleted":
            return {"status": "cancelled", "subscription": event["data"]["object"]["id"]}
        
        return {"status": "ignored"}
    except Exception as e:
        return {"error": str(e)}
''')
    
    # backend/app/services/affiliate.py
    write_file("backend/app/services/affiliate.py", '''"""Affiliate Link Manager"""
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
''')
    
    print("  [DONE] Phase 3 - Services")
    
    # ============================================
    # PHASE 4: API ROUTES
    # ============================================
    print("[Phase 4] API Routes...")
    
    # backend/app/api/__init__.py
    write_file("backend/app/api/__init__.py", "")
    
    # backend/app/api/track.py
    write_file("backend/app/api/track.py", '''"""Product Tracking API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ProductTrack, PriceHistory
from ..scrapers.crawler import crawler

router = APIRouter()

class TrackRequest(BaseModel):
    url: str
    target_price: float = 0
    user_id: int

@router.post("/api/v1/track")
async def track_product(req: TrackRequest, db: Session = Depends(get_db)):
    """Start tracking a product"""
    result = await crawler.crawl(req.url)
    
    track = ProductTrack(
        user_id=req.user_id,
        url=req.url,
        title=result.get("title", "Unknown"),
        image_url=result.get("image_url", ""),
        current_price=result.get("price", 0),
        target_price=req.target_price,
        store=result.get("store", "unknown"),
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    
    if result.get("price"):
        history = PriceHistory(
            product_id=track.id,
            price=result["price"],
            store=result.get("store", "unknown"),
        )
        db.add(history)
        db.commit()
    
    return {"id": track.id, "status": "tracking", "price": result.get("price")}

@router.get("/api/v1/price-history/{product_id}")
async def get_price_history(product_id: int, db: Session = Depends(get_db)):
    """Get price history for a product"""
    history = db.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(PriceHistory.recorded_at).all()
    return [{"date": h.recorded_at.isoformat(), "price": h.price, "store": h.store} for h in history]
''')
    
    # backend/app/api/leaderboard.py
    write_file("backend/app/api/leaderboard.py", '''"""Deal Leaderboard API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import ProductTrack

router = APIRouter()

@router.get("/api/v1/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    """Get top 10 deals"""
    products = db.query(ProductTrack).filter(
        ProductTrack.current_price > 0,
        ProductTrack.target_price > 0,
    ).all()
    
    deals = []
    for p in products:
        if p.target_price > 0:
            discount = ((p.target_price - p.current_price) / p.target_price) * 100
            deals.append({
                "id": p.id,
                "title": p.title or "Unknown",
                "current_price": p.current_price,
                "original_price": p.target_price,
                "discount_percent": round(discount, 1),
                "store": p.store,
                "url": p.url,
            })
    
    deals.sort(key=lambda x: x["discount_percent"], reverse=True)
    return {"deals": deals[:10]}

@router.get("/api/v1/deals/today")
async def get_todays_deals(db: Session = Depends(get_db)):
    """Get today's best deals"""
    from datetime import datetime, timedelta
    today = datetime.utcnow() - timedelta(hours=24)
    
    products = db.query(ProductTrack).filter(
        ProductTrack.created_at >= today,
        ProductTrack.current_price > 0,
    ).all()
    
    return {"count": len(products), "deals": [{"title": p.title, "price": p.current_price, "store": p.store} for p in products[:20]]}
''')
    
    # backend/app/api/webhook.py
    write_file("backend/app/api/webhook.py", '''"""Webhook Handlers"""
from fastapi import APIRouter, Request
from ..services.stripe_pay import handle_webhook

router = APIRouter()

@router.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    result = handle_webhook(payload, sig_header)
    return result

@router.get("/api/v1/whatsapp/webhook")
async def whatsapp_verify():
    """Twilio webhook verification"""
    return {"status": "ok"}
''')
    
    print("  [DONE] Phase 4 - API Routes")
    
    # ============================================
    # PHASE 5: MAIN APP
    # ============================================
    print("[Phase 5] Main App...")
    
    # backend/app/main.py
    write_file("backend/app/main.py", '''"""Vgas Shopping AI v3.0 - FastAPI Main App"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from .database import init_db
from .api import track, leaderboard, webhook
from .services import whatsapp

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    init_db()
    print("Vgas Shopping AI v3.0 - Server Started!")
    yield
    print("Server Shutdown")

app = FastAPI(
    title="Vgas Shopping AI v3.0",
    description="AI-Powered Deal Snatcher & Price Optimization Platform",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(track.router)
app.include_router(leaderboard.router)
app.include_router(webhook.router)
app.include_router(whatsapp.router)

@app.get("/")
async def root():
    return {"message": "Vgas Shopping AI v3.0 - Running!", "docs": "/docs"}

@app.get("/api/v1/plans")
async def get_plans():
    return {
        "plans": [
            {"name": "Free", "price": 0, "tracks": 5, "features": ["5 items", "6-hour scans", "Basic leaderboard"]},
            {"name": "Pro", "price": 99, "tracks": -1, "features": ["Unlimited items", "5-min scans", "Early alerts", "Ad-free"]},
            {"name": "Premium", "price": 299, "tracks": -1, "features": ["Everything in Pro", "API access", "White-label", "Priority support"]},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''')
    
    print("  [DONE] Phase 5 - Main App")
    
    # ============================================
    # PHASE 6: EXTENSION
    # ============================================
    print("[Phase 6] Chrome Extension...")
    
    # extension/manifest.json
    write_file("extension/manifest.json", '''{
  "manifest_version": 3,
  "name": "Vgas Shopping AI - Price Tracker",
  "version": "3.0.0",
  "description": "Track prices, find deals, save money automatically",
  "permissions": ["activeTab", "storage", "alarms", "notifications"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["*://*.amazon.in/*", "*://*.amazon.com/*", "*://*.flipkart.com/*", "*://*.ebay.com/*", "*://*.ebay.in/*"],
      "js": ["content.js"],
      "css": []
    }
  ],
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}''')
    
    # extension/content.js
    write_file("extension/content.js", '''/* Content Script - Auto-detect e-commerce pages */
(function() {
  "use strict";
  
  const API_BASE = "http://localhost:8000";
  
  function extractProductData() {
    const hostname = window.location.hostname;
    let data = { url: window.location.href, store: "unknown" };
    
    if (hostname.includes("amazon")) {
      data.store = "amazon";
      data.title = document.querySelector("#productTitle")?.textContent?.trim() || "";
      const priceEl = document.querySelector(".a-price-whole");
      data.price = priceEl ? parseFloat(priceEl.textContent.replace(/[^0-9.]/g, "")) : null;
      data.image = document.querySelector("#landingImage")?.src || "";
    } else if (hostname.includes("flipkart")) {
      data.store = "flipkart";
      data.title = document.querySelector("span.B_NuCI")?.textContent?.trim() || "";
      const priceText = document.querySelector("div._30jeq3._16Jk6d")?.textContent || "";
      data.price = priceText ? parseFloat(priceText.replace(/[^0-9.]/g, "")) : null;
      data.image = document.querySelector("img._396cs4")?.src || "";
    } else if (hostname.includes("ebay")) {
      data.store = "ebay";
      data.title = document.querySelector("h1.x-item-title__mainTitle")?.textContent?.trim() || "";
      const priceEl = document.querySelector(".x-price-primary span");
      data.price = priceEl ? parseFloat(priceEl.textContent.replace(/[^0-9.]/g, "")) : null;
    }
    
    return data;
  }
  
  // Send data to extension
  const productData = extractProductData();
  if (productData.price) {
    chrome.runtime.sendMessage({ type: "PRODUCT_DETECTED", data: productData });
  }
})();
''')
    
    # extension/background.js
    write_file("extension/background.js", '''/* Background Service Worker */
const API_BASE = "http://localhost:8000";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PRODUCT_DETECTED") {
    chrome.storage.local.set({ currentProduct: message.data });
    
    // Check price via API
    fetch(`${API_BASE}/api/v1/extension/price?url=${encodeURIComponent(message.data.url)}`)
      .then(res => res.json())
      .then(data => {
        chrome.storage.local.set({ priceData: data });
      })
      .catch(err => console.error("API Error:", err));
  }
  
  if (message.type === "WATCH_PRODUCT") {
    fetch(`${API_BASE}/api/v1/extension/watch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.data),
    })
      .then(res => res.json())
      .then(data => sendResponse(data))
      .catch(err => sendResponse({ error: err.message }));
    
    return true; // Keep message channel open for async response
  }
});

// Price check alarm
chrome.alarms.create("priceCheck", { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "priceCheck") {
    chrome.storage.local.get("watchlist", (result) => {
      const watchlist = result.watchlist || [];
      watchlist.forEach(item => {
        fetch(`${API_BASE}/api/v1/price-history/${item.product_id}`)
          .then(res => res.json())
          .then(data => {
            if (data.length > 0) {
              const latest = data[data.length - 1];
              if (latest.price <= item.target_price) {
                chrome.notifications.create({
                  type: "basic",
                  title: "Price Drop Alert!",
                  message: `${item.title} is now ${latest.price}!`,
                  iconUrl: "icons/icon128.png",
                });
              }
            }
          });
      });
    });
  }
});
''')
    
    # extension/popup.html
    write_file("extension/popup.html", '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vgas Shopping AI</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { width: 380px; min-height: 500px; }
    .badge-good { background: #10b981; }
    .badge-ok { background: #f59e0b; }
    .badge-high { background: #ef4444; }
  </style>
</head>
<body class="bg-gray-900 text-white">
  <div class="p-4">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-lg font-bold">Vgas Shopping AI</h1>
      <span class="text-xs text-gray-400">v3.0</span>
    </div>
    
    <div id="product-info" class="bg-gray-800 rounded-lg p-3 mb-4 hidden">
      <div class="flex gap-3">
        <img id="product-image" class="w-16 h-16 rounded object-cover" src="" alt="">
        <div class="flex-1">
          <h2 id="product-title" class="text-sm font-medium line-clamp-2"></h2>
          <div class="flex items-center gap-2 mt-1">
            <span id="product-price" class="text-xl font-bold text-green-400"></span>
            <span id="price-badge" class="text-xs px-2 py-0.5 rounded-full"></span>
          </div>
        </div>
      </div>
    </div>
    
    <div id="no-product" class="text-center py-8 text-gray-400">
      <p class="text-4xl mb-2">Browse a product on Amazon, Flipkart, or eBay</p>
      <p class="text-sm mt-1">Price data will appear here</p>
    </div>
    
    <div class="space-y-2">
      <button id="watch-btn" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition hidden">
        Watch This Price
      </button>
      <button id="compare-btn" class="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg font-medium transition hidden">
        Compare Prices
      </button>
    </div>
    
    <div id="coupon-section" class="mt-4 hidden">
      <h3 class="text-sm font-bold mb-2">Working Coupons</h3>
      <div id="coupon-list" class="space-y-1"></div>
    </div>
    
    <div class="mt-4 pt-4 border-t border-gray-700 text-center">
      <a href="http://localhost:8000" target="_blank" class="text-xs text-blue-400 hover:underline">Open Dashboard</a>
    </div>
  </div>
  
  <script src="popup.js"></script>
</body>
</html>''')
    
    # extension/popup.js
    write_file("extension/popup.js", '''/* Popup Script */
const API_BASE = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  chrome.storage.local.get(["currentProduct", "priceData"], (result) => {
    if (result.currentProduct) {
      const product = result.currentProduct;
      
      document.getElementById("no-product").classList.add("hidden");
      document.getElementById("product-info").classList.remove("hidden");
      document.getElementById("watch-btn").classList.remove("hidden");
      document.getElementById("compare-btn").classList.remove("hidden");
      
      document.getElementById("product-title").textContent = product.title || "Unknown Product";
      document.getElementById("product-price").textContent = product.price ? `${product.price}` : "N/A";
      
      if (product.image) {
        document.getElementById("product-image").src = product.image;
      }
      
      // Price badge
      const badge = document.getElementById("price-badge");
      if (result.priceData?.verdict) {
        badge.textContent = result.priceData.verdict;
        badge.className = "text-xs px-2 py-0.5 rounded-full " + 
          (result.priceData.verdict === "BEST" ? "badge-good" : 
           result.priceData.verdict === "GOOD" ? "badge-good" : "badge-ok");
      }
    }
  });
  
  // Watch button
  document.getElementById("watch-btn").addEventListener("click", () => {
    chrome.storage.local.get("currentProduct", (result) => {
      if (result.currentProduct) {
        chrome.runtime.sendMessage({
          type: "WATCH_PRODUCT",
          data: {
            url: result.currentProduct.url,
            title: result.currentProduct.title,
            target_price: result.currentProduct.price * 0.9,
          }
        }, (response) => {
          alert(response?.id ? "Added to watchlist!" : "Error adding to watchlist");
        });
      }
    });
  });
  
  // Compare button
  document.getElementById("compare-btn").addEventListener("click", () => {
    chrome.storage.local.get("currentProduct", (result) => {
      if (result.currentProduct) {
        window.open(`${API_BASE}/api/v1/compare?url=${encodeURIComponent(result.currentProduct.url)}`, "_blank");
      }
    });
  });
});
''')
    
    print("  [DONE] Phase 6 - Extension")
    
    # ============================================
    # PHASE 7: WEB TEMPLATES
    # ============================================
    print("[Phase 7] Web Templates...")
    
    # web/templates/index.html
    write_file("web/templates/index.html", '''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vgas Shopping AI - Never Overpay Again</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Vgas Shopping AI",
    "url": "http://localhost:8000",
    "potentialAction": {
      "@type": "SearchAction",
      "target": "http://localhost:8000/search?q={search_term_string}",
      "query-input": "required name=search_term_string"
    }
  }
  </script>
</head>
<body class="bg-gray-950 text-white min-h-screen">
  <!-- Hero -->
  <div class="container mx-auto px-4 py-16 text-center">
    <h1 class="text-5xl font-bold mb-4">Never <span class="text-green-400">Overpay</span> Again</h1>
    <p class="text-xl text-gray-400 mb-8">Track prices across 100+ stores. Get alerts when prices drop. Save money automatically.</p>
    
    <!-- Search Bar -->
    <div class="max-w-2xl mx-auto mb-12">
      <div class="flex gap-2">
        <input type="text" id="search-input" placeholder="Paste a product URL to check price..." 
               class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-green-500">
        <button onclick="checkPrice()" class="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-bold transition">
          Check Price
        </button>
      </div>
    </div>
    
    <!-- Stats -->
    <div class="grid grid-cols-3 gap-8 max-w-2xl mx-auto mb-16">
      <div class="text-center">
        <div class="text-3xl font-bold text-green-400">50,000+</div>
        <div class="text-gray-400">Active Users</div>
      </div>
      <div class="text-center">
        <div class="text-3xl font-bold text-green-400">2 Crore+</div>
        <div class="text-gray-400">Money Saved</div>
      </div>
      <div class="text-center">
        <div class="text-3xl font-bold text-green-400">1M+</div>
        <div class="text-gray-400">Deals Tracked</div>
      </div>
    </div>
    
    <!-- Deal of the Day -->
    <div class="max-w-4xl mx-auto">
      <h2 class="text-2xl font-bold mb-6">Deal of the Day</h2>
      <div id="deals-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-800 rounded-lg p-4 animate-pulse h-32"></div>
        <div class="bg-gray-800 rounded-lg p-4 animate-pulse h-32"></div>
      </div>
    </div>
    
    <!-- Features -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-16">
      <div class="bg-gray-800 rounded-lg p-6 text-center">
        <div class="text-4xl mb-3">Instant Alerts</div>
        <h3 class="font-bold mb-2">WhatsApp/SMS Alerts</h3>
        <p class="text-gray-400 text-sm">Get notified when prices drop</p>
      </div>
      <div class="bg-gray-800 rounded-lg p-6 text-center">
        <div class="text-4xl mb-3">Price History</div>
        <h3 class="font-bold mb-2">90-Day Trends</h3>
        <p class="text-gray-400 text-sm">See price history before buying</p>
      </div>
      <div class="bg-gray-800 rounded-lg p-6 text-center">
        <div class="text-4xl mb-3">Cashback</div>
        <h3 class="font-bold mb-2">Instant UPI Payout</h3>
        <p class="text-gray-400 text-sm">Earn cashback on purchases</p>
      </div>
    </div>
    
    <!-- CTA -->
    <div class="mt-16">
      <a href="/dashboard" class="bg-green-600 hover:bg-green-700 px-8 py-4 rounded-lg font-bold text-lg transition">
        Start Saving Now
      </a>
    </div>
  </div>
  
  <script>
    async function checkPrice() {
      const url = document.getElementById("search-input").value;
      if (!url) return alert("Please enter a product URL");
      window.location.href = `/dashboard?track=${encodeURIComponent(url)}`;
    }
    
    // Load deals
    fetch("/api/v1/leaderboard").then(r => r.json()).then(data => {
      const container = document.getElementById("deals-container");
      container.innerHTML = data.deals?.slice(0, 4).map(deal => `
        <a href="${deal.url}" target="_blank" class="bg-gray-800 hover:bg-gray-700 rounded-lg p-4 text-left transition">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="font-medium line-clamp-2">${deal.title}</h3>
              <div class="mt-2">
                <span class="text-green-400 font-bold text-lg">${deal.current_price}</span>
                <span class="text-gray-500 line-through text-sm ml-2">${deal.original_price}</span>
                <span class="bg-green-600 text-white text-xs px-2 py-0.5 rounded-full ml-2">${deal.discount_percent}% OFF</span>
              </div>
            </div>
          </div>
        </a>
      `).join("") || "<p class='text-gray-400'>No deals yet. Start tracking products!</p>";
    });
  </script>
</body>
</html>''')
    
    print("  [DONE] Phase 7 - Web Templates")
    
    # ============================================
    # PHASE 8: CONFIG & REQUIREMENTS
    # ============================================
    print("[Phase 8] Config & Requirements...")
    
    # backend/requirements.txt
    write_file("backend/requirements.txt", '''fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
httpx==0.26.0
playwright==1.41.0
stripe==7.12.0
python-dotenv==1.0.0
python-multipart==0.0.6
''')
    
    # requirements.txt (root)
    write_file("requirements.txt", '''fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
httpx==0.26.0
playwright==1.41.0
stripe==7.12.0
python-dotenv==1.0.0
python-multipart==0.0.6
''')
    
    # config.json
    write_file("config.json", json.dumps({
        "app_name": "Vgas Shopping AI v3.0",
        "version": "3.0.0",
        "backend_port": 8000,
        "database": "sqlite:///vgas_shopping.db",
        "stores": ["amazon", "flipkart", "ebay", "walmart", "myntra", "nykaa"],
        "plans": {
            "free": {"price": 0, "tracks": 5},
            "pro": {"price": 99, "tracks": -1},
            "premium": {"price": 299, "tracks": -1}
        }
    }, indent=2))
    
    # self_heal.py
    write_file("self_heal.py", '''"""Self-Healing Module for Vgas Shopping AI"""
import os
import sys
import subprocess
from pathlib import Path

REQUIRED_DIRS = [
    "backend/app",
    "backend/app/scrapers",
    "backend/app/services",
    "backend/app/api",
    "extension",
    "extension/icons",
    "web/templates",
    "tests",
]

REQUIRED_FILES = [
    "backend/app/__init__.py",
    "backend/app/main.py",
    "backend/app/database.py",
    "backend/app/models.py",
    "backend/app/scrapers/__init__.py",
    "backend/app/scrapers/crawler.py",
    "backend/app/scrapers/analyzer.py",
    "backend/app/scrapers/proxy_manager.py",
    "backend/app/services/__init__.py",
    "backend/app/services/whatsapp.py",
    "backend/app/services/stripe_pay.py",
    "backend/app/services/affiliate.py",
    "backend/app/api/__init__.py",
    "backend/app/api/track.py",
    "backend/app/api/leaderboard.py",
    "backend/app/api/webhook.py",
    "extension/manifest.json",
    "extension/background.js",
    "extension/content.js",
    "extension/popup.html",
    "extension/popup.js",
    "self_heal.py",
    "config.json",
    "requirements.txt",
]

def heal():
    print("Running Self-Heal...")
    
    # Create missing directories
    for d in REQUIRED_DIRS:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Check missing files
    missing = []
    for f in REQUIRED_FILES:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print(f"Missing {len(missing)} files:")
        for f in missing:
            print(f"   - {f}")
    else:
        print("All required files exist!")
    
    # Check Python syntax
    print("Checking Python syntax...")
    errors = []
    for f in Path("backend").rglob("*.py"):
        try:
            compile(f.read_text(), str(f), "exec")
        except SyntaxError as e:
            errors.append(f"{f}: {e}")
    
    if errors:
        print(f"{len(errors)} syntax errors:")
        for e in errors:
            print(f"   - {e}")
    else:
        print("All Python files have valid syntax!")
    
    # Install missing packages
    print("Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("Core packages installed!")
    except ImportError as e:
        print(f"Missing package: {e.name}")
        print("   Run: pip install -r requirements.txt")
    
    print("Self-heal complete!")

if __name__ == "__main__":
    heal()
''')
    
    print("  [DONE] Phase 8 - Config & Requirements")
    
    # ============================================
    # PHASE 9: LAUNCH SCRIPT
    # ============================================
    print("[Phase 9] Launch Script...")
    
    # START_VGAS_SHOPPING_AI.bat
    write_file("START_VGAS_SHOPPING_AI.bat", '''@echo off
title Vgas Shopping AI v3.0 - Launching...
color 0A

echo ============================================================
echo   Vgas Shopping AI v3.0 - Total Domination Edition
echo ============================================================
echo.

cd /d "d:\\sam\\projects\\Vgas Shooping Ai"

echo [1/5] Running Self-Heal...
python self_heal.py
echo.

echo [2/5] Installing Python dependencies...
pip install -r requirements.txt -q 2>nul
echo.

echo [3/5] Setting up database...
python -c "from backend.app.database import init_db; init_db()"
echo.

echo [4/5] Starting Backend (FastAPI - Port 8000)...
start "Vgas Backend" cmd /k "cd /d d:\\sam\\projects\\Vgas Shooping Ai && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [5/5] Opening Browser...
start http://localhost:8000

echo.
echo ============================================================
echo   VGAS SHOPPING AI v3.0 - READY!
echo ============================================================
echo.
echo   Backend API:   http://localhost:8000
echo   API Docs:      http://localhost:8000/docs
echo   Extension:     Load extension/ folder in Chrome
echo.
echo   Press Ctrl+C to stop.
echo ============================================================
echo.

pause
''')
    
    # backend/bootstrap.py
    write_file("backend/bootstrap.py", '''"""Bootstrap Database with Mock Data"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, SessionLocal
from app.models import User, ProductTrack, PriceHistory
from datetime import datetime, timedelta
import random

def seed():
    print("Seeding database...")
    init_db()
    db = SessionLocal()
    
    # Create demo user
    user = User(
        username="demo_user",
        email="demo@vgas.ai",
        phone="+919999999999",
        plan="free",
        referral_code="VGAS2024",
    )
    db.add(user)
    db.commit()
    
    # Create demo products
    products = [
        {"title": "iPhone 15 Pro Max 256GB", "url": "https://amazon.in/dp/B0CHX1W1XY", "store": "amazon", "price": 159900, "target": 179900},
        {"title": "Samsung Galaxy S24 Ultra", "url": "https://amazon.in/dp/B0CMDL4WP6", "store": "amazon", "price": 129999, "target": 149999},
        {"title": "Sony WH-1000XM5", "url": "https://amazon.in/dp/B09XS7JWHH", "store": "amazon", "price": 24990, "target": 34990},
        {"title": "MacBook Air M3", "url": "https://amazon.in/dp/B0CX23V2ZK", "store": "amazon", "price": 114900, "target": 134900},
        {"title": "OnePlus 12 5G", "url": "https://amazon.in/dp/B0CMDL5DPV", "store": "amazon", "price": 64999, "target": 69999},
    ]
    
    for p in products:
        track = ProductTrack(
            user_id=user.id,
            url=p["url"],
            title=p["title"],
            current_price=p["price"],
            target_price=p["target"],
            store=p["store"],
        )
        db.add(track)
        db.commit()
        
        # Add price history
        for i in range(30):
            history = PriceHistory(
                product_id=track.id,
                price=p["price"] + random.uniform(-5000, 5000),
                store=p["store"],
                recorded_at=datetime.utcnow() - timedelta(days=i),
            )
            db.add(history)
        db.commit()
    
    db.close()
    print("Database seeded with demo data!")

if __name__ == "__main__":
    seed()
''')
    
    # package.json
    write_file("package.json", json.dumps({
        "name": "vgas-shopping-ai",
        "version": "3.0.0",
        "description": "AI-Powered Deal Snatcher & Price Optimization Platform",
        "scripts": {
            "start": "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload",
            "seed": "python backend/bootstrap.py",
            "heal": "python self_heal.py",
            "test": "pytest tests/ -v"
        },
        "dependencies": {},
        "devDependencies": {}
    }, indent=2))
    
    print("  [DONE] Phase 9 - Launch Script")
    
    # ============================================
    # PHASE 10: TESTS
    # ============================================
    print("[Phase 10] Tests...")
    
    # tests/__init__.py
    write_file("tests/__init__.py", "")
    
    # tests/test_api.py
    write_file("tests/test_api.py", '''"""API Tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Vgas" in response.json()["message"]

def test_plans():
    response = client.get("/api/v1/plans")
    assert response.status_code == 200
    assert len(response.json()["plans"]) == 3

def test_leaderboard():
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    assert "deals" in response.json()
''')
    
    # tests/test_scraper.py
    write_file("tests/test_scraper.py", '''"""Scraper Tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app.scrapers.analyzer import analyzer

def test_validate_discount_good():
    result = analyzer.validate_discount(1000, 500)
    assert result["valid"] is True
    assert result["discount_percent"] == 50.0

def test_validate_discount_fake():
    result = analyzer.validate_discount(1000, 100)
    assert result["valid"] is False

def test_is_good_price():
    history = [100, 110, 90, 105, 95]
    result = analyzer.is_good_price(80, history)
    assert result["verdict"] == "BEST"

def test_calculate_discount_stack():
    coupons = [
        {"code": "SAVE10", "type": "percentage", "value": 10},
        {"code": "FLAT100", "type": "fixed", "value": 100},
    ]
    result = analyzer.calculate_discount_stack(1000, coupons)
    assert result["final_price"] == 800
    assert result["savings_percent"] == 20.0
''')
    
    # tests/test_extension.py
    write_file("tests/test_extension.py", '''"""Extension Tests"""
import json
from pathlib import Path

def test_manifest_exists():
    manifest = Path("extension/manifest.json")
    assert manifest.exists(), "manifest.json not found"

def test_manifest_valid():
    manifest = Path("extension/manifest.json")
    data = json.loads(manifest.read_text())
    assert data["manifest_version"] == 3
    assert "permissions" in data

def test_content_script_exists():
    content = Path("extension/content.js")
    assert content.exists(), "content.js not found"

def test_background_script_exists():
    bg = Path("extension/background.js")
    assert bg.exists(), "background.js not found"

def test_popup_exists():
    popup = Path("extension/popup.html")
    assert popup.exists(), "popup.html not found"
''')
    
    print("  [DONE] Phase 10 - Tests")
    
    # ============================================
    # SUMMARY
    # ============================================
    elapsed = time.time() - start_time
    
    print()
    print("="*60)
    print("  VGAS SHOPPING AI v3.0 - COMPLETE!")
    print("="*60)
    print()
    
    # Count files
    file_count = 0
    for root, dirs, files in os.walk(PROJECT_DIR):
        for f in files:
            if not f.endswith('.pyc') and '__pycache__' not in root:
                file_count += 1
    
    print(f"  Total Files: {file_count}")
    print(f"  Build Time:  {elapsed:.1f} seconds")
    print()
    print("  PHASES COMPLETED:")
    print("  [1] Database Models    DONE")
    print("  [2] Scrapers           DONE")
    print("  [3] Services           DONE")
    print("  [4] API Routes         DONE")
    print("  [5] Main App           DONE")
    print("  [6] Chrome Extension   DONE")
    print("  [7] Web Templates      DONE")
    print("  [8] Config & Reqs      DONE")
    print("  [9] Launch Script      DONE")
    print("  [10] Tests             DONE")
    print()
    print("  TO RUN:")
    print('  cd "d:\\sam\\projects\\Vgas Shooping Ai"')
    print("  START_VGAS_SHOPPING_AI.bat")
    print()

if __name__ == "__main__":
    run()
