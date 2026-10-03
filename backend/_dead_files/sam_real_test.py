# -*- coding: utf-8 -*-
"""SAM REAL TEST - Samsung Galaxy S24 Search"""
import asyncio, sys, re
sys.stdout.reconfigure(encoding="utf-8")

async def main():
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    print("=" * 70)
    print("📱 SAM REAL TEST - Samsung Galaxy S24 Search")
    print("=" * 70)
    
    query = "Samsung Galaxy S24"
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&sort=price_asc"
    
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=20000, simulate_user=True, magic=True))
        soup = BeautifulSoup(r.html, "lxml")
    
    # Find product cards
    cards = soup.select("div[data-id]")
    
    if not cards:
        print("❌ No products found - trying alternative selector")
        cards = soup.select("div._1AtBbE")
    
    print(f"\nFound {len(cards)} products\n")
    
    for i, card in enumerate(cards[:3], 1):
        # Extract name
        name_el = card.select_one("div.KzDlHZ, a.s1Q9rs, div._4rR01T, h1")
        name = name_el.get_text(strip=True) if name_el else "Unknown"
        
        # Extract price
        price_el = card.select_one("div._1psv1ze2c, div._30jeq3, div.Nx9bqj")
        price = price_el.get_text(strip=True) if price_el else "N/A"
        
        # Extract original price
        orig_el = card.select_one("div._1psv1zekc, div.yRaY8j, div._2p6lqe")
        orig = orig_el.get_text(strip=True) if orig_el else "N/A"
        
        print(f"Product {i}:")
        print(f"  Name: {name[:60]}")
        print(f"  Price: {price}")
        print(f"  Original: {orig}")
        
        # Calculate discount
        if price != "N/A" and orig != "N/A":
            p = float(re.sub(r'[^0-9.]','',price))
            o = float(re.sub(r'[^0-9.]','',orig))
            if o > 0:
                discount = round(((o - p) / o) * 100)
                print(f"  Discount: {discount}% OFF")
                print(f"  Saving: ₹{o - p:,.0f}")
        print()

asyncio.run(main())
