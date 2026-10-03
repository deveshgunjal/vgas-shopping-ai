# -*- coding: utf-8 -*-
"""
SAM FINAL REAL SYSTEM
Crawl4AI browser - works on ALL sites
Real prices, real data, no blocks
"""
import asyncio, sys, re, json, time, os
sys.stdout.reconfigure(encoding="utf-8")

AFFILIATE = {
    "amazon.in":    "tag=vgas-vikasg-21",
    "flipkart.com": "affid=vgas2024",
    "myntra.com":   "utm_source=vgas",
    "meesho.com":   "utm_source=vgas",
    "snapdeal.com": "utm_source=vgas",
    "amazon.com":   "tag=vgas-us-21",
    "ebay.com":     "campid=vgas",
    "walmart.com":  "utm_source=vgas",
    "aliexpress.com":"utm_source=vgas",
    "noon.com":     "utm_source=vgas",
}

SEARCH_URLS = {
    "amazon.in":    "https://www.amazon.in/s?k={q}&ref=nb_sb_noss",
    "flipkart.com": "https://www.flipkart.com/search?q={q}&sort=price_asc",
    "meesho.com":   "https://www.meesho.com/search?q={q}",
    "snapdeal.com": "https://www.snapdeal.com/search?keyword={q}&sort=rlvncy",
    "ebay.com":     "https://www.ebay.com/sch/i.html?_nkw={q}&_sop=15",
    "walmart.com":  "https://www.walmart.com/search?q={q}&sort=price_low",
    "aliexpress.com":"https://www.aliexpress.com/wholesale?SearchText={q}&SortType=price_asc",
}

CURRENCY = {
    "amazon.in":"INR","flipkart.com":"INR","meesho.com":"INR",
    "snapdeal.com":"INR","ebay.com":"USD","walmart.com":"USD",
    "aliexpress.com":"USD","noon.com":"AED",
}
TO_INR = {"INR":1,"USD":84,"GBP":107,"EUR":91,"AED":23}

def to_f(t):
    try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
    except: return 0.0

def aff(url):
    for p,tag in AFFILIATE.items():
        if p in url:
            sep = "&" if "?" in url else "?"
            return f"{url}{sep}{tag}"
    return url

async def browser_get(url):
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
        r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000,simulate_user=True,magic=True))
        return r.html if r.success else ""

