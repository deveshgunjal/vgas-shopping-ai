# -*- coding: utf-8 -*-
import asyncio, sys, re
sys.stdout.reconfigure(encoding='utf-8')

URL = "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G"

async def main():
    print("SAM: Crawl4AI browser test...")
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup

    cfg = BrowserConfig(headless=True, verbose=False)
    rcfg = CrawlerRunConfig(page_timeout=35000, simulate_user=True, magic=True)

    async with AsyncWebCrawler(config=cfg) as crawler:
        res = await crawler.arun(url=URL, config=rcfg)
        print("Success:", res.success)
        if res.success:
            soup = BeautifulSoup(res.html, "lxml")
            # Find all rupee prices
            found = []
            for el in soup.find_all(["div","span"], class_=True):
                t = el.get_text(strip=True)
                if "\u20b9" in t and 3 < len(t) < 15:
                    found.append((str(el.get("class")), t))
            print("PRICE ELEMENTS:")
            for c,v in found[:10]:
                print(" ", c, "->", v)
            name = soup.select_one("span.VU-ZEz") or soup.select_one("span.B_NuCI") or soup.select_one("h1")
            print("NAME:", name.get_text(strip=True)[:80] if name else "NOT FOUND")
        else:
            print("ERROR:", res.error_message)

asyncio.run(main())
