# -*- coding: utf-8 -*-
"""
SAM ULTIMATE VGAS ENGINE
Tools: curl_cffi (bot bypass) + price_parser + crawl4ai + beautifulsoup
Platforms: Amazon, Flipkart, Meesho, Snapdeal, eBay, AliExpress + more
Real working. No placeholders.
"""
import asyncio, sys, re, json, time, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from price_parser import Price
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

AFFILIATE = {
    "amazon.in":     "tag=vgas-vikasg-21",
    "amazon.com":    "tag=vgas-us-21",
    "amazon.co.uk":  "tag=vgas-uk-21",
    "amazon.de":     "tag=vgas-de-21",
    "amazon.ae":     "tag=vgas-ae-21",
    "flipkart.com":  "affid=vgas2024&affExtParam1=VGAS",
    "myntra.com":    "utm_source=vgas",
    "ajio.com":      "utm_source=vgas",
    "meesho.com":    "utm_source=vgas",
    "snapdeal.com":  "utm_source=vgas",
    "tatacliq.com":  "utm_source=vgas",
    "croma.com":     "utm_source=vgas",
    "nykaa.com":     "utm_source=vgas",
    "reliancedigital.in": "utm_source=vgas",
    "walmart.com":   "utm_source=vgas",
    "ebay.com":      "campid=vgas",
    "aliexpress.com":"utm_source=vgas",
    "noon.com":      "utm_source=vgas",
    "bestbuy.com":   "utm_source=vgas",
}

SEARCH_URLS = {
    "amazon.in":     "https://www.amazon.in/s?k={q}&ref=sr_st_price-asc-rank&sort=price-asc-rank",
    "flipkart.com":  "https://www.flipkart.com/search?q={q}&sort=price_asc",
    "meesho.com":    "https://www.meesho.com/search?q={q}",
    "snapdeal.com":  "https://www.snapdeal.com/search?keyword={q}&sort=rlvncy",
    "amazon.com":    "https://www.amazon.com/s?k={q}&sort=price-asc-rank",
    "ebay.com":      "https://www.ebay.com/sch/i.html?_nkw={q}&_sop=15",
    "aliexpress.com":"https://www.aliexpress.com/wholesale?SearchText={q}&SortType=price_asc",
    "walmart.com":   "https://www.walmart.com/search?q={q}&sort=price_low",
    "amazon.co.uk":  "https://www.amazon.co.uk/s?k={q}&sort=price-asc-rank",
}

CURRENCY_INR = {"INR":1,"USD":84,"GBP":107,"EUR":91,"AED":23,"CNY":12}
CURRENCY_SYMBOL = {"INR":"₹","USD":"$","GBP":"£","EUR":"€","AED":"AED","CNY":"¥"}
PLATFORM_CURRENCY = {
    "amazon.in":"INR","flipkart.com":"INR","meesho.com":"INR","snapdeal.com":"INR",
    "myntra.com":"INR","ajio.com":"INR","tatacliq.com":"INR","croma.com":"INR",
    "nykaa.com":"INR","reliancedigital.in":"INR",
    "amazon.com":"USD","walmart.com":"USD","ebay.com":"USD","bestbuy.com":"USD",
    "aliexpress.com":"USD","amazon.co.uk":"GBP","amazon.de":"EUR","noon.com":"AED","amazon.ae":"AED",
}

def aff(url, platform):
    tag = AFFILIATE.get(platform,"utm_source=vgas")
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{tag}"

def get_platform(url):
    for p in AFFILIATE:
        if p in url: return p
    return "unknown"

def parse_price(text):
    """price_parser - GitHub top library, handles all formats"""
    try:
        p = Price.fromstring(str(text))
        if p.amount: return float(p.amount)
    except: pass
    try: return float(re.sub(r"[^\d.]","",str(text)) or 0)
    except: return 0.0

async def curl_get(url, mobile=False):
    """curl_cffi - impersonates real Chrome, bypasses bot detection"""
    try:
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit/605.1.15 Mobile/15E148" if mobile else None
        async with AsyncSession(impersonate="chrome124") as s:
            r = await s.get(url, timeout=15, headers={"Accept-Language":"en-IN,en;q=0.9"} | ({"User-Agent":ua} if ua else {}))
            return r.text
    except: return ""

async def browser_get(url):
    """Crawl4AI - for JS heavy sites"""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
            r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000,simulate_user=True,magic=True))
            return r.html if r.success else ""
    except: return ""

