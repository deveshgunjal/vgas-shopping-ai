# -*- coding: utf-8 -*-
"""
VGAS WORLD PRICE ENGINE v3.0
SAM + Swarm Army - Every trick, hack, tech combined
Master: Vikas Gunjal
"""
import asyncio, sys, re, json, ssl, time, os, hashlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

# ============================================================
# HACK 1: Rotate User Agents (anti-bot bypass)
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
]

# ============================================================
# HACK 2: Free Proxy APIs (no cost)
# ============================================================
FREE_PRICE_APIS = {
    # Google Shopping (free scrape)
    "google_shopping": "https://www.google.com/search?q={q}+buy+price&tbm=shop",
    # DuckDuckGo shopping
    "duckduckgo": "https://duckduckgo.com/?q={q}+lowest+price&ia=shopping",
    # PriceRunner (free)
    "pricerunner": "https://www.pricerunner.com/search?q={q}",
    # Shopzilla
    "shopzilla": "https://www.shopzilla.com/search?keyword={q}",
}

# ============================================================
# WORLD PLATFORMS
# ============================================================
PLATFORMS = {
    # INDIA - All major
    "amazon.in":      {"s": "https://www.amazon.in/s?k={q}&sort=price-asc-rank", "cur": "INR", "aff": "tag=vgas-vikasg-21"},
    "flipkart.com":   {"s": "https://www.flipkart.com/search?q={q}&sort=price_asc", "cur": "INR", "aff": "affid=vgas2024"},
    "myntra.com":     {"s": "https://www.myntra.com/{q}?sort=price_asc", "cur": "INR", "aff": "utm_source=vgas"},
    "ajio.com":       {"s": "https://www.ajio.com/search/?text={q}&sortby=price&orderby=asc", "cur": "INR", "aff": "utm_source=vgas"},
    "meesho.com":     {"s": "https://www.meesho.com/search?q={q}", "cur": "INR", "aff": "utm_source=vgas"},
    "snapdeal.com":   {"s": "https://www.snapdeal.com/search?keyword={q}&sort=rlvncy", "cur": "INR", "aff": "utm_source=vgas"},
    "tatacliq.com":   {"s": "https://www.tatacliq.com/search/?searchCategory=all&text={q}", "cur": "INR", "aff": "utm_source=vgas"},
    "croma.com":      {"s": "https://www.croma.com/searchB?q={q}", "cur": "INR", "aff": "utm_source=vgas"},
    "nykaa.com":      {"s": "https://www.nykaa.com/search/result/?q={q}", "cur": "INR", "aff": "utm_source=vgas"},
    "reliancedigital.in": {"s": "https://www.reliancedigital.in/search?q={q}", "cur": "INR", "aff": "utm_source=vgas"},
    # USA
    "amazon.com":     {"s": "https://www.amazon.com/s?k={q}&sort=price-asc-rank", "cur": "USD", "aff": "tag=vgas-us-21"},
    "walmart.com":    {"s": "https://www.walmart.com/search?q={q}&sort=price_low", "cur": "USD", "aff": "utm_source=vgas"},
    "ebay.com":       {"s": "https://www.ebay.com/sch/i.html?_nkw={q}&_sop=15", "cur": "USD", "aff": "campid=vgas"},
    "bestbuy.com":    {"s": "https://www.bestbuy.com/site/searchpage.jsp?st={q}", "cur": "USD", "aff": "utm_source=vgas"},
    "newegg.com":     {"s": "https://www.newegg.com/p/pl?d={q}&Order=1", "cur": "USD", "aff": "utm_source=vgas"},
    # GLOBAL
    "aliexpress.com": {"s": "https://www.aliexpress.com/wholesale?SearchText={q}&SortType=price_asc", "cur": "USD", "aff": "utm_source=vgas"},
    "amazon.co.uk":   {"s": "https://www.amazon.co.uk/s?k={q}&sort=price-asc-rank", "cur": "GBP", "aff": "tag=vgas-uk-21"},
    "amazon.de":      {"s": "https://www.amazon.de/s?k={q}&sort=price-asc-rank", "cur": "EUR", "aff": "tag=vgas-de-21"},
    "amazon.ae":      {"s": "https://www.amazon.ae/s?k={q}&sort=price-asc-rank", "cur": "AED", "aff": "tag=vgas-ae-21"},
    "noon.com":       {"s": "https://www.noon.com/uae-en/search/?q={q}&sort%5Bby%5D=price&sort%5Bdir%5D=asc", "cur": "AED", "aff": "utm_source=vgas"},
}

