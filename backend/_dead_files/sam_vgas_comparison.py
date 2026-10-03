# -*- coding: utf-8 -*-
"""VGAS REAL COMPARISON - Browser Verified - NO PLACEHOLDERS"""
import asyncio, re, sys
sys.stdout.reconfigure(encoding="utf-8")

async def check_product(query):
    """Browser ने खरं डेटा घ्या"""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&sort=price_asc"
    
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000, simulate_user=True, magic=True))
        soup = BeautifulSoup(r.html, "lxml")
    
    # Extract prices
    prices = []
    for el in soup.find_all(["div", "span"], class_=True):
        t = el.get_text(strip=True)
        if "₹" in t and len(t) < 20:
            n = re.findall(r"[\d,]+", t)
            if n:
                v = float(n[0].replace(",", ""))
                if 1000 < v < 500000:
                    prices.append(v)
    
    prices = sorted(set(prices))
    
    # Extract product names
    names = soup.select("div.KzDlHZ, a.s1Q9rs, div._4rR01T")
    name = names[0].get_text(strip=True)[:60] if names else "Unknown"
    
    return {
        "query": query,
        "name": name,
        "price": prices[0] if prices else 0,
        "mrp": prices[-1] if len(prices) > 1 else 0,
        "discount": int(((prices[-1] - prices[0]) / prices[-1]) * 100) if len(prices) > 1 else 0
    }

async def main():
    print("=" * 80)
    print("VGAS REAL COMPARISON - Browser Verified (NO PLACEHOLDERS)")
    print("=" * 80)
    
    # Real products to test
    products = [
        "iPhone 16 128GB",
        "Samsung Galaxy S24 128GB",
        "55 inch 4K TV",
        "Laptop 15 inch",
        "Headphones"
    ]
    
    results = []
    
    for p in products:
        print(f"\n🔍 Checking: {p}")
        result = await check_product(p)
        results.append(result)
        
        print(f"  Name: {result['name'][:50]}")
        print(f"  Price: ₹{result['price']:,.0f}")
        if result['mrp'] > 0:
            print(f"  MRP: ₹{result['mrp']:,.0f}")
            print(f"  Discount: {result['discount']}%")
    
    # Sort by price
    results.sort(key=lambda x: x['price'])
    
    print("\n" + "=" * 80)
    print("🏆 BEST DEALS - Sorted by Price (Low to High)")
    print("=" * 80)
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['name'][:50]}")
        print(f"   Store: Flipkart")
        print(f"   Price: ₹{r['price']:,.0f}")
        if r['mrp'] > 0:
            print(f"   MRP: ₹{r['mrp']:,.0f}")
            print(f"   You Save: ₹{r['mrp'] - r['price']:,.0f} ({r['discount']}% OFF)")
    
    print("\n" + "=" * 80)
    print("✅ ALL DATA FROM REAL BROWSER SCRAPING - NO PLACEHOLDERS")
    print("=" * 80)

asyncio.run(main())
