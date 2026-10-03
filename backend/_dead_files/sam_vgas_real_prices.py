# -*- coding: utf-8 -*-
"""VGAS REAL PRICES - Browser Verified"""
import asyncio, re, sys
sys.stdout.reconfigure(encoding="utf-8")

async def check_flipkart(query):
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&sort=price_asc"
    
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000, simulate_user=True, magic=True))
        soup = BeautifulSoup(r.html, "lxml")
    
    prices = []
    for el in soup.find_all(["div", "span"], class_=True):
        t = el.get_text(strip=True)
        if "₹" in t:
            n = re.findall(r"[\d,]+", t)
            if n:
                v = float(n[0].replace(",", ""))
                if 10000 < v < 150000:
                    prices.append(v)
    
    prices = sorted(set(prices))
    
    names = soup.select("div.KzDlHZ, a.s1Q9rs")
    name = names[0].get_text(strip=True)[:50] if names else query
    
    return {"name": name, "prices": prices}

async def main():
    print("=" * 70)
    print("VGAS REAL PRICES - Browser Verified")
    print("=" * 70)
    
    products = ["iPhone 16", "Samsung Galaxy S24", "TV 55 inch"]
    
    for p in products:
        print(f"\n📦 {p}")
        print("-" * 40)
        
        result = await check_flipkart(p)
        print(f"नाव: {result['name']}")
        
        if result['prices']:
            print(f"खरी किंमत: ₹{result['prices'][0]:,.0f}")
            if len(result['prices']) > 1:
                print(f"सर्वात महागडी: ₹{result['prices'][-1]:,.0f}")
                disc = int(((result['prices'][-1] - result['prices'][0]) / result['prices'][-1]) * 100)
                print(f"खरं सूट: {disc}%")
        else:
            print("❌ कोणतेही खरे उत्पादन सापडलं नाही")

asyncio.run(main())