INR_RATE = {"INR":1,"USD":84,"GBP":107,"EUR":91,"AED":23,"CAD":62,"AUD":55,"SGD":63,"JPY":0.56}

# ============================================================
# HACK 3: Smart Cache with TTL
# ============================================================
_cache = {}
def cache_get(k):
    if k in _cache and time.time()-_cache[k][1] < 3600: return _cache[k][0]
def cache_set(k, v): _cache[k] = (v, time.time())

# ============================================================
# HACK 4: Rotating headers
# ============================================================
import random
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

# ============================================================
# HACK 5: Smart HTTP with retry + SSL bypass
# ============================================================
async def http_get(url, retries=2):
    import aiohttp
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for i in range(retries):
        try:
            async with aiohttp.ClientSession(headers=get_headers()) as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=10), ssl=ctx, allow_redirects=True) as r:
                    if r.status == 200:
                        return await r.text()
                    elif r.status == 503 and i < retries-1:
                        await asyncio.sleep(1)
        except: pass
    return ""

# ============================================================
# HACK 6: Browser scrape with stealth
# ============================================================
async def browser_get(url):
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        cfg  = BrowserConfig(headless=True, verbose=False,
                             extra_args=["--disable-blink-features=AutomationControlled",
                                        "--no-sandbox","--disable-dev-shm-usage"])
        rcfg = CrawlerRunConfig(page_timeout=25000, simulate_user=True, magic=True)
        async with AsyncWebCrawler(config=cfg) as c:
            r = await c.arun(url=url, config=rcfg)
            return r.html if r.success else ""
    except: return ""

# ============================================================
# HACK 7: AI extraction with Mistral (no CSS selectors needed)
# ============================================================
async def ai_extract(url):
    try:
        import httpx
        html = await browser_get(url)
        if not html: return {}
        from bs4 import BeautifulSoup
        text = BeautifulSoup(html,"lxml").get_text()[:3000]
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": "Bearer r0x1j7Wno0qepHVo8wGImgSjctgkabdQ"},
                json={
                    "model": "mistral-small-latest",
                    "messages": [{"role":"user","content":
                        f"Extract from this product page text. Return JSON only:\n"
                        f"{{name, price_number, original_price_number, discount_percent, rating, in_stock}}\n\n{text}"
                    }],
                    "temperature": 0
                }, timeout=15
            )
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match: return json.loads(match.group())
    except: pass
    return {}

