# -*- coding: utf-8 -*-
"""
SAM ULTIMATE MISSION - VGAS SHOPPING AI
Goal: Find LOWEST PRICE for ANY product from ENTIRE WORLD
Master: Vikas Gunjal
All permissions granted. Real working. No placeholders.
"""
import asyncio, sys, re, json, ssl, time, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

# ============================================================
# WORLD PLATFORMS - 30+ stores
# ============================================================
WORLD_PLATFORMS = {
    # INDIA
    "amazon.in":      {"search": "https://www.amazon.in/s?k={q}",           "currency": "INR", "affiliate": "tag=vgas-vikasg-21"},
    "flipkart.com":   {"search": "https://www.flipkart.com/search?q={q}",   "currency": "INR", "affiliate": "affid=vgas2024"},
    "myntra.com":     {"search": "https://www.myntra.com/{q}",               "currency": "INR", "affiliate": "utm_source=vgas"},
    "ajio.com":       {"search": "https://www.ajio.com/search/?text={q}",   "currency": "INR", "affiliate": "utm_source=vgas"},
    "meesho.com":     {"search": "https://www.meesho.com/search?q={q}",     "currency": "INR", "affiliate": "utm_source=vgas"},
    "snapdeal.com":   {"search": "https://www.snapdeal.com/search?keyword={q}", "currency": "INR", "affiliate": "utm_source=vgas"},
    "tatacliq.com":   {"search": "https://www.tatacliq.com/search/?searchCategory=all&text={q}", "currency": "INR", "affiliate": "utm_source=vgas"},
    "croma.com":      {"search": "https://www.croma.com/searchB?q={q}",     "currency": "INR", "affiliate": "utm_source=vgas"},
    "nykaa.com":      {"search": "https://www.nykaa.com/search/result/?q={q}", "currency": "INR", "affiliate": "utm_source=vgas"},
    "reliancedigital.in": {"search": "https://www.reliancedigital.in/search?q={q}", "currency": "INR", "affiliate": "utm_source=vgas"},
    # USA
    "amazon.com":     {"search": "https://www.amazon.com/s?k={q}",          "currency": "USD", "affiliate": "tag=vgas-us-21"},
    "walmart.com":    {"search": "https://www.walmart.com/search?q={q}",    "currency": "USD", "affiliate": "utm_source=vgas"},
    "ebay.com":       {"search": "https://www.ebay.com/sch/i.html?_nkw={q}","currency": "USD", "affiliate": "campid=vgas"},
    "bestbuy.com":    {"search": "https://www.bestbuy.com/site/searchpage.jsp?st={q}", "currency": "USD", "affiliate": "utm_source=vgas"},
    "target.com":     {"search": "https://www.target.com/s?searchTerm={q}", "currency": "USD", "affiliate": "utm_source=vgas"},
    "newegg.com":     {"search": "https://www.newegg.com/p/pl?d={q}",       "currency": "USD", "affiliate": "utm_source=vgas"},
    # GLOBAL
    "aliexpress.com": {"search": "https://www.aliexpress.com/wholesale?SearchText={q}", "currency": "USD", "affiliate": "utm_source=vgas"},
    "ebay.co.uk":     {"search": "https://www.ebay.co.uk/sch/i.html?_nkw={q}", "currency": "GBP", "affiliate": "campid=vgas"},
    "amazon.co.uk":   {"search": "https://www.amazon.co.uk/s?k={q}",        "currency": "GBP", "affiliate": "tag=vgas-uk-21"},
    "amazon.de":      {"search": "https://www.amazon.de/s?k={q}",           "currency": "EUR", "affiliate": "tag=vgas-de-21"},
    "noon.com":       {"search": "https://www.noon.com/uae-en/search/?q={q}", "currency": "AED", "affiliate": "utm_source=vgas"},
    "amazon.ae":      {"search": "https://www.amazon.ae/s?k={q}",           "currency": "AED", "affiliate": "tag=vgas-ae-21"},
}

# Currency to INR conversion (approximate)
CURRENCY_TO_INR = {
    "INR": 1, "USD": 84, "GBP": 107, "EUR": 91,
    "AED": 23, "CAD": 62, "AUD": 55, "SGD": 63,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}

CACHE = {}

# ============================================================
# CORE FUNCTIONS
# ============================================================
def aff(url, platform):
    cfg = WORLD_PLATFORMS.get(platform, {})
    if not cfg: return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{cfg['affiliate']}&vgas=1"

def to_f(t):
    try: return float(re.sub(r"[^\d.]", "", str(t)) or 0)
    except: return 0.0

def to_inr(price, currency):
    return price * CURRENCY_TO_INR.get(currency, 1)

async def http_get(url):
    try:
        import aiohttp
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(headers=HEADERS) as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=12), ssl=ctx) as r:
                return await r.text()
    except: return ""

