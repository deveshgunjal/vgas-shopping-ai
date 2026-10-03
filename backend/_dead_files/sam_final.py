# -*- coding: utf-8 -*-
"""SAM FINAL - VGAS REAL WORKING"""
import asyncio, sys, re, json, time
sys.stdout.reconfigure(encoding="utf-8")

async def main():
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    
    url = "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G"
    
    async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=20000,simulate_user=True,magic=True))
        soup = BeautifulSoup(r.html,"lxml")
    
    # Extract all rupee prices
    prices = []
    for el in soup.find_all(["div","span"], class_=True):
        t = el.get_text(strip=True)
        if re.match(r'^₹[\d,]+$', t):
            v = float(re.sub(r'[^0-9.]','',t))
            if 1000 < v < 500000: prices.append(v)
    
    prices = sorted(set(prices))
    
    print(f"NAME: {soup.title.text.split('-')[0].strip()[:60]}")
    print(f"REAL PRICE: Rs {prices[0]:,.0f}" if prices else "NO PRICE")
    print(f"MRP: Rs {prices[-1]:,.0f}" if len(prices)>1 else "NO MRP")
    print(f"DISCOUNT: {round(((prices[-1]-prices[0])/prices[-1])*100) if len(prices)>1 else 0}%")

asyncio.run(main())
