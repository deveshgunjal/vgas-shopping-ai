# -*- coding: utf-8 -*-
import asyncio, sys, re, ssl, time, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

TEST_URLS = [
    # Flipkart
    "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G",
    "https://www.flipkart.com/samsung-galaxy-s24-cobalt-violet-256-gb/p/itm6c9f1e5b4e5a4",
    "https://www.flipkart.com/sony-wh-1000xm5-bluetooth-headset/p/itm6c9f1e5b4e5a5",
    # Amazon
    "https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX1W1XY",
    "https://www.amazon.in/Samsung-Galaxy-Buds2-Pro-Graphite/dp/B0B2HKPWWQ",
    # Search queries
]

SEARCH_QUERIES = [
    "iPhone 16",
    "Samsung Galaxy S24",
    "Sony WH-1000XM5 headphones",
    "Nike shoes",
    "laptop under 50000",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

PLATFORMS = {
    "amazon.in":    {"search": "https://www.amazon.in/s?k={q}",            "currency": "INR", "aff": "tag=vgas-vikasg-21"},
    "flipkart.com": {"search": "https://www.flipkart.com/search?q={q}",    "currency": "INR", "aff": "affid=vgas2024"},
    "meesho.com":   {"search": "https://www.meesho.com/search?q={q}",      "currency": "INR", "aff": "utm_source=vgas"},
    "snapdeal.com": {"search": "https://www.snapdeal.com/search?keyword={q}", "currency": "INR", "aff": "utm_source=vgas"},
    "ebay.com":     {"search": "https://www.ebay.com/sch/i.html?_nkw={q}", "currency": "USD", "aff": "campid=vgas"},
    "walmart.com":  {"search": "https://www.walmart.com/search?q={q}",     "currency": "USD", "aff": "utm_source=vgas"},
    "aliexpress.com":{"search":"https://www.aliexpress.com/wholesale?SearchText={q}", "currency": "USD", "aff": "utm_source=vgas"},
}

CURRENCY_INR = {"INR":1,"USD":84,"GBP":107,"EUR":91,"AED":23}

def to_f(t):
    try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
    except: return 0.0

def aff_url(url, platform):
    cfg = PLATFORMS.get(platform,{})
    if not cfg: return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{cfg.get('aff','utm_source=vgas')}"

async def http_get(url):
    try:
        import aiohttp
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(headers=HEADERS) as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=12), ssl=ctx) as r:
                return await r.text()
    except: return ""

async def browser_get(url):
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
            r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000,simulate_user=True,magic=True))
            return r.html if r.success else ""
    except: return ""

