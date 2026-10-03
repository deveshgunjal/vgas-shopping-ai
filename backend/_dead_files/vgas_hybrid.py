# -*- coding: utf-8 -*-
"""
VGAS SHOPPING AI - HYBRID PRICE ENGINE v3.0
===========================================
Hybrid approach: Direct scraping + Cached known prices + Bank offers
Works immediately without browser dependency for most products.
"""
import requests
import re
import sys
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Known product prices cache (updated periodically)
PRODUCT_CACHE = {
    "B0DDT4W8WY": {
        "name": "iBELL CT20-38 Cordless Impact Drill 20V with 101 Home Tools",
        "prices": [
            {"platform": "Amazon.in", "price": 5510, "url": "https://www.amazon.in/dp/B0DDT4W8WY", "rating": 4.2, "reviews": 250},
            {"platform": "Flipkart", "price": 5234, "url": "https://www.flipkart.com/ibell-ct20-38-20v-cordless-brushless-impact-drill-tool-kit-38nm-1450-rpm-10mm-chuck-power-hand-kit/p/itm896ee8c666d63", "rating": 4.2, "reviews": 119},
            {"platform": "iBELL Official", "price": 5510, "url": "https://www.ibelltools.com", "rating": 4.2},
            {"platform": "IndiaMART", "price": 4855, "url": "https://www.indiamart.com", "note": "Dealer price"},
            {"platform": "IndiaMART (alt)", "price": 5070, "url": "https://www.indiamart.com", "note": "Dealer price"},
            {"platform": "Moglix", "price": 5848, "url": "https://www.moglix.com", "note": "MRP: 8700"},
            {"platform": "Globe Tools", "price": 4900, "url": "https://globetools.in", "note": "Online dealer"},
            {"platform": "PriceHistory Low", "price": 4276, "note": "All-time low price"},
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

# Coupon codes
COUPONS = [
    {"code": "FLAT500", "platform": "Flipkart", "discount": 500, "min": 3000},
    {"code": "FIRST100", "platform": "Amazon", "discount": 100, "min": 500},
    {"code": "VGAS10", "platform": "All", "discount_pct": 10, "max": 750, "min": 2000},
]


def extract_asin(url: str) -> str:
    """Extract ASIN from Amazon URL"""
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


def scrape_amazon_live(url: str) -> dict:
    """Live scrape Amazon for current price"""
    try:
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
            "source": "live_scrape"
        }
    except Exception as e:
        return {"platform": "Amazon.in", "error": str(e), "source": "live_scrape"}


def compare_product(asin: str = None, url: str = None, product_name: str = None) -> dict:
    """Full product comparison"""
    
    print("=" * 70)
    print("  🛒 VGAS SHOPPING AI - HYBRID PRICE COMPARISON v3.0")
    print("=" * 70)
    
    # Extract ASIN
    if url and not asin:
        asin = extract_asin(url)
    
    # Get cached data
    cached = PRODUCT_CACHE.get(asin, {}) if asin else {}
    
    # Live scrape Amazon
    amazon_live = None
    if url:
        print(f"\n  🔴 LIVE: Scraping Amazon...")
        amazon_live = scrape_amazon_live(url)
        if amazon_live.get("price"):
            print(f"     ✅ Amazon: ₹{amazon_live['price']:,.0f}")
    
    # Merge results
    all_prices = []
    
    # Add live Amazon data
    if amazon_live and amazon_live.get("price"):
        all_prices.append(amazon_live)
    
    # Add cached prices
    if cached:
        for p in cached.get("prices", []):
            # Skip if we already have live data for this platform
            if p["platform"] == "Amazon.in" and amazon_live and amazon_live.get("price"):
                continue
            all_prices.append({**p, "source": "cached"})
    
    # Sort by price
    all_prices.sort(key=lambda x: x.get("price", float("inf")))
    
    # Display
    product_title = (amazon_live or {}).get("title") or cached.get("name") or product_name or "Product"
    
    print(f"\n  📦 Product: {product_title[:70]}")
    print(f"  📊 Total prices: {len(all_prices)}")
    
    if all_prices:
        print("\n  🏆 PRICE COMPARISON (lowest → highest):")
        print("  " + "=" * 65)
        
        for i, p in enumerate(all_prices, 1):
            platform = p.get("platform", "Unknown")
            price = p.get("price", 0)
            marker = " 🥇" if i == 1 else " 🥈" if i == 2 else " 🥉" if i == 3 else "   "
            note = p.get("note", "")
            source = "📡" if p.get("source") == "live_scrape" else "💾"
            
            print(f"  {i:2d}. {source} ₹{price:>8,.0f} | {platform:20s}{marker}")
            if note:
                print(f"      ({note})")
            if p.get("url"):
                print(f"      🔗 {p['url'][:65]}")
            if p.get("rating"):
                print(f"      ⭐ {p['rating']}/5 ({p.get('reviews', 'N/A')} reviews)")
        
        best = all_prices[0]
        worst = all_prices[-1]
        
        print("\n  " + "=" * 65)
        print(f"  🏆 CHEAPEST: ₹{best['price']:,.0f} on {best['platform']}")
        print(f"  💰 MOST EXPENSIVE: ₹{worst['price']:,.0f} on {worst['platform']}")
        
        if worst["price"] > best["price"]:
            savings = worst["price"] - best["price"]
            print(f"  💵 YOU SAVE: ₹{savings:,.0f} by choosing {best['platform']}!")
        
        # All-time low
        if cached.get("all_time_low"):
            atl = cached["all_time_low"]
            if best["price"] > atl:
                print(f"\n  📉 ALL-TIME LOW: ₹{atl:,.0f} (currently ₹{best['price'] - atl:,.0f} higher)")
            else:
                print(f"\n  🔥 CURRENT PRICE = ALL-TIME LOW!")
        
        # Bank offers
        print(f"\n  💳 BANK OFFERS (on ₹{best['price']:,.0f}):")
        print("  " + "-" * 65)
        
        best_final = best["price"]
        best_offer_name = "None"
        
        for offer in BANK_OFFERS:
            if best["price"] >= offer["min"]:
                discount = min(best["price"] * offer["pct"] / 100, offer["max"])
                final = best["price"] - discount
                print(f"  ✅ {offer['bank']:6s} {offer['card']:12s}: ₹{final:>8,.0f} (save ₹{discount:,.0f})")
                if final < best_final:
                    best_final = final
                    best_offer_name = f"{offer['bank']} {offer['card']}"
        
        # Coupons
        print(f"\n  🏷️  COUPON CODES:")
        print("  " + "-" * 65)
        for coupon in COUPONS:
            if coupon.get("platform") == best["platform"] or coupon.get("platform") == "All":
                if coupon.get("discount"):
                    print(f"  ✅ {coupon['code']}: ₹{coupon['discount']} off (min ₹{coupon['min']})")
                elif coupon.get("discount_pct"):
                    disc = min(best["price"] * coupon["discount_pct"] / 100, coupon.get("max", 99999))
                    print(f"  ✅ {coupon['code']}: {coupon['discount_pct']}% off (save ₹{disc:,.0f})")
        
        # Final verdict
        print("\n  " + "=" * 65)
        print(f"  🎯 FINAL VERDICT:")
        print(f"  ─────────────────")
        print(f"  Best Platform:     {best['platform']}")
        print(f"  Listed Price:      ₹{best['price']:,.0f}")
        if best_offer_name != "None":
            print(f"  With Bank Offer:   ₹{best_final:,.0f} ({best_offer_name})")
        print(f"  MRP:               ₹{cached.get('mrp', 'N/A'):,}" if cached.get("mrp") else "")
        print(f"  You Save:          ₹{cached.get('mrp', best['price']) - best['price']:,}" if cached.get("mrp") else "")
        
    print("\n  " + "=" * 65)
    print("  ✅ VGAS Shopping AI - Hybrid Comparison Complete!")
    print("  💡 Tip: Add 'vgas.shop/' before any product URL to compare!")
    print("=" * 70)
    
    return {
        "product": product_title,
        "asin": asin,
        "prices": all_prices,
        "best": all_prices[0] if all_prices else None,
        "bank_offers": [o for o in BANK_OFFERS if all_prices and all_prices[0]["price"] >= o["min"]],
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# URL TRICK HANDLER
# ============================================================
def handle_url_trick(input_url: str):
    """Handle vgas.shop/ prefix - like flash.co but better"""
    clean = input_url
    for prefix in ["vgas.shop/", "vgas.shop"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break
    
    if not clean.startswith("http"):
        clean = "https://" + clean
    
    asin = extract_asin(clean)
    if asin:
        return compare_product(asin=asin, url=clean)
    else:
        return compare_product(url=clean)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    result = compare_product(
        asin="B0DDT4W8WY",
        url="https://www.amazon.in/Professional-CT20-38-Brushless-Essential-Accessories/dp/B0DDT4W8WY/",
        product_name="iBELL CT20-38 Cordless Drill 20V"
    )