def extract_product(html, url):
    """Smart extraction with price_parser"""
    soup = BeautifulSoup(html, "lxml")
    platform = get_platform(url)
    currency = PLATFORM_CURRENCY.get(platform, "INR")

    # NAME
    name = ""
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","#productTitle","h1._6EBuvT",
                "h1.x-item-title__mainTitle span","h1"]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 3:
            name = el.get_text(strip=True)[:150]; break
    if not name and soup.title:
        name = soup.title.text.split("-")[0].split("|")[0].strip()[:150]

    # PRICE using price_parser on all elements
    all_prices = []
    for el in soup.find_all(["span","div"], class_=True):
        t = el.get_text(strip=True)
        if any(s in t for s in ["₹","$","£","€","AED"]) and len(t) < 20:
            # Only pure price - no prefix words
            if re.match(r'^[\u20b9\$\£\€AED\s]*[\d,]+(\.\d{1,2})?$', t.strip()):
                v = parse_price(t)
                if 50 < v < 50000000: all_prices.append(v)

    all_prices = sorted(set(all_prices))
    price = all_prices[0] if all_prices else 0.0
    orig  = all_prices[-1] if len(all_prices) > 1 else price

    # DISCOUNT
    disc = 0
    for sel in ["div.UkUFwK span","div._3Ay6Sb span","span.savingsPercentage",
                "td.a-span12 span.a-color-price","span.a-color-price"]:
        el = soup.select_one(sel)
        if el:
            d = int(re.sub(r"[^\d]","",el.get_text()) or 0)
            if 0 < d < 100: disc = d; break
    if not disc and orig > price > 0:
        disc = round(((orig-price)/orig)*100)

    # RATING
    rating = 0.0
    for sel in ["div.XQDdHH","div._3LWZlK","span.a-icon-alt","div.ipqd2A",
                "span[class*='rating']","div[class*='rating']"]:
        el = soup.select_one(sel)
        if el:
            v = parse_price(el.get_text())
            if 0 < v <= 5: rating = round(v,1); break

    # IMAGE
    img = ""
    for sel in ["img._396cs4","img.DByuf4","#landingImage","img.s-image",
                "img[data-old-hires]","img.img-fluid"]:
        el = soup.select_one(sel)
        if el:
            img = el.get("data-old-hires") or el.get("src",""); break

    # SPECS
    specs = {}
    for row in soup.select("tr._1s_Smc,tr.WJdYP6,tr.a-spacing-small")[:15]:
        k = row.select_one("td:first-child,th")
        v = row.select_one("td:last-child")
        if k and v and k.get_text(strip=True) != v.get_text(strip=True):
            specs[k.get_text(strip=True)[:40]] = v.get_text(strip=True)[:100]

    # BANK OFFERS
    bank_offers = []
    for bank in ["HDFC","SBI","ICICI","Axis","Kotak","IDFC","RBL"]:
        if bank in html:
            idx = html.find(bank)
            ctx = BeautifulSoup(html[max(0,idx-30):idx+200],"lxml").get_text()
            m = re.search(r'(\d+%\s*(?:off|instant|cashback)|flat\s*[\u20b9Rs\.]*[\d,]+\s*off)', ctx, re.I)
            if m: bank_offers.append(f"{bank}: {m.group()}")

    # FAKE DISCOUNT
    fake = False; fake_msg = "Cannot verify"
    if orig > price > 0:
        actual = round(((orig-price)/orig)*100)
        fake = abs(actual-disc) > 10
        fake_msg = f"FAKE! Claimed {disc}% actual {actual}%" if fake else f"GENUINE {actual}% off"

    price_inr = price * CURRENCY_INR.get(currency,1)

    return {
        "name": name or "Unknown",
        "price": price, "original_price": orig,
        "discount": disc, "rating": rating, "image": img,
        "currency": currency, "price_inr": price_inr,
        "store": platform, "url": aff(url,platform),
        "fake_discount": fake, "fake_discount_msg": fake_msg,
        "bank_offers": bank_offers, "specs": specs,
        "in_stock": "out of stock" not in html.lower(),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

async def scrape_product_url(url):
    """Scrape any product URL"""
    platform = get_platform(url)
    needs_browser = any(p in url for p in ["flipkart","meesho","ajio","myntra","noon"])

    # Try curl_cffi first (fastest, best bot bypass)
    html = await curl_get(url)
    result = extract_product(html, url) if html else {}

    # If price missing, try browser
    if not result.get("price") or needs_browser:
        html = await browser_get(url)
        if html: result = extract_product(html, url)

    return result

async def search_one(platform, query, limit=5):
    """Search one platform"""
    if platform not in SEARCH_URLS: return []
    url = SEARCH_URLS[platform].format(q=query.replace(" ","+"))
    currency = PLATFORM_CURRENCY.get(platform,"INR")

    # curl_cffi for Amazon (best), browser for Flipkart
    html = await browser_get(url) if "flipkart" in platform else await curl_get(url)
    if not html: html = await curl_get(url)
    if not html: return []

    soup = BeautifulSoup(html,"lxml")
    products = []

    CARD_SEL = {
        "amazon.in":    "div[data-component-type='s-search-result']",
        "amazon.com":   "div[data-component-type='s-search-result']",
        "amazon.co.uk": "div[data-component-type='s-search-result']",
        "flipkart.com": "div[data-id]",
        "ebay.com":     "li.s-item",
        "walmart.com":  "div[data-item-id]",
        "aliexpress.com":"div[class*='product']",
        "meesho.com":   "div[class*='ProductList']",
        "snapdeal.com": "li.product-tuple-listing",
    }
    NAME_SEL = {
        "amazon.in":  "h2 a span",
        "amazon.com": "h2 a span",
        "flipkart.com":"div._4rR01T,a.s1Q9rs,div.KzDlHZ",
        "ebay.com":   "div.s-item__title",
        "walmart.com":"span[class*='product-title']",
        "snapdeal.com":"p.product-title",
    }
    PRICE_SEL = {
        "amazon.in":  "span.a-price-whole",
        "amazon.com": "span.a-price-whole",
        "flipkart.com":"div._1psv1ze2c,div.css-g5y9jx",
        "ebay.com":   "span.s-item__price",
        "walmart.com":"div[class*='price-main']",
        "snapdeal.com":"span.product-price",
    }

    card_sel  = CARD_SEL.get(platform,"div[class*='product'],article,li")
    name_sel  = NAME_SEL.get(platform,"h2,h3,a[class*='title']")
    price_sel = PRICE_SEL.get(platform,"span[class*='price'],div[class*='price']")

    for card in soup.select(card_sel)[:limit]:
        name_el  = card.select_one(name_sel)
        price_el = card.select_one(price_sel)
        link_el  = card.select_one("a[href]")
        img_el   = card.select_one("img")

        name  = name_el.get_text(strip=True)[:100] if name_el else ""
        price = parse_price(price_el.get_text()) if price_el else 0.0
        href  = link_el["href"] if link_el else ""
        link  = href if href.startswith("http") else f"https://www.{platform}{href}"
        img   = img_el.get("src","") if img_el else ""

        if name and price > 0:
            products.append({
                "name": name, "price": price,
                "price_inr": price * CURRENCY_INR.get(currency,1),
                "currency": currency,
                "url": aff(link,platform),
                "store": platform, "image": img,
            })
    return products

async def world_lowest_price(query, limit=5):
    """Search ALL platforms in parallel - find world lowest"""
    print(f"\nSAM: '{query}' - सगळ्या platforms वर search करतो...")
    t0 = time.time()

    tasks = [search_one(p, query, limit) for p in SEARCH_URLS]
    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    products = []
    for r in all_results:
        if isinstance(r, list): products.extend(r)

    products = [p for p in products if p.get("price_inr",0) > 0]
    products.sort(key=lambda x: x["price_inr"])

    elapsed = time.time()-t0
    print(f"  {len(products)} results | {elapsed:.1f}s")
    print(f"\n  {'STORE':22} {'PRICE':>12} {'INR':>10}  NAME")
    print(f"  {'-'*70}")
    for p in products[:10]:
        sym = CURRENCY_SYMBOL.get(p["currency"],"")
        print(f"  {p['store']:22} {sym+str(int(p['price'])):>12} {int(p['price_inr']):>10}  {p['name'][:35]}")

    if products:
        best = products[0]
        print(f"\n  WORLD LOWEST: {CURRENCY_SYMBOL.get(best['currency'],'')}{best['price']:,.0f} = Rs {best['price_inr']:,.0f}")
        print(f"  STORE       : {best['store']}")
        print(f"  BUY LINK    : {best['url'][:70]}")

    return products

async def main():
    print("SAM ULTIMATE VGAS ENGINE - REAL WORKING")
    print("="*55)

    # TEST 1: URL scrape
    print("\n[TEST 1] Flipkart iPhone 16 URL...")
    r = await scrape_product_url("https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G")
    print(f"  Name    : {r.get('name','?')}")
    print(f"  Price   : Rs {r.get('price',0):,.0f}")
    print(f"  MRP     : Rs {r.get('original_price',0):,.0f}")
    print(f"  Disc    : {r.get('discount',0)}%")
    print(f"  Fake    : {r.get('fake_discount_msg','?')}")
    print(f"  Bank    : {r.get('bank_offers',[])}")
    print(f"  Specs   : {len(r.get('specs',{}))} items")

    # TEST 2: World search - multiple products
    queries = ["iPhone 16 128GB", "Samsung Galaxy S24", "boAt Airdopes 141", "Nike Air Max 270", "laptop under 50000"]
    all_data = {}
    for q in queries:
        results = await world_lowest_price(q, limit=4)
        all_data[q] = results[:8]

    # Save report
    with open("sam_ultimate_report.json","w",encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("\nSAM: Report saved -> sam_ultimate_report.json")
    print("SAM ULTIMATE: MISSION COMPLETE")

asyncio.run(main())
