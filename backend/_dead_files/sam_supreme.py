# -*- coding: utf-8 -*-
"""
SAM SUPREME ORDER - VGAS SHOPPING AI
Master: Vikas Gunjal
SAM + Swarm Army - Full Autonomous Execution
No placeholders. No simulations. Real working code only.
"""
import asyncio, sys, os, json, re, ssl, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

MISTRAL_KEY = os.environ.get("MISTRAL_API_KEY", "")
AFFILIATE = {
    "flipkart.com": "affid=vgas2024&affExtParam1=VGAS-VIKAS",
    "amazon.in":    "tag=vgas-vikasg-21",
    "amazon.com":   "tag=vgas-us-21",
    "myntra.com":   "utm_source=vgas",
    "ajio.com":     "utm_source=vgas",
    "meesho.com":   "utm_source=vgas",
    "snapdeal.com": "utm_source=vgas",
    "tatacliq.com": "utm_source=vgas",
    "croma.com":    "utm_source=vgas",
    "nykaa.com":    "utm_source=vgas",
    "walmart.com":  "utm_source=vgas",
    "ebay.com":     "campid=vgas",
    "aliexpress.com":"utm_source=vgas",
    "noon.com":     "utm_source=vgas",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}
CACHE = {}

def aff_url(url):
    for p, tag in AFFILIATE.items():
        if p in url:
            sep = "&" if "?" in url else "?"
            return f"{url}{sep}{tag}"
    return url

def to_f(t):
    try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
    except: return 0.0

def to_i(t):
    try: return int(re.sub(r"[^\d]","",str(t)) or 0)
    except: return 0

async def browser_scrape(url):
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    cfg = BrowserConfig(headless=True, verbose=False)
    rcfg = CrawlerRunConfig(page_timeout=30000, simulate_user=True, magic=True)
    async with AsyncWebCrawler(config=cfg) as c:
        r = await c.arun(url=url, config=rcfg)
        return r.html if r.success else ""

async def http_scrape(url):
    import aiohttp
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession(headers=HEADERS) as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=ctx) as r:
            return await r.text()