# ============================================================
# CORE: Parse HTML for prices
# ============================================================
def parse_html(html, currency="INR"):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # Name
    name = ""
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","#productTitle","h1._6EBuvT","h1"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and len(t) > 3: name = t[:150]; break
    if not name and soup.title:
        name = soup.title.text.split("-")[0].split("|")[0].strip()

    # HACK: Pure price regex - only clean numbers with currency symbol
    syms = {"INR":"\u20b9","USD":"\\$","GBP":"\u00a3","EUR":"\u20ac","AED":"AED"}
    sym = syms.get(currency, "\u20b9")
    prices = []
    for el in soup.find_all(["span","div","p"], class_=True):
        t = el.get_text(strip=True)
        if re.match(rf'^{sym}[\d,]+(\.\d{{1,2}})?$', t):
            v = float(re.sub(r"[^\d.]","",t) or 0)
            if v > 0: prices.append(v)
    prices = sorted(set(prices))

    price = prices[0] if prices else 0.0
    orig  = prices[-1] if len(prices)>1 else price

    # Discount
    disc = 0
    for sel in ["div.UkUFwK span","div._3Ay6Sb span","span.savingsPercentage","[class*='discount']","[class*='saving']"]:
        el = soup.select_one(sel)
        if el:
            disc = int(re.sub(r"[^\d]","",el.get_text()) or 0); break
    if not disc and orig > price > 0:
        disc = round(((orig-price)/orig)*100)

    # Rating
    rating = 0.0
    for sel in ["div.XQDdHH","div._3LWZlK","span.a-icon-alt","div.ipqd2A"]:
        el = soup.select_one(sel)
        if el:
            v = float(re.sub(r"[^\d.]","",el.get_text()) or 0)
            if 0 < v <= 5: rating = v; break

    # Image
    img = ""
    for sel in ["img._396cs4","img.DByuf4","#landingImage","img.s-image"]:
        el = soup.select_one(sel)
        if el: img = el.get("data-old-hires") or el.get("src",""); break

    # Specs
    specs = {}
    for row in soup.select("tr._1s_Smc,tr.WJdYP6,tr")[:20]:
        k = row.select_one("td:first-child")
        v = row.select_one("td:last-child")
        if k and v and k.get_text(strip=True) != v.get_text(strip=True):
            specs[k.get_text(strip=True)[:30]] = v.get_text(strip=True)[:50]

    # Fake discount
    fake = False; fake_msg = "Cannot verify"
    if orig > price > 0:
        actual = round(((orig-price)/orig)*100)
        fake = abs(actual-disc) > 10
        fake_msg = f"FAKE! Claimed {disc}% actual {actual}%" if fake else f"GENUINE {actual}% off"

    return {
        "name": name or "Unknown", "price": price, "original_price": orig,
        "discount_percentage": disc, "rating": rating, "image": img,
        "specs": specs, "fake_discount": fake, "fake_discount_msg": fake_msg,
        "in_stock": not bool(soup.select_one("[class*='out-of-stock'],[class*='OutOfStock']")),
    }

# ============================================================
# MAIN: Scrape any URL
# ============================================================
async def scrape_url(url):
    key = hashlib.md5(url.encode()).hexdigest()
    cached = cache_get(key)
    if cached: return {**cached, "cached": True}

    platform = next((p for p in PLATFORMS if p in url), "unknown")
    currency = PLATFORMS.get(platform,{}).get("cur","INR")
    needs_browser = any(p in url for p in ["flipkart","meesho","ajio","myntra","noon"])

    html = await browser_get(url) if needs_browser else await http_get(url)
    if not html: html = await browser_get(url)
    if not html: return {"error":"Cannot fetch","url":url}

    result = parse_html(html, currency)

    # If AI needed (price still 0)
    if result["price"] == 0:
        ai = await ai_extract(url)
        if ai:
            result["price"] = float(ai.get("price_number",0) or 0)
            result["original_price"] = float(ai.get("original_price_number",0) or result["price"])
            result["discount_percentage"] = int(ai.get("discount_percent",0) or 0)
            result["rating"] = float(ai.get("rating",0) or 0)
            result["name"] = ai.get("name","") or result["name"]

    aff_tag = PLATFORMS.get(platform,{}).get("aff","")
    sep = "&" if "?" in url else "?"
    result.update({
        "url": url,
        "affiliate_url": f"{url}{sep}{aff_tag}&vgas=1" if aff_tag else url,
        "store": platform, "currency": currency,
        "price_inr": result["price"] * INR_RATE.get(currency,1),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cached": False,
    })
    if result["price"] > 0: cache_set(key, result)
    return result