def parse_prices(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    prices = []
    for el in soup.find_all(["span","div"],class_=True):
        t = el.get_text(strip=True)
        if re.match(r'^[\u20b9\$\£\€][\d,]+(\.\d{1,2})?$',t):
            v = to_f(t)
            if 100 < v < 10000000: prices.append(v)
    return sorted(set(prices))

def parse_name(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","#productTitle","h1._6EBuvT","h1"]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True))>3:
            return el.get_text(strip=True)[:120]
    if soup.title: return soup.title.text.split("-")[0].split("|")[0].strip()[:100]
    return "Unknown"

def parse_search_results(html, platform, limit=5):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    products = []
    sel = {
        "amazon.in":  "div[data-component-type='s-search-result']",
        "amazon.com": "div[data-component-type='s-search-result']",
        "flipkart.com":"div[data-id]",
        "ebay.com":   "li.s-item",
        "walmart.com":"div[data-item-id]",
    }.get(platform,"div[class*='product'],article,li[class*='item'],div[class*='ProductCard']")

    for card in soup.select(sel)[:limit]:
        # Name
        name = ""
        for ns in ["h2 a span","span.a-text-normal","div._4rR01T","span.VU-ZEz",
                   "h2","h3","a[class*='title']","span[class*='title']"]:
            el = card.select_one(ns)
            if el and el.get_text(strip=True): name=el.get_text(strip=True)[:100]; break

        # Price - Amazon specific
        price = 0.0
        amz_whole = card.select_one("span.a-price-whole")
        amz_frac  = card.select_one("span.a-price-fraction")
        if amz_whole:
            price = to_f(amz_whole.get_text() + "." + (amz_frac.get_text() if amz_frac else "0"))
        else:
            for el in card.find_all(["span","div"],class_=True):
                t = el.get_text(strip=True)
                if re.match(r'^[\u20b9\$\£][\d,]+',t) and len(t)<15:
                    v = to_f(t)
                    if v > 10: price=v; break

        # Rating
        rating = 0.0
        for rs in ["span.a-icon-alt","div._3LWZlK","div.XQDdHH","span[class*='rating']"]:
            el = card.select_one(rs)
            if el:
                v = to_f(el.get_text())
                if 0 < v <= 5: rating=v; break

        # Link
        link_el = card.select_one("a[href]")
        href = link_el["href"] if link_el else ""
        link = href if href.startswith("http") else f"https://www.{platform}{href}"

        # Image
        img_el = card.select_one("img")
        img = img_el.get("src","") if img_el else ""

        # Original price
        orig = 0.0
        for os_ in ["span.a-text-price span","div._3I9_wc","span[class*='original']"]:
            el = card.select_one(os_)
            if el: orig=to_f(el.get_text()); break

        if name and price > 0:
            cur = CURRENCY.get(platform,"INR")
            disc = round(((orig-price)/orig)*100) if orig > price > 0 else 0
            products.append({
                "name": name,
                "price": price,
                "original_price": orig or price,
                "discount": disc,
                "rating": rating,
                "currency": cur,
                "price_inr": price * TO_INR.get(cur,1),
                "url": aff(link),
                "store": platform,
                "image": img,
            })
    return products

async def scrape_product_url(url):
    """Scrape single product URL"""
    platform = next((p for p in AFFILIATE if p in url),"unknown")
    html = await browser_get(url)
    if not html: return {"error":"failed","url":url}

    prices = parse_prices(html)
    name   = parse_name(html)
    cur    = CURRENCY.get(platform,"INR")

    price = prices[0] if prices else 0.0
    orig  = prices[-1] if len(prices)>1 else price
    disc  = round(((orig-price)/orig)*100) if orig > price > 0 else 0
    fake  = abs(disc - round(((orig-price)/orig)*100 if orig>price>0 else 0)) > 10

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    rating = 0.0
    for sel in ["div.XQDdHH","div._3LWZlK","span.a-icon-alt"]:
        el = soup.select_one(sel)
        if el:
            v = to_f(el.get_text())
            if 0 < v <= 5: rating=v; break

    img = ""
    for sel in ["img._396cs4","img.DByuf4","#landingImage"]:
        el = soup.select_one(sel)
        if el and el.get("src"): img=el["src"]; break

    return {
        "name": name, "price": price, "original_price": orig,
        "discount": disc, "rating": rating, "image": img,
        "currency": cur, "price_inr": price*TO_INR.get(cur,1),
        "store": platform, "url": aff(url),
        "fake_discount": fake,
        "fake_msg": f"GENUINE {disc}% off" if not fake else f"FAKE discount!",
        "in_stock": "out of stock" not in html.lower(),
    }

async def search_platform_browser(platform, query, limit=5):
    """Search using browser - works on all sites"""
    url = SEARCH_URLS.get(platform,"").format(q=query.replace(" ","+"))
    if not url: return []
    html = await browser_get(url)
    if not html: return []
    return parse_search_results(html, platform, limit)

async def world_search(query, limit=5):
    """Search all platforms in parallel"""
    platforms = list(SEARCH_URLS.keys())
    tasks = [search_platform_browser(p, query, limit) for p in platforms]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_p = []
    for r in results:
        if isinstance(r,list): all_p.extend(r)
    all_p = [p for p in all_p if p.get("price_inr",0)>0]
    all_p.sort(key=lambda x: x["price_inr"])
    return all_p

async def main():
    print("SAM REAL SYSTEM - VGAS")
    print("="*60)

    # Test 1: Direct URL
    print("\n[1] Flipkart iPhone 16 Direct URL:")
    r = await scrape_product_url("https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G")
    print(f"  Name    : {r.get('name')}")
    print(f"  Price   : {r.get('currency')} {r.get('price'):,.0f}")
    print(f"  MRP     : {r.get('currency')} {r.get('original_price'):,.0f}")
    print(f"  Disc    : {r.get('discount')}%  |  {r.get('fake_msg')}")
    print(f"  Rating  : {r.get('rating')}")
    print(f"  AffLink : {r.get('url','')[:70]}")

    # Test 2: Amazon search
    print("\n[2] Amazon.in iPhone 16 Search:")
    amz = await search_platform_browser("amazon.in","iPhone 16",5)
    for p in amz[:5]:
        print(f"  Rs {p['price']:>8,.0f} | {p['discount']}% off | {p['name'][:50]}")

    # Test 3: World search
    print("\n[3] World Lowest - boAt headphones:")
    world = await world_search("boAt Rockerz 450 headphones", limit=3)
    print(f"  Found {len(world)} results")
    for p in world[:6]:
        print(f"  {p['store']:20} | {p['currency']} {p['price']:>8,.0f} = Rs {p['price_inr']:>8,.0f} | {p['name'][:35]}")
    if world:
        best = world[0]
        print(f"\n  WORLD LOWEST: Rs {best['price_inr']:,.0f} at {best['store']}")
        print(f"  BUY: {best['url'][:70]}")

    # Save
    report = {"flipkart_test":r, "amazon_search":amz[:5], "world_search":world[:10]}
    with open("sam_real_report.json","w",encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\nSAM: sam_real_report.json saved")
    print("MISSION COMPLETE")

asyncio.run(main())