def parse(html, url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # NAME
    name = ""
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","#productTitle","h1._6EBuvT","h1"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and len(t) > 3: name = t[:150]; break
    if not name and soup.title:
        name = soup.title.text.split("-")[0].split("|")[0].strip()

    # PRICE - direct text only, sane range
    prices = []
    for el in soup.find_all(["span","div"], class_=True):
        direct = "".join(str(c) for c in el.children if hasattr(c,"string") and c.string).strip()
        t = el.get_text(strip=True)
        for sym in ["\u20b9","$","£","€"]:
            if sym in t and len(t) < 15:
                v = to_f(t)
                if 100 < v < 9999999: prices.append(v); break
    prices = sorted(set(prices))
    # Smart filter: exclude EMI, cashback, exchange amounts
    # Real price = clean rupee amount without prefix words
    clean_prices = []
    for el in soup.find_all(["span","div"], class_=True):
        t = el.get_text(strip=True)
        # Only pure price like "₹66,900" - no prefix words
        if re.match(r'^[\u20b9\$\£\u20ac][\d,]+$', t):
            v = to_f(t)
            if 5000 < v < 500000:
                clean_prices.append(v)
    clean_prices = sorted(set(clean_prices))
    price = clean_prices[0] if clean_prices else (sorted(set(prices))[0] if prices else 0.0)
    orig  = clean_prices[-1] if len(clean_prices) > 1 else price

    # DISCOUNT
    disc = 0
    for sel in ["div.UkUFwK span","div._3Ay6Sb span","span.savingsPercentage","[class*='discount']"]:
        el = soup.select_one(sel)
        if el: disc = to_i(el.get_text()); break
    if not disc and orig > price > 0:
        disc = round(((orig-price)/orig)*100)

    # RATING
    rating = 0.0
    for sel in ["div.XQDdHH","div._3LWZlK","span.a-icon-alt","div.ipqd2A"]:
        el = soup.select_one(sel)
        if el: rating = to_f(el.get_text()); break

    # IMAGE
    img = ""
    for sel in ["img._396cs4","img.DByuf4","#landingImage","img.s-image"]:
        el = soup.select_one(sel)
        if el and el.get("src"): img = el["src"]; break

    # SPECS
    specs = {}
    for row in soup.select("tr._1s_Smc, tr.WJdYP6")[:15]:
        k = row.select_one("td:first-child")
        v = row.select_one("td:last-child")
        if k and v: specs[k.get_text(strip=True)] = v.get_text(strip=True)

    # FAKE DISCOUNT
    fake = False; fake_msg = "Cannot verify"
    if orig > price > 0:
        actual = round(((orig-price)/orig)*100)
        fake = abs(actual-disc) > 10
        fake_msg = f"FAKE! Claimed {disc}% actual {actual}%" if fake else f"GENUINE {disc}% off"

    return {
        "name": name or "Unknown",
        "price": price, "original_price": orig,
        "discount_percentage": disc, "rating": rating,
        "image": img, "specs": specs,
        "fake_discount": fake, "fake_discount_msg": fake_msg,
        "in_stock": not bool(soup.select_one("[class*='out-of-stock'],[class*='OutOfStock']")),
    }

async def scrape_product(url):
    key = url[:100]
    if key in CACHE and time.time()-CACHE[key][1] < 3600:
        return {**CACHE[key][0], "cached": True}

    needs_browser = any(p in url for p in ["flipkart","meesho","ajio","myntra"])
    html = ""

    if needs_browser:
        html = await browser_scrape(url)
    else:
        try: html = await http_scrape(url)
        except: html = await browser_scrape(url)

    if not html:
        return {"error": "Failed to fetch", "url": url}

    result = parse(html, url)

    # If price still 0, try browser fallback
    if result["price"] == 0 and not needs_browser:
        html2 = await browser_scrape(url)
        if html2: result = parse(html2, url)

    result.update({
        "url": url,
        "affiliate_url": aff_url(url),
        "store": next((p for p in AFFILIATE if p in url), "unknown"),
        "currency": "INR" if any(x in url for x in ["amazon.in","flipkart","myntra","ajio","meesho","snapdeal","tatacliq","croma","nykaa"]) else "USD",
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cached": False,
    })

    if result["price"] > 0:
        CACHE[key] = (result, time.time())
    return result

async def search_platform(platform, query, limit=5):
    urls = {
        "amazon.in":    f"https://www.amazon.in/s?k={query.replace(' ','+')}",
        "flipkart.com": f"https://www.flipkart.com/search?q={query.replace(' ','+')}",
        "myntra.com":   f"https://www.myntra.com/{query.replace(' ','-')}",
        "ajio.com":     f"https://www.ajio.com/search/?text={query.replace(' ','+')}",
        "meesho.com":   f"https://www.meesho.com/search?q={query.replace(' ','+')}",
        "snapdeal.com": f"https://www.snapdeal.com/search?keyword={query.replace(' ','+')}",
        "walmart.com":  f"https://www.walmart.com/search?q={query.replace(' ','+')}",
        "ebay.com":     f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ','+')}",
        "aliexpress.com":f"https://www.aliexpress.com/wholesale?SearchText={query.replace(' ','+')}",
    }
    if platform not in urls: return []
    try:
        html = await http_scrape(urls[platform])
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        products = []
        sel = "div[data-component-type='s-search-result']" if "amazon" in platform else "div[data-id]" if "flipkart" in platform else "div[class*='product'],article"
        for card in soup.select(sel)[:limit]:
            name = ""
            for ns in ["h2 a span","div._4rR01T","span.VU-ZEz","h2","h3"]:
                el = card.select_one(ns)
                if el and el.get_text(strip=True): name = el.get_text(strip=True)[:80]; break
            price = 0.0
            for el in card.find_all(["span","div"], class_=True):
                t = el.get_text(strip=True)
                if any(s in t for s in ["\u20b9","$","£"]) and len(t)<15:
                    v = to_f(t)
                    if v > 100: price = v; break
            link_el = card.select_one("a[href]")
            href = link_el["href"] if link_el else ""
            link = href if href.startswith("http") else f"https://www.{platform}{href}"
            if name:
                products.append({"name":name,"price":price,"url":aff_url(link),"store":platform})
        return products
    except Exception as e:
        return []

async def search_all(query, limit=5):
    platforms = ["amazon.in","flipkart.com","myntra.com","ajio.com","meesho.com","snapdeal.com","walmart.com","ebay.com"]
    tasks = [search_platform(p, query, limit) for p in platforms]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_products = []
    for p, r in zip(platforms, results):
        if isinstance(r, list):
            for item in r: item["store"] = p
            all_products.extend(r)
    # Sort by price
    all_products = [x for x in all_products if x.get("price",0) > 0]
    all_products.sort(key=lambda x: x.get("price",0))
    return all_products

# ============ MAIN TEST ============
async def main():
    print("SAM SWARM ARMY - VGAS UNIVERSAL SCRAPER")
    print("="*55)

    # TEST 1: Flipkart iPhone 16
    print("\n[1] Flipkart iPhone 16 URL Test...")
    r = await scrape_product("https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G")
    print(f"  Name     : {r.get('name')}")
    print(f"  Price    : {r.get('currency')} {r.get('price')}")
    print(f"  MRP      : {r.get('currency')} {r.get('original_price')}")
    print(f"  Discount : {r.get('discount_percentage')}%")
    print(f"  Rating   : {r.get('rating')}")
    print(f"  Fake     : {r.get('fake_discount_msg')}")
    print(f"  Aff URL  : {r.get('affiliate_url','')[:70]}")
    print(f"  Specs    : {len(r.get('specs',{}))} items found")

    # TEST 2: Amazon iPhone 16
    print("\n[2] Amazon.in iPhone 16 Search...")
    results = await search_all("iPhone 16", limit=3)
    print(f"  Total results across all platforms: {len(results)}")
    for item in results[:5]:
        print(f"  {item['store']:20} | {item.get('currency','INR')} {item.get('price'):>10} | {item.get('name','')[:40]}")

    if results:
        best = results[0]
        print(f"\n  BEST PRICE: {best.get('currency')} {best.get('price')} at {best.get('store')}")
        print(f"  BUY LINK : {best.get('url','')[:70]}")

    # Save results
    with open("sam_final_result.json","w",encoding="utf-8") as f:
        json.dump({"flipkart_test": r, "search_results": results[:10]}, f, ensure_ascii=False, indent=2)
    print("\nSAM: Results saved -> sam_final_result.json")
    print("SAM SWARM ARMY: MISSION COMPLETE")

asyncio.run(main())
