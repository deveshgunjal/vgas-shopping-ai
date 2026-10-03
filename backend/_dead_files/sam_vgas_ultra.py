# -*- coding: utf-8 -*-
"""
VGAS ULTRA ENGINE - Browser + Requests Hybrid
Amazon: Browser (works)
Flipkart/Meesho: Requests (fast)
"""
import asyncio, re, sys, concurrent.futures
sys.stdout.reconfigure(encoding="utf-8")

def fetch_flipkart(query):
    """Flipkart - Fast requests"""
    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&sort=price_asc"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        if r.status_code != 200: return None
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all(["div", "span"], class_=True):
            t = el.get_text(strip=True)
            if "₹" in t:
                n = re.findall(r"[\d,]+", t)
                if n:
                    v = float(n[0].replace(",", ""))
                    if 1000 < v < 500000:
                        prices.append(v)
        
        if prices:
            low = min(prices)
            high = max(prices)
            disc = int(((high - low) / high) * 100)
            names = soup.select("div.KzDlHZ, a.s1Q9rs")
            name = names[0].get_text(strip=True)[:50] if names else query
            
            return {"store": "Flipkart", "name": name, "price": low, "mrp": high, "discount": disc}
    except: pass
    return None

def fetch_meesho(query):
    """Meesho - Fast requests"""
    try:
        url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all(["h5", "span"]):
            t = el.get_text()
            if "₹" in t:
                n = re.findall(r"[\d,]+", t)
                if n:
                    v = float(n[0].replace(",", ""))
                    if 100 < v < 100000:
                        prices.append(v)
        
        if prices:
            low = min(prices)
            high = max(prices)
            return {"store": "Meesho", "name": query, "price": low, "mrp": high, "discount": int(((high-low)/high)*100)}
    except: pass
    return None

async def fetch_amazon(query):
    """Amazon - Browser (slow but works)"""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        from bs4 import BeautifulSoup
        
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}&sort=price-asc"
        
        async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
            r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=30000, simulate_user=True, magic=True))
            soup = BeautifulSoup(r.html, "lxml")
        
        prices = []
        for el in soup.find_all("span", class_="a-price-whole"):
            t = el.get_text(strip=True).replace(",", "")
            if t.isdigit() and 1000 < float(t) < 500000:
                prices.append(float(t))
        
        if prices:
            low = min(prices)
            high = max(prices)
            disc = int(((high - low) / high) * 100)
            names = soup.select("h2 a span")
            name = names[0].get_text(strip=True)[:50] if names else query
            
            return {"store": "Amazon", "name": name, "price": low, "mrp": high, "discount": disc}
    except Exception as e:
        print(f"Amazon error: {e}")
        return None

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36"}

import requests

async def find_cheapest(query):
    print("=" * 70)
    print(f"🔍 VGAS ULTRA ENGINE - {query}")
    print("=" * 70)
    
    results = []
    
    # Flipkart & Meesho in parallel (fast)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(fetch_flipkart, query)
        f2 = ex.submit(fetch_meesho, query)
        
        for f in [f1, f2]:
            r = f.result()
            if r and r.get("price", 0) > 0:
                results.append(r)
    
    # Amazon (browser - slow but works)
    r = await fetch_amazon(query)
    if r and r.get("price", 0) > 0:
        results.append(r)
    
    # Sort by price
    results.sort(key=lambda x: x["price"])
    
    # Display
    print("\n📊 सर्व प्लॅटफॉर्मवरील किंमत:\n")
    
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['store']:12} | ₹{r['price']:>8,.0f}")
        print(f"     MRP: ₹{r['mrp']:>8,.0f} | {r['discount']}% OFF")
        print(f"     नाव: {r['name'][:40]}...")
        print()
    
    if results:
        cheapest = results[0]
        print("=" * 70)
        print(f"🏆 सर्वात स्वस्त: {cheapest['store']} - ₹{cheapest['price']:,.0f}")
        print(f"   तुमचं बचत: ₹{cheapest['mrp'] - cheapest['price']:,.0f} ({cheapest['discount']}% OFF)")
        print("=" * 70)
        return results
    else:
        print("❌ कोणतेही प्रॉडक्ट सापडलं नाही")
        return []

# Test
if __name__ == "__main__":
    asyncio.run(find_cheapest("iPhone 16"))
    print("\n" + "="*70)
    asyncio.run(find_cheapest("Samsung Galaxy S24"))