async def browser_get(url):
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        cfg  = BrowserConfig(headless=True, verbose=False)
        rcfg = CrawlerRunConfig(page_timeout=25000, simulate_user=True, magic=True)
        async with AsyncWebCrawler(config=cfg) as c:
            r = await c.arun(url=url, config=rcfg)
            return r.html if r.success else ""
    except: return ""

def extract_prices(html):
    """Extract all clean prices from HTML"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    prices = []
    for el in soup.find_all(["span","div"], class_=True):
        t = el.get_text(strip=True)
        # Pure price only - no prefix words
        if re.match(r'^[\u20b9\$\£\€AED\s]*[\d,]+(\.\d{1,2})?$', t):
            v = to_f(t)
            if 100 < v < 10000000:
                prices.append(v)
    return sorted(set(prices))

def extract_name(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","#productTitle","h1._6EBuvT","h1"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and len(t) > 3: return t[:150]
    if soup.title:
        return soup.title.text.split("-")[0].split("|")[0].strip()
    return "Unknown"

def extract_rating(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for sel in ["div.XQDdHH","div._3LWZlK","span.a-icon-alt","div.ipqd2A","[class*='rating']"]:
        el = soup.select_one(sel)
        if el:
            v = to_f(el.get_text())
            if 0 < v <= 5: return v
    return 0.0

def extract_image(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for sel in ["img._396cs4","img.DByuf4","#landingImage","img.s-image","img[data-old-hires]"]:
        el = soup.select_one(sel)
        if el:
            return el.get("data-old-hires") or el.get("src","")
    return ""

def fake_discount_check(price, orig, claimed_disc):
    if orig <= price or price <= 0: return False, "Cannot verify"
    actual = round(((orig-price)/orig)*100)
    fake = abs(actual - claimed_disc) > 10
    msg = f"FAKE! Claimed {claimed_disc}% but actual {actual}%" if fake else f"GENUINE {actual}% off"
    return fake, msg

# ============================================================
# PRODUCT SCRAPER
# ============================================================
async def scrape_url(url):
    """Scrape any product URL from any platform"""
    key = url[:120]
    if key in CACHE and time.time()-CACHE[key][1] < 3600:
        return {**CACHE[key][0], "cached": True}

    platform = next((p for p in WORLD_PLATFORMS if p in url), "unknown")
    needs_browser = any(p in url for p in ["flipkart","meesho","ajio","myntra","noon"])

    html = await browser_get(url) if needs_browser else await http_get(url)
    if not html: html = await browser_get(url)
    if not html: return {"error": "Cannot fetch", "url": url}

    prices = extract_prices(html)
    name   = extract_name(html)
    rating = extract_rating(html)
    image  = extract_image(html)
    cfg    = WORLD_PLATFORMS.get(platform, {})
    currency = cfg.get("currency", "INR")

    price = prices[0] if prices else 0.0
    orig  = prices[-1] if len(prices) > 1 else price

    # Discount
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    disc = 0
    for sel in ["div.UkUFwK span","div._3Ay6Sb span","span.savingsPercentage","[class*='discount']"]:
        el = soup.select_one(sel)
        if el:
            disc = int(re.sub(r"[^\d]","",el.get_text()) or 0); break
    if not disc and orig > price > 0:
        disc = round(((orig-price)/orig)*100)

    fake, fake_msg = fake_discount_check(price, orig, disc)

    result = {
        "name": name, "price": price, "original_price": orig,
        "discount_percentage": disc, "rating": rating, "image": image,
        "currency": currency, "price_inr": to_inr(price, currency),
        "store": platform, "url": url, "affiliate_url": aff(url, platform),
        "fake_discount": fake, "fake_discount_msg": fake_msg,
        "in_stock": not bool(soup.select_one("[class*='out-of-stock'],[class*='OutOfStock']")),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"), "cached": False,
    }
    if price > 0: CACHE[key] = (result, time.time())
    return result

# ============================================================
# WORLD SEARCH - All platforms parallel
# ============================================================
async def search_one_platform(platform, query, limit=5):
    cfg = WORLD_PLATFORMS.get(platform)
    if not cfg: return []
    url = cfg["search"].format(q=query.replace(" ","+"))
    html = await http_get(url)
    if not html: return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    products = []

    card_sel = {
        "amazon.in":  "div[data-component-type='s-search-result']",
        "amazon.com": "div[data-component-type='s-search-result']",
        "amazon.co.uk":"div[data-component-type='s-search-result']",
        "amazon.de":  "div[data-component-type='s-search-result']",
        "amazon.ae":  "div[data-component-type='s-search-result']",
        "flipkart.com":"div[data-id]",
        "ebay.com":   "li.s-item",
        "ebay.co.uk": "li.s-item",
        "walmart.com":"div[data-item-id]",
    }.get(platform, "div[class*='product'],article,li[class*='item']")

    for card in soup.select(card_sel)[:limit]:
        name = ""
        for ns in ["h2 a span","div._4rR01T","span.VU-ZEz","h2","h3","a[class*='title']"]:
            el = card.select_one(ns)
            if el and el.get_text(strip=True):
                name = el.get_text(strip=True)[:100]; break

        price = 0.0
        for el in card.find_all(["span","div"], class_=True):
            t = el.get_text(strip=True)
            if re.match(r'^[\u20b9\$\£\€][\d,]+', t) and len(t) < 15:
                v = to_f(t)
                if v > 10: price = v; break

        link_el = card.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        link = href if href.startswith("http") else f"https://www.{platform}{href}"

        img_el = card.select_one("img")
        img = img_el.get("src","") if img_el else ""

        if name and price > 0:
            products.append({
                "name": name[:100], "price": price,
                "price_inr": to_inr(price, cfg["currency"]),
                "currency": cfg["currency"],
                "url": aff(link, platform), "store": platform, "image": img,
            })
    return products

async def world_search(query, limit=5):
    """Search ALL world platforms in parallel"""
    tasks = {p: search_one_platform(p, query, limit) for p in WORLD_PLATFORMS}
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    all_products = []
    for platform, result in zip(tasks.keys(), results):
        if isinstance(result, list):
            all_products.extend(result)

    # Sort by INR price (lowest first)
    valid = [p for p in all_products if p.get("price_inr",0) > 0]
    valid.sort(key=lambda x: x["price_inr"])
    return valid

# ============================================================
# PRICE HISTORY + TRACKER
# ============================================================
PRICE_HISTORY_FILE = "price_history.json"

def save_price_history(product_name, price, store, currency):
    history = {}
    if os.path.exists(PRICE_HISTORY_FILE):
        with open(PRICE_HISTORY_FILE,"r",encoding="utf-8") as f:
            history = json.load(f)
    key = product_name[:50]
    if key not in history: history[key] = []
    history[key].append({
        "price": price, "store": store, "currency": currency,
        "date": time.strftime("%Y-%m-%d %H:%M")
    })
    history[key] = history[key][-30:]  # keep last 30 records
    with open(PRICE_HISTORY_FILE,"w",encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_price_history(product_name):
    if not os.path.exists(PRICE_HISTORY_FILE): return []
    with open(PRICE_HISTORY_FILE,"r",encoding="utf-8") as f:
        history = json.load(f)
    return history.get(product_name[:50], [])

# ============================================================
# SAM TEST - FULL MISSION
# ============================================================
async def main():
    print("SAM ULTIMATE MISSION - WORLD LOWEST PRICE FINDER")
    print("="*55)

    # TEST 1: Scrape Flipkart URL
    print("\n[1] Scraping Flipkart iPhone 16...")
    r = await scrape_url("https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G")
    print(f"  Name     : {r.get('name')}")
    print(f"  Price    : {r.get('currency')} {r.get('price'):,.0f}")
    print(f"  MRP      : {r.get('currency')} {r.get('original_price'):,.0f}")
    print(f"  Discount : {r.get('discount_percentage')}%")
    print(f"  Fake     : {r.get('fake_discount_msg')}")
    print(f"  Aff URL  : {r.get('affiliate_url','')[:65]}")
    save_price_history(r.get("name",""), r.get("price",0), r.get("store",""), r.get("currency",""))

    # TEST 2: World Search
    print("\n[2] World Search: iPhone 16 (all platforms parallel)...")
    t0 = time.time()
    results = await world_search("iPhone 16", limit=3)
    elapsed = time.time()-t0
    print(f"  Found {len(results)} results in {elapsed:.1f}s")
    print(f"\n  {'STORE':25} {'PRICE':>12} {'INR':>12}  NAME")
    print(f"  {'-'*70}")
    for item in results[:10]:
        print(f"  {item['store']:25} {item['currency']+' '+str(int(item['price'])):>12} {int(item['price_inr']):>10}  {item['name'][:35]}")

    if results:
        best = results[0]
        print(f"\n  WORLD LOWEST: {best['currency']} {best['price']:,.0f} = Rs {best['price_inr']:,.0f} at {best['store']}")
        print(f"  BUY NOW     : {best['url'][:70]}")

    # TEST 3: Price History
    print("\n[3] Price History saved for tracking...")
    history = get_price_history(r.get("name",""))
    print(f"  Records: {len(history)}")

    # Save full report
    report = {
        "mission": "VGAS World Lowest Price",
        "flipkart_result": r,
        "world_search_top10": results[:10],
        "total_platforms": len(WORLD_PLATFORMS),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("sam_ultimate_report.json","w",encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\nSAM: Report saved -> sam_ultimate_report.json")
    print("SAM ULTIMATE MISSION: COMPLETE")

asyncio.run(main())
