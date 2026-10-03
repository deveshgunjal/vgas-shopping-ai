# -*- coding: utf-8 -*-
"""SAM FINAL ENGINE - Real working search"""
import asyncio, sys, re, json, time, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

from price_parser import Price
from bs4 import BeautifulSoup

CURRENCY_INR = {"INR":1,"USD":84,"GBP":107,"EUR":91,"AED":23}

def parse_price(t):
    try:
        p = Price.fromstring(str(t))
        if p.amount: return float(p.amount)
    except: pass
    try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
    except: return 0.0

def aff(url, platform):
    tags = {
        "amazon.in":"tag=vgas-vikasg-21","amazon.com":"tag=vgas-us-21",
        "flipkart.com":"affid=vgas2024","meesho.com":"utm_source=vgas",
        "snapdeal.com":"utm_source=vgas","ebay.com":"campid=vgas",
        "aliexpress.com":"utm_source=vgas","walmart.com":"utm_source=vgas",
    }
    tag = tags.get(platform,"utm_source=vgas")
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{tag}"

async def curl_get(url):
    try:
        from curl_cffi.requests import AsyncSession
        async with AsyncSession(impersonate="chrome124") as s:
            r = await s.get(url, timeout=15, headers={"Accept-Language":"en-IN,en;q=0.9"})
            return r.text
    except: return ""

async def browser_get(url):
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
            r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000,simulate_user=True,magic=True))
            return r.html if r.success else ""
    except: return ""

def parse_amazon(html, platform):
    soup = BeautifulSoup(html,"lxml")
    products = []
    currency = "INR" if "amazon.in" in platform else "USD"
    for card in soup.select("div[data-component-type='s-search-result']")[:6]:
        name_el  = card.select_one("h2 a span")
        price_el = card.select_one("span.a-price-whole")
        link_el  = card.select_one("h2 a")
        img_el   = card.select_one("img.s-image")
        rating_el= card.select_one("span.a-icon-alt")
        if not name_el or not price_el: continue
        price = parse_price(price_el.get_text())
        if price <= 0: continue
        href = link_el["href"] if link_el else ""
        link = f"https://www.{platform}{href}" if not href.startswith("http") else href
        products.append({
            "name": name_el.get_text(strip=True)[:100],
            "price": price, "price_inr": price * CURRENCY_INR.get(currency,1),
            "currency": currency, "store": platform,
            "url": aff(link,platform),
            "image": img_el.get("src","") if img_el else "",
            "rating": parse_price(rating_el.get_text()) if rating_el else 0.0,
        })
    return products

def parse_flipkart(html):
    soup = BeautifulSoup(html,"lxml")
    products = []
    for card in soup.select("div[data-id]")[:6]:
        name_el = card.select_one("div._4rR01T,a.s1Q9rs,div.KzDlHZ,div._2WkVRV")
        # Flipkart 2025 price classes
        price_el = card.select_one("div._1psv1ze2c,div.css-g5y9jx,div._30jeq3")
        link_el  = card.select_one("a[href*='/p/']")
        img_el   = card.select_one("img._396cs4,img.DByuf4")
        if not name_el: continue
        price = parse_price(price_el.get_text()) if price_el else 0.0
        if price <= 0: continue
        href = link_el["href"] if link_el else ""
        link = f"https://www.flipkart.com{href}" if not href.startswith("http") else href
        products.append({
            "name": name_el.get_text(strip=True)[:100],
            "price": price, "price_inr": price,
            "currency": "INR", "store": "flipkart.com",
            "url": aff(link,"flipkart.com"),
            "image": img_el.get("src","") if img_el else "",
        })
    return products

def parse_ebay(html):
    soup = BeautifulSoup(html,"lxml")
    products = []
    for card in soup.select("li.s-item")[:6]:
        name_el  = card.select_one("div.s-item__title")
        price_el = card.select_one("span.s-item__price")
        link_el  = card.select_one("a.s-item__link")
        img_el   = card.select_one("img")
        if not name_el or not price_el: continue
        name = name_el.get_text(strip=True)
        if "Shop on eBay" in name: continue
        price = parse_price(price_el.get_text())
        if price <= 0: continue
        products.append({
            "name": name[:100], "price": price,
            "price_inr": price * 84,
            "currency": "USD", "store": "ebay.com",
            "url": aff(link_el["href"] if link_el else "","ebay.com"),
            "image": img_el.get("src","") if img_el else "",
        })
    return products