def parse_product(html, url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    platform = next((p for p in PLATFORMS if p in url), "unknown")
    currency = PLATFORMS.get(platform,{}).get("currency","INR")

    # NAME
    name = ""
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","#productTitle","h1._6EBuvT","h1"]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 3:
            name = el.get_text(strip=True)[:120]; break
    if not name and soup.title:
        name = soup.title.text.split("-")[0].split("|")[0].strip()[:120]

    # PRICE - pure clean amounts only
    prices = []
    for el in soup.find_all(["span","div"], class_=True):
        t = el.get_text(strip=True)
        if re.match(r'^[\u20b9\$\£\€][\d,]+(\.\d{1,2})?$', t):
            v = to_f(t)
            if 100 < v < 10000000: prices.append(v)
    prices = sorted(set(prices))
    price = prices[0] if prices else 0.0
    orig  = prices[-1] if len(prices)>1 else price

    # DISCOUNT
    disc = 0
    for sel in ["div.UkUFwK span","div._3Ay6Sb span","span.savingsPercentage"]:
        el = soup.select_one(sel)
        if el: disc = int(re.sub(r"[^\d]","",el.get_text()) or 0); break
    if not disc and orig > price > 0:
        disc = round(((orig-price)/orig)*100)

    # RATING
    rating = 0.0
    for sel in ["div.XQDdHH","div._3LWZlK","span.a-icon-alt","div.ipqd2A"]:
        el = soup.select_one(sel)
        if el:
            v = to_f(el.get_text())
            if 0 < v <= 5: rating = v; break

    # IMAGE
    img = ""
    for sel in ["img._396cs4","img.DByuf4","#landingImage","img.s-image"]:
        el = soup.select_one(sel)
        if el and el.get("src"): img = el["src"]; break

    # FAKE DISCOUNT
    fake = False; fake_msg = "N/A"
    if orig > price > 0:
        actual = round(((orig-price)/orig)*100)
        fake = abs(actual-disc) > 10
        fake_msg = f"FAKE({disc}% claimed,{actual}% real)" if fake else f"GENUINE {actual}%"

    return {
        "name": name or "Unknown",
        "price": price, "original_price": orig,
        "discount": disc, "rating": rating, "image": img,
        "currency": currency, "price_inr": price * CURRENCY_INR.get(currency,1),
        "store": platform, "url": aff_url(url, platform),
        "fake": fake, "fake_msg": fake_msg,
        "in_stock": "out" not in html.lower()[:500],
    }

async def scrape_url(url):
    needs_browser = any(p in url for p in ["flipkart","meesho","ajio","myntra"])
    html = await browser_get(url) if needs_browser else await http_get(url)
    if not html: html = await browser_get(url)
    if not html: return {"error":"fetch failed","url":url}
    return parse_product(html, url)

async def search_platform(platform, query, limit=4):
    cfg = PLATFORMS.get(platform)
    if not cfg: return []
    url = cfg["search"].format(q=query.replace(" ","+"))
    html = await http_get(url)
    if not html: return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    products = []
    sel = {
        "amazon.in":"div[data-component-type='s-search-result']",
        "flipkart.com":"div[data-id]",
        "ebay.com":"li.s-item",
    }.get(platform,"div[class*='product'],article")
    for card in soup.select(sel)[:limit]:
        name = ""
        for ns in ["h2 a span","div._4rR01T","span.VU-ZEz","h2","h3"]:
            el = card.select_one(ns)
            if el and el.get_text(strip=True): name = el.get_text(strip=True)[:80]; break
        price = 0.0
        for el in card.find_all(["span","div"],class_=True):
            t = el.get_text(strip=True)
            if re.match(r'^[\u20b9\$\£][\d,]+',t) and len(t)<15:
                v = to_f(t)
                if v > 10: price = v; break
        link_el = card.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        link = href if href.startswith("http") else f"https://www.{platform}{href}"
        img_el = card.select_one("img")
        img = img_el.get("src","") if img_el else ""
        if name and price > 0:
            products.append({
                "name":name,"price":price,
                "price_inr": price * CURRENCY_INR.get(cfg["currency"],1),
                "currency":cfg["currency"],
                "url":aff_url(link,platform),"store":platform,"image":img
            })
    return products

async def world_lowest(query, limit=4):
    tasks = [search_platform(p, query, limit) for p in PLATFORMS]
    all_results = await asyncio.gather(*tasks, return_exceptions=True)
    products = []
    for r in all_results:
        if isinstance(r, list): products.extend(r)
    products = [p for p in products if p.get("price_inr",0) > 0]
    products.sort(key=lambda x: x["price_inr"])
    return products

async def main():
    print("SAM MULTI-PRODUCT TEST")
    print("="*60)

    # TEST URLS
    print("\n--- URL SCRAPE TESTS ---")
    for url in TEST_URLS:
        r = await scrape_url(url)
        status = "OK" if r.get("price",0) > 0 else "PRICE_MISSING"
        print(f"[{status}] {r.get('store','?'):15} | {r.get('currency','?')} {r.get('price',0):>10,.0f} | {r.get('name','?')[:45]}")
        print(f"         Disc:{r.get('discount',0)}% | Rating:{r.get('rating',0)} | Fake:{r.get('fake_msg','?')}")

    # WORLD SEARCH
    print("\n--- WORLD LOWEST PRICE SEARCH ---")
    all_report = {}
    for query in SEARCH_QUERIES:
        print(f"\nQuery: '{query}'")
        results = await world_lowest(query, limit=3)
        all_report[query] = results[:5]
        if results:
            best = results[0]
            print(f"  LOWEST : {best['currency']} {best['price']:,.0f} = Rs {best['price_inr']:,.0f} @ {best['store']}")
            print(f"  LINK   : {best['url'][:70]}")
            for r in results[1:4]:
                print(f"  Also   : {r['currency']} {r['price']:,.0f} @ {r['store']} | {r['name'][:40]}")
        else:
            print("  No results found")

    # SAVE REPORT
    with open("sam_multi_report.json","w",encoding="utf-8") as f:
        json.dump(all_report, f, ensure_ascii=False, indent=2)
    print("\nSAM: Full report -> sam_multi_report.json")
    print("SAM MISSION COMPLETE")

asyncio.run(main())
