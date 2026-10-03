# -*- coding: utf-8 -*-
"""VGAS - REAL AMAZON LINKS ONLY"""
import asyncio, re, sys
sys.stdout.reconfigure(encoding="utf-8")

async def get_amazon_real_links(query):
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup

    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}&sort=price-asc"

    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=30000, simulate_user=True, magic=True))
        soup = BeautifulSoup(r.html, "lxml")

    results = []
    cards = soup.select("div[data-component-type='s-search-result']")

    for card in cards[:3]:
        name_el = card.select_one("h2 a span")
        link_el = card.select_one("h2 a")
        price_el = card.select_one("span.a-price-whole")

        name = name_el.get_text(strip=True)[:60] if name_el else ""
        href = link_el["href"] if link_el else ""
        price = price_el.get_text(strip=True).replace(",","") if price_el else "0"

        if href and not href.startswith("http"):
            href = "https://www.amazon.in" + href

        # Clean URL - keep only /dp/ASIN part
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
        if asin_match:
            clean_url = f"https://www.amazon.in/dp/{asin_match.group(1)}"
        else:
            clean_url = href

        if name and clean_url and float(price or 0) > 0:
            results.append({"name": name, "price": float(price), "url": clean_url})

    return results

async def main():
    queries = ["iPhone 16 128GB", "Samsung Galaxy S24", "55 inch 4K TV", "Laptop 15 inch", "Headphones"]

    print("=" * 80)
    print("VGAS - REAL AMAZON BUY LINKS (Browser Verified)")
    print("=" * 80)

    for q in queries:
        print(f"\n📦 {q}")
        results = await get_amazon_real_links(q)
        for r in results:
            print(f"   ₹{r['price']:,.0f} - {r['name'][:50]}")
            print(f"   👉 {r['url']}")

asyncio.run(main())
