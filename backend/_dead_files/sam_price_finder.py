# -*- coding: utf-8 -*-
"""SAM: Extract real price from Crawl4AI rendered Flipkart page"""
import asyncio, sys, re, json
sys.stdout.reconfigure(encoding="utf-8")

URL = "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G"

async def main():
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup

    cfg  = BrowserConfig(headless=True, verbose=False)
    rcfg = CrawlerRunConfig(page_timeout=30000, simulate_user=True, magic=True)

    async with AsyncWebCrawler(config=cfg) as c:
        res = await c.arun(url=URL, config=rcfg)

    soup = BeautifulSoup(res.html, "lxml")

    # Collect ALL rupee elements with their exact class
    rupee_data = []
    for el in soup.find_all(["div","span"], class_=True):
        t = el.get_text(strip=True)
        if "\u20b9" in t and len(t) < 20:
            val = float(re.sub(r"[^\d.]","",t) or 0)
            if val > 0:
                rupee_data.append({"class": el.get("class"), "text": t, "value": val})

    # Sort by value
    rupee_data.sort(key=lambda x: x["value"])

    print("ALL PRICES FOUND:")
    for d in rupee_data:
        print(f"  {d['value']:>12,.0f}  |  {d['text']:20}  |  {d['class']}")

    # Best price = lowest value > 5000 and < 200000 (phone range)
    phone_prices = [d for d in rupee_data if 5000 < d["value"] < 200000]
    if phone_prices:
        best = phone_prices[0]
        mrp  = phone_prices[-1]
        disc = round(((mrp["value"]-best["value"])/mrp["value"])*100) if mrp["value"] > best["value"] else 0
        print(f"\nRESULT:")
        print(f"  Name     : Apple iPhone 16 (White, 128 GB)")
        print(f"  Price    : Rs {best['value']:,.0f}  (class: {best['class']})")
        print(f"  MRP      : Rs {mrp['value']:,.0f}")
        print(f"  Discount : {disc}%")
        print(f"  Fake     : {'FAKE' if abs(disc-20)>15 else 'GENUINE'}")

        # Save winning class to use in scraper
        with open("winning_price_class.json","w") as f:
            json.dump({"price_class": best["class"], "mrp_class": mrp["class"]}, f, indent=2)
        print(f"\nSAM: Winning class saved -> winning_price_class.json")

asyncio.run(main())
