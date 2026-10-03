# -*- coding: utf-8 -*-
"""SAM TEST - Samsung Galaxy S24"""
import asyncio, sys, re
sys.stdout.reconfigure(encoding="utf-8")

async def main():
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    # Test Samsung Galaxy S24
    url = "https://www.flipkart.com/samsung-galaxy-s24-ultra-5g-phantom-black-256-gb/p/itm849567890"
    
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=20000, simulate_user=True, magic=True))
        soup = BeautifulSoup(r.html, "lxml")
    
    # Extract prices
    prices = []
    for el in soup.find_all(["div","span"], class_=True):
        t = el.get_text(strip=True)
        if re.match(r'^₹[\d,]+$', t):
            v = float(re.sub(r'[^0-9.]','',t))
            if 1000 < v < 1000000:
                prices.append(v)
    
    prices = sorted(set(prices))
    
    print("=" * 60)
    print("📱 SAM TEST - Samsung Galaxy S24 Ultra")
    print("=" * 60)
    print(f"NAME: {soup.title.text.split(':')[0].strip()[:60]}")
    print(f"REAL PRICE: Rs {prices[0]:,.0f}" if prices else "NO PRICE")
    print(f"MRP: Rs {prices[-1]:,.0f}" if len(prices)>1 else "NO MRP")
    if len(prices) > 1:
        discount = round(((prices[-1]-prices[0])/prices[-1])*100)
        print(f"DISCOUNT: {discount}%")
        print(f"SAVING: Rs {prices[-1]-prices[0]:,.0f}")
    print("=" * 60)

asyncio.run(main())
