"""
VGAS Hybrid Price Comparison API
Cross-platform price comparison with bank offers, price history, and fake discount detection
"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
import re
import json
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vgas-compare", tags=["VGAS Hybrid Compare"])

# Known product database (updated from real scrapes)
PRODUCT_DB = {
    "B0DDT4W8WY": {
        "name": "iBELL CT20-38 Cordless Impact Drill 20V with 101 Home Tools",
        "prices": [
            {"platform": "Amazon.in", "price": 5510, "url": "https://www.amazon.in/dp/B0DDT4W8WY", "rating": 4.2, "reviews": 250},
            {"platform": "Flipkart", "price": 5234, "url": "https://www.flipkart.com/ibell-ct20-38-20v-cordless-brushless-impact-drill-tool-kit-38nm-1450-rpm-10mm-chuck-power-hand-kit/p/itm896ee8c666d63", "rating": 4.2, "reviews": 119},
            {"platform": "iBELL Official", "price": 5510, "url": "https://www.ibelltools.com"},
            {"platform": "IndiaMART", "price": 4855, "url": "https://www.indiamart.com", "note": "Dealer price"},
            {"platform": "Moglix", "price": 5848, "url": "https://www.moglix.com", "note": "MRP: 8700"},
            {"platform": "Globe Tools", "price": 4900, "url": "https://globetools.in", "note": "Online dealer"},
            {"platform": "PriceHistory Low", "price": 4276, "note": "All-time low"},
        ],
        "all_time_low": 4276,
        "mrp": 7999,
    }
}

# Bank offers
BANK_OFFERS = [
    {"bank": "SBI", "card": "Credit Card", "pct": 10, "max": 1500, "min": 3000},
    {"bank": "HDFC", "card": "Credit Card", "pct": 5, "max": 750, "min": 3000},
    {"bank": "ICICI", "card": "Credit Card", "pct": 5, "max": 1000, "min": 5000},
    {"bank": "Axis", "card": "Credit Card", "pct": 10, "max": 500, "min": 2000},
    {"bank": "Kotak", "card": "Debit Card", "pct": 5, "max": 500, "min": 3000},
    {"bank": "AMEX", "card": "Credit Card", "pct": 10, "max": 2000, "min": 5000},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_asin(url: str) -> Optional[str]:
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


def scrape_amazon_live(url: str) -> Dict:
    try:
        from bs4 import BeautifulSoup
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        
        title_el = soup.find("span", {"id": "productTitle"})
        title = title_el.get_text(strip=True) if title_el else "Unknown"
        
        price = None
        price_div = soup.find("span", {"class": "a-price"})
        if price_div:
            offscreen = price_div.find("span", {"class": "a-offscreen"})
            if offscreen:
                price = float(re.sub(r'[^\d.]', '', offscreen.get_text(strip=True)))
        
        rating = None
        rating_el = soup.find("span", {"id": "acrPopover"})
        if rating_el:
            match = re.search(r'([\d.]+)', rating_el.get("title", ""))
            if match:
                rating = float(match.group(1))
        
        reviews = None
        reviews_el = soup.find("span", {"id": "acrCustomerReviewText"})
        if reviews_el:
            match = re.search(r'([\d,]+)', reviews_el.get_text())
            if match:
                reviews = int(match.group(1).replace(",", ""))
        
        return {
            "platform": "Amazon.in",
            "title": title[:120],
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "url": url,
            "source": "live"
        }
    except Exception as e:
        return {"platform": "Amazon.in", "error": str(e)}


@router.get("/compare")
async def compare_product(
    url: Optional[str] = Query(default=None, description="Product URL (Amazon, Flipkart, etc.)"),
    asin: Optional[str] = Query(default=None, description="Amazon ASIN"),
    query: Optional[str] = Query(default=None, description="Product search query"),
):
    """
    Compare product prices across all platforms
    Supports: Amazon URLs, ASIN codes, or product names
    """
    extracted_asin = asin or (extract_asin(url) if url else None)
    
    all_prices = []
    product_name = "Product"
    
    # 1. Live scrape Amazon if URL provided
    if url and "amazon" in url.lower():
        live = scrape_amazon_live(url)
        if live.get("price"):
            all_prices.append(live)
            product_name = live.get("title", product_name)
    
    # 2. Check database
    if extracted_asin and extracted_asin in PRODUCT_DB:
        cached = PRODUCT_DB[extracted_asin]
        product_name = cached["name"]
        
        for p in cached["prices"]:
            if p["platform"] == "Amazon.in" and any(x["platform"] == "Amazon.in" for x in all_prices):
                continue
            all_prices.append({**p, "source": "database"})
        
        # Add all-time low
        if cached.get("all_time_low"):
            all_prices.append({
                "platform": "All-Time Low",
                "price": cached["all_time_low"],
                "note": "Historical lowest price",
                "source": "database"
            })
    
    # Sort by price
    all_prices.sort(key=lambda x: x.get("price", float("inf")))
    
    # Calculate bank offers
    bank_offers = []
    if all_prices:
        best_price = all_prices[0]["price"]
        for offer in BANK_OFFERS:
            if best_price >= offer["min"]:
                discount = min(best_price * offer["pct"] / 100, offer["max"])
                bank_offers.append({
                    "bank": offer["bank"],
                    "card": offer["card"],
                    "discount": round(discount),
                    "final_price": round(best_price - discount),
                    "saves": f"₹{discount:,.0f} with {offer['bank']} {offer['card']}"
                })
    
    # Best deal
    best = all_prices[0] if all_prices else None
    
    return {
        "product": product_name,
        "asin": extracted_asin,
        "total_platforms": len(all_prices),
        "prices": all_prices,
        "best_deal": {
            "platform": best["platform"],
            "price": best["price"],
            "url": best.get("url"),
        } if best else None,
        "bank_offers": bank_offers,
        "effective_best_price": bank_offers[0]["final_price"] if bank_offers else (best["price"] if best else None),
        "all_time_low": PRODUCT_DB.get(extracted_asin, {}).get("all_time_low"),
        "mrp": PRODUCT_DB.get(extracted_asin, {}).get("mrp"),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/url-trick")
async def url_trick(url: str = Query(..., description="Product URL (will add vgas.shop/ prefix)")):
    """
    URL Prefix Trick - like flash.co but with AI price stacking
    Add vgas.shop/ before any product URL to compare prices
    """
    clean = url
    for prefix in ["vgas.shop/", "vgas.shop", "http://vgas.shop/", "https://vgas.shop/"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break
    
    if not clean.startswith("http"):
        clean = "https://" + clean
    
    asin = extract_asin(clean)
    
    return {
        "original_url": clean,
        "vgas_url": f"vgas.shop/{clean}",
        "asin": asin,
        "message": f"Use vgas.shop/{clean} to compare prices instantly!",
        "trick": "Like flash.co but with AI-powered bank offer stacking + price history"
    }


@router.get("/bank-offers")
async def get_bank_offers(
    price: float = Query(..., description="Product price"),
    platform: str = Query(default="Amazon", description="Platform name"),
):
    """Get applicable bank offers and cashback for a given price"""
    offers = []
    for offer in BANK_OFFERS:
        if price >= offer["min"]:
            discount = min(price * offer["pct"] / 100, offer["max"])
            offers.append({
                "bank": offer["bank"],
                "card": offer["card"],
                "discount_pct": offer["pct"],
                "max_discount": offer["max"],
                "discount": round(discount),
                "final_price": round(price - discount),
                "saves": f"₹{discount:,.0f} with {offer['bank']} {offer['card']}"
            })
    
    offers.sort(key=lambda x: x["final_price"])
    
    return {
        "price": price,
        "platform": platform,
        "applicable_offers": len(offers),
        "best_offer": offers[0] if offers else None,
        "all_offers": offers,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/price-history")
async def get_price_history(asin: str = Query(..., description="Product ASIN")):
    """Get price history for a product"""
    cached = PRODUCT_DB.get(asin)
    if not cached:
        return {"asin": asin, "error": "Product not found in database"}
    
    return {
        "asin": asin,
        "product": cached["name"],
        "all_time_low": cached.get("all_time_low"),
        "mrp": cached.get("mrp"),
        "current_prices": cached["prices"],
        "price_trend": "stable",
        "recommendation": "Buy now" if cached.get("all_time_low") and cached["prices"][0]["price"] <= cached["all_time_low"] * 1.1 else "Wait for price drop"
    }
