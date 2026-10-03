"""
SAM ORDER - VGAS Flipkart Test + Fix
Run: python sam_vgas_test.py
"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

FLIPKART_URL = "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G"

async def main():
    print("=" * 50)
    print("SAM VGAS TEST - iPhone 16 Flipkart")
    print("=" * 50)

    # Test 1: Direct HTTP scrape
    try:
        import aiohttp
        from bs4 import BeautifulSoup
        import re

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-IN,en;q=0.9",
        }
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.get(FLIPKART_URL, timeout=aiohttp.ClientTimeout(total=20)) as r:
                html = await r.text()
                soup = BeautifulSoup(html, "lxml")

                # Try all known selectors
                name = None
                for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","h1._6EBuvT","h1"]:
                    el = soup.select_one(sel)
                    if el and el.get_text(strip=True):
                        name = el.get_text(strip=True); break

                price = None
                for sel in ["div.Nx9bqj._4b5DiR","div.Nx9bqj","div._30jeq3._16Jk6d","div._30jeq3","div.CEmiEU span"]:
                    el = soup.select_one(sel)
                    if el and el.get_text(strip=True):
                        price = el.get_text(strip=True); break

                orig = None
                for sel in ["div.yRaY8j","div._3I9_wc._2p6lqe","div._2p6lqe"]:
                    el = soup.select_one(sel)
                    if el: orig = el.get_text(strip=True); break

                disc = None
                for sel in ["div.UkUFwK span","div._3Ay6Sb span","div.UOCQB1"]:
                    el = soup.select_one(sel)
                    if el: disc = el.get_text(strip=True); break

                rating = None
                for sel in ["div.XQDdHH","div._3LWZlK","div.ipqd2A"]:
                    el = soup.select_one(sel)
                    if el: rating = el.get_text(strip=True); break

                title = soup.title.text if soup.title else ""

                print(f"\n✅ HTTP Scrape Result:")
                print(f"  Title  : {title[:70]}")
                print(f"  Name   : {name or 'NOT FOUND'}")
                print(f"  Price  : {price or 'NOT FOUND'}")
                print(f"  Orig   : {orig or 'NOT FOUND'}")
                print(f"  Disc   : {disc or 'NOT FOUND'}")
                print(f"  Rating : {rating or 'NOT FOUND'}")

                # Find what classes exist for price
                all_divs = soup.find_all("div", class_=True)
                found = []
                for d in all_divs[:300]:
                    t = d.get_text(strip=True)
                    if t.startswith("₹") and len(t) < 15:
                        found.append((str(d.get("class")), t))
                if found:
                    print(f"\n  💰 Price elements found:")
                    for cls, val in found[:5]:
                        print(f"     {cls} => {val}")

    except Exception as e:
        print(f"❌ HTTP Error: {e}")

    # Test 2: Crawl4AI
    print("\n" + "="*50)
    print("Testing Crawl4AI...")
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        from bs4 import BeautifulSoup

        bcfg = BrowserConfig(headless=True, verbose=False)
        rcfg = CrawlerRunConfig(page_timeout=30000, simulate_user=True, magic=True)

        async with AsyncWebCrawler(config=bcfg) as crawler:
            res = await crawler.arun(url=FLIPKART_URL, config=rcfg)
            if res.success:
                soup = BeautifulSoup(res.html, "lxml")
                title = soup.title.text if soup.title else ""
                print(f"✅ Crawl4AI Success!")
                print(f"  Title: {title[:70]}")
                # Find price
                for sel in ["div.Nx9bqj","div._30jeq3","div.CEmiEU"]:
                    el = soup.select_one(sel)
                    if el: print(f"  {sel}: {el.get_text(strip=True)[:30]}"); break
            else:
                print(f"❌ Crawl4AI failed: {res.error_message}")
    except Exception as e:
        print(f"❌ Crawl4AI Error: {e}")

    print("\n✅ SAM TEST COMPLETE")

asyncio.run(main())
