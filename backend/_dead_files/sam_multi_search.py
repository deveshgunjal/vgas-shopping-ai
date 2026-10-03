# -*- coding: utf-8 -*-
"""SAM MULTI-PLATFORM SEARCH - Find Cheapest Deals"""
import asyncio, sys, re, json
sys.stdout.reconfigure(encoding="utf-8")

async def main():
    from scrapling import AsyncFetcher
    
    products = [
        "iPhone 16",
        "Samsung Galaxy S24",
        "TV 55 inch",
        "Laptop 15 inch",
        "Headphones"
    ]
    
    platforms = {
        "Amazon.in": "https://www.amazon.in/s?k={q}&sort=price-asc",
        "Flipkart": "https://www.flipkart.com/search?q={q}&sort=price_asc",
        "Meesho": "https://www.meesho.com/search?q={q}",
        "Myntra": "https://www.myntra.com/{q}"
    }
    
    print("🔍 SAM MULTI-PLATFORM SEARCH - Cheapest Deals")
    print("=" * 60)
    
    for product in products[:3]:  # First 3 products
        print(f"\n📦 Product: {product}")
        print("-" * 40)
        
        for platform, url_template in platforms.items():
            try:
                url = url_template.format(q=product.replace(" ", "+"))
                fetcher = AsyncFetcher()
                r = await fetcher.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    print(f"  ✅ {platform}: Found (Status: {r.status_code})")
            except Exception as e:
                print(f"  ⚠️  {platform}: Error")

asyncio.run(main())