def parse_snapdeal(html):
    soup = BeautifulSoup(html,"lxml")
    products = []
    for card in soup.select("li.product-tuple-listing")[:6]:
        name_el  = card.select_one("p.product-title")
        price_el = card.select_one("span.product-price")
        link_el  = card.select_one("a[href]")
        img_el   = card.select_one("img")
        if not name_el or not price_el: continue
        price = parse_price(price_el.get_text())
        if price <= 0: continue
        products.append({
            "name": name_el.get_text(strip=True)[:100],
            "price": price, "price_inr": price,
            "currency": "INR", "store": "snapdeal.com",
            "url": aff(link_el["href"] if link_el else "","snapdeal.com"),
            "image": img_el.get("src","") if img_el else "",
        })
    return products

async def search_all(query):
    """Search all platforms - real working"""
    q = query.replace(" ","+")
    print(f"  Searching: {query}")

    # Run in parallel
    results = await asyncio.gather(
        curl_get(f"https://www.amazon.in/s?k={q}&sort=price-asc-rank"),
        curl_get(f"https://www.amazon.com/s?k={q}&sort=price-asc-rank"),
        browser_get(f"https://www.flipkart.com/search?q={q}&sort=price_asc"),
        curl_get(f"https://www.ebay.com/sch/i.html?_nkw={q}&_sop=15"),
        curl_get(f"https://www.snapdeal.com/search?keyword={q}&sort=rlvncy"),
        return_exceptions=True
    )

    amz_in_html, amz_com_html, fk_html, ebay_html, snap_html = [
        r if isinstance(r,str) else "" for r in results
    ]

    all_products = []
    if amz_in_html:  all_products.extend(parse_amazon(amz_in_html, "amazon.in"))
    if amz_com_html: all_products.extend(parse_amazon(amz_com_html, "amazon.com"))
    if fk_html:      all_products.extend(parse_flipkart(fk_html))
    if ebay_html:    all_products.extend(parse_ebay(ebay_html))
    if snap_html:    all_products.extend(parse_snapdeal(snap_html))

    all_products = [p for p in all_products if p.get("price_inr",0) > 0]
    all_products.sort(key=lambda x: x["price_inr"])
    return all_products

async def main():
    print("SAM FINAL ENGINE - VGAS WORLD LOWEST PRICE")
    print("="*55)

    queries = [
        "iPhone 16 128GB",
        "Samsung Galaxy S24",
        "boAt Airdopes 141",
        "Sony WH-1000XM5",
        "laptop under 50000",
    ]

    all_report = {}
    for query in queries:
        t0 = time.time()
        products = await search_all(query)
        elapsed = time.time()-t0

        print(f"\n  [{query}] - {len(products)} results in {elapsed:.1f}s")
        print(f"  {'STORE':22} {'PRICE':>10} {'INR':>10}  NAME")
        print(f"  {'-'*65}")
        for p in products[:6]:
            sym = {"INR":"Rs","USD":"$","GBP":"£"}.get(p["currency"],"")
            print(f"  {p['store']:22} {sym+str(int(p['price'])):>10} {int(p['price_inr']):>10}  {p['name'][:30]}")

        if products:
            best = products[0]
            print(f"\n  WORLD LOWEST: Rs {best['price_inr']:,.0f} at {best['store']}")
            print(f"  BUY: {best['url'][:65]}")

        all_report[query] = products[:8]

    with open("sam_final_report.json","w",encoding="utf-8") as f:
        json.dump(all_report, f, ensure_ascii=False, indent=2)

    print("\nSAM: Report -> sam_final_report.json")
    print("MISSION COMPLETE")

asyncio.run(main())