# ============================================================
# MAIN: Search all platforms
# ============================================================
async def search_platform(platform, query, limit=5):
    cfg = PLATFORMS.get(platform)
    if not cfg: return []
    url = cfg["s"].format(q=query.replace(" ","+"))
    html = await http_get(url)
    if not html: return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    products = []

    CARD_SEL = {
        "amazon.in":"div[data-component-type='s-search-result']",
        "amazon.com":"div[data-component-type='s-search-result']",
        "amazon.co.uk":"div[data-component-type='s-search-result']",
        "amazon.de":"div[data-component-type='s-search-result']",
        "amazon.ae":"div[data-component-type='s-search-result']",
        "flipkart.com":"div[data-id]",
        "ebay.com":"li.s-item",
        "ebay.co.uk":"li.s-item",
    }
    sel = CARD_SEL.get(platform,"div[class*='product'],article,li[class*='item']")
    sym = {"INR":"\u20b9","USD":"$","GBP":"\u00a3","EUR":"\u20ac"}.get(cfg["cur"],"\u20b9")

    for card in soup.select(sel)[:limit]:
        name = ""
        for ns in ["h2 a span","div._4rR01T","span.VU-ZEz","h2","h3","a[class*='title']","span[class*='title']"]:
            el = card.select_one(ns)
            if el and el.get_text(strip=True): name = el.get_text(strip=True)[:100]; break

        price = 0.0
        for el in card.find_all(["span","div"], class_=True):
            t = el.get_text(strip=True)
            if re.match(rf'^[{sym}\$\u20b9\u00a3\u20ac][\d,]+', t) and len(t)<15:
                v = float(re.sub(r"[^\d.]","",t) or 0)
                if v > 10: price = v; break

        link_el = card.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        link = href if href.startswith("http") else f"https://www.{platform}{href}"
        aff_tag = cfg.get("aff","")
        sep = "&" if "?" in link else "?"
        aff_link = f"{link}{sep}{aff_tag}&vgas=1" if aff_tag and link else link

        img_el = card.select_one("img")
        img = img_el.get("src","") if img_el else ""

        if name and price > 0:
            products.append({
                "name": name, "price": price,
                "price_inr": price * INR_RATE.get(cfg["cur"],1),
                "currency": cfg["cur"], "url": aff_link,
                "store": platform, "image": img,
            })
    return products

async def world_search(query, limit=5):
    """All platforms parallel - fastest possible"""
    tasks = [search_platform(p, query, limit) for p in PLATFORMS]
    all_results = await asyncio.gather(*tasks, return_exceptions=True)
    products = []
    for r in all_results:
        if isinstance(r, list): products.extend(r)
    valid = [p for p in products if p.get("price_inr",0) > 0]
    valid.sort(key=lambda x: x["price_inr"])
    return valid

# ============================================================
# PRICE HISTORY
# ============================================================
def save_history(name, price, store, currency):
    f = "price_history.json"
    h = json.load(open(f,encoding="utf-8")) if os.path.exists(f) else {}
    k = name[:50]
    h.setdefault(k,[]).append({"price":price,"store":store,"currency":currency,"date":time.strftime("%Y-%m-%d %H:%M")})
    h[k] = h[k][-50:]
    json.dump(h, open(f,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

# ============================================================
# SAM TEST
# ============================================================
async def main():
    print("VGAS WORLD PRICE ENGINE v3.0 - SAM SWARM ARMY")
    print("="*55)

    # Test 1: Flipkart URL
    print("\n[1] Flipkart iPhone 16...")
    r = await scrape_url("https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G")
    print(f"  Name     : {r.get('name')}")
    print(f"  Price    : {r.get('currency')} {r.get('price'):,.0f}")
    print(f"  MRP      : {r.get('currency')} {r.get('original_price'):,.0f}")
    print(f"  Discount : {r.get('discount_percentage')}%")
    print(f"  Fake     : {r.get('fake_discount_msg')}")
    print(f"  Rating   : {r.get('rating')}")
    print(f"  Specs    : {len(r.get('specs',{}))} items")
    print(f"  Aff URL  : {r.get('affiliate_url','')[:65]}")
    if r.get("name"): save_history(r["name"], r.get("price",0), r.get("store",""), r.get("currency",""))

    # Test 2: World search
    print("\n[2] World Search: iPhone 16...")
    t0 = time.time()
    results = await world_search("iPhone 16", limit=3)
    print(f"  {len(results)} results in {time.time()-t0:.1f}s")
    print(f"\n  {'STORE':22} {'PRICE':>10} {'=INR':>10}  NAME")
    print(f"  {'-'*65}")
    for item in results[:8]:
        print(f"  {item['store']:22} {item['currency']+str(int(item['price'])):>10} {int(item['price_inr']):>10}  {item['name'][:30]}")

    if results:
        best = results[0]
        print(f"\n  WORLD LOWEST : {best['currency']} {best['price']:,.0f} = Rs {best['price_inr']:,.0f}")
        print(f"  STORE        : {best['store']}")
        print(f"  BUY NOW      : {best['url'][:70]}")

    # Save report
    report = {"flipkart": r, "world_top10": results[:10], "platforms": len(PLATFORMS), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    json.dump(report, open("vgas_report.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nSAM: vgas_report.json saved")
    print("MISSION COMPLETE")

asyncio.run(main())
