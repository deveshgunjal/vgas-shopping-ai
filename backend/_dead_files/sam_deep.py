# -*- coding: utf-8 -*-
"""
SAM DEEP ORDER - VGAS COMPLETE SYSTEM
Layer 1: Google Shopping + DuckDuckGo (no block, free)
Layer 2: Cashback + Coupons + Bank Offers
Layer 3: Real Web UI update
Token saving: minimal, direct, real only
"""
import asyncio, sys, re, ssl, json, time, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

HEADERS_MOBILE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    "Accept-Language": "en-IN,en;q=0.9",
}
HEADERS_DESKTOP = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}

def to_f(t):
    try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
    except: return 0.0

async def http_get(url, mobile=False):
    try:
        import aiohttp
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        h = HEADERS_MOBILE if mobile else HEADERS_DESKTOP
        async with aiohttp.ClientSession(headers=h) as s:
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

# ============================================================
# LAYER 1: GOOGLE SHOPPING - Best free source
# ============================================================
async def google_shopping(query):
    """Google Shopping - shows prices from ALL stores"""
    url = f"https://www.google.com/search?q={query.replace(' ','+')}+buy+online+india&tbm=shop"
    html = await http_get(url)
    if not html: html = await browser_get(url)
    if not html: return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    products = []

    # Google Shopping result cards
    for card in soup.select("div.sh-dgr__grid-result, div.KZmu8e, div.i0X6df")[:10]:
        name_el = card.select_one("h3, div.tAxDx, div.EI11Pd")
        price_el = card.select_one("span.a8Pemb, div.kHxwFf span, span.T14wmb")
        store_el = card.select_one("div.aULzUe, span.E5ocAb, div.IuHnof")
        link_el  = card.select_one("a[href]")

        if name_el and price_el:
            price_text = price_el.get_text(strip=True)
            price = to_f(price_text)
            products.append({
                "name": name_el.get_text(strip=True)[:100],
                "price": price,
                "price_inr": price,
                "currency": "INR",
                "store": store_el.get_text(strip=True) if store_el else "Google Shopping",
                "url": "https://www.google.com" + link_el["href"] if link_el else "",
                "source": "google_shopping",
            })
    return products

# ============================================================
# LAYER 2: DUCKDUCKGO SHOPPING - No bot detection
# ============================================================
async def ddg_shopping(query):
    """DuckDuckGo - no bot detection, free"""
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddg:
            for r in ddg.shopping(query, max_results=10):
                price = to_f(str(r.get("price","0")))
                results.append({
                    "name": r.get("title","")[:100],
                    "price": price,
                    "price_inr": price,
                    "currency": "INR",
                    "store": r.get("merchant","") or r.get("source",""),
                    "url": r.get("url",""),
                    "image": r.get("image",""),
                    "rating": to_f(str(r.get("rating","0"))),
                    "source": "duckduckgo",
                })
        return results
    except Exception as e:
        return []

# ============================================================
# LAYER 3: CASHBACK SITES
# ============================================================
async def cashkaro_deals(query):
    """CashKaro - extra cashback on top of discount"""
    url = f"https://cashkaro.com/search?q={query.replace(' ','+')}"
    html = await http_get(url)
    if not html: return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    deals = []
    for card in soup.select("div.store-card, div.deal-card, div[class*='product']")[:5]:
        name_el = card.select_one("h3,h4,div[class*='title'],a[class*='title']")
        cashback_el = card.select_one("div[class*='cashback'],span[class*='cashback']")
        link_el = card.select_one("a[href]")
        if name_el:
            deals.append({
                "name": name_el.get_text(strip=True)[:80],
                "cashback": cashback_el.get_text(strip=True) if cashback_el else "Up to 10%",
                "url": "https://cashkaro.com" + link_el["href"] if link_el and not link_el["href"].startswith("http") else (link_el["href"] if link_el else ""),
                "source": "cashkaro",
            })
    return deals

async def gopaise_deals(query):
    """GoPaisa - another cashback source"""
    url = f"https://www.gopaisa.com/search?q={query.replace(' ','+')}"
    html = await http_get(url)
    if not html: return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    deals = []
    for card in soup.select("div[class*='deal'],div[class*='product'],div[class*='offer']")[:5]:
        name_el = card.select_one("h3,h4,a,div[class*='title']")
        cb_el = card.select_one("[class*='cashback'],[class*='earn']")
        link_el = card.select_one("a[href]")
        if name_el:
            deals.append({
                "name": name_el.get_text(strip=True)[:80],
                "cashback": cb_el.get_text(strip=True) if cb_el else "",
                "url": link_el["href"] if link_el else "",
                "source": "gopaisa",
            })
    return deals

# ============================================================
# LAYER 4: COUPON SITES
# ============================================================
async def coupondunia_coupons(store):
    """CouponDunia - free coupons for extra discount"""
    url = f"https://coupondunia.in/{store.replace('.com','').replace('.in','')}"
    html = await http_get(url)
    if not html: return []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    coupons = []
    for card in soup.select("div.coupon-code, div[class*='coupon'], div[class*='offer']")[:5]:
        code_el = card.select_one("[class*='code'],button[class*='code']")
        desc_el = card.select_one("div[class*='desc'],p,h3")
        if desc_el:
            coupons.append({
                "code": code_el.get_text(strip=True) if code_el else "CLICK TO REVEAL",
                "description": desc_el.get_text(strip=True)[:100],
                "store": store,
                "source": "coupondunia",
            })
    return coupons

# ============================================================
# LAYER 5: TELEGRAM LOOT DEALS (public channels)
# ============================================================
async def telegram_deals(query):
    """Scrape public Telegram deal channels via web"""
    channels = [
        "https://t.me/s/lootdeals",
        "https://t.me/s/dealsnloot",
        "https://t.me/s/loothub",
    ]
    deals = []
    for ch_url in channels:
        html = await http_get(ch_url)
        if not html: continue
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html,"lxml")
        for msg in soup.select("div.tgme_widget_message_text")[:20]:
            text = msg.get_text(strip=True)
            if query.lower() in text.lower() or any(w in text.lower() for w in ["free","loot","99%","off","deal"]):
                price_match = re.search(r'[\u20b9Rs\.]+\s*[\d,]+', text)
                deals.append({
                    "text": text[:200],
                    "price_mentioned": price_match.group() if price_match else "",
                    "source": ch_url,
                    "type": "telegram_deal",
                })
            if len(deals) >= 5: break
        if len(deals) >= 5: break
    return deals

# ============================================================
# LAYER 6: BANK OFFERS DETECTION
# ============================================================
async def detect_bank_offers(html):
    """Detect bank/card offers from product page"""
    offers = []
    banks = ["HDFC","SBI","ICICI","Axis","Kotak","IDFC","RBL","Yes Bank","Citi","AMEX"]
    for bank in banks:
        if bank.lower() in html.lower():
            # Find context around bank mention
            idx = html.lower().find(bank.lower())
            context = html[max(0,idx-50):idx+150]
            from bs4 import BeautifulSoup
            text = BeautifulSoup(context,"lxml").get_text(strip=True)
            discount_match = re.search(r'(\d+)%\s*(?:off|instant|discount|cashback)', text, re.I)
            flat_match = re.search(r'(?:flat|instant)\s*[\u20b9Rs\.]*\s*([\d,]+)\s*off', text, re.I)
            if discount_match or flat_match:
                offers.append({
                    "bank": bank,
                    "offer": discount_match.group() if discount_match else flat_match.group(),
                    "source": "bank_offer_detection",
                })
    return offers

# ============================================================
# MASTER FUNCTION - Get EVERYTHING for a product
# ============================================================
async def get_everything(query, product_url=None):
    """Get lowest price + cashback + coupons + deals + bank offers"""
    print(f"\nSAM: Searching '{query}'...")
    t0 = time.time()

    # Run all sources in parallel
    tasks = [
        google_shopping(query),
        ddg_shopping(query),
        cashkaro_deals(query),
        gopaise_deals(query),
        coupondunia_coupons("flipkart.com"),
        coupondunia_coupons("amazon.in"),
        telegram_deals(query),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    google_results   = results[0] if isinstance(results[0], list) else []
    ddg_results      = results[1] if isinstance(results[1], list) else []
    cashkaro_results = results[2] if isinstance(results[2], list) else []
    gopaisa_results  = results[3] if isinstance(results[3], list) else []
    fk_coupons       = results[4] if isinstance(results[4], list) else []
    amz_coupons      = results[5] if isinstance(results[5], list) else []
    tg_deals         = results[6] if isinstance(results[6], list) else []

    # Combine all price results
    all_prices = google_results + ddg_results
    all_prices = [p for p in all_prices if p.get("price",0) > 0]
    all_prices.sort(key=lambda x: x.get("price_inr",0))

    elapsed = time.time()-t0

    # DISPLAY
    print(f"  Time: {elapsed:.1f}s")
    print(f"\n  PRICES ({len(all_prices)} found):")
    for p in all_prices[:8]:
        print(f"    Rs {p.get('price',0):>8,.0f} | {p.get('store','?'):25} | {p.get('name','')[:40]}")

    if all_prices:
        best = all_prices[0]
        print(f"\n  WORLD LOWEST: Rs {best.get('price',0):,.0f} at {best.get('store','?')}")

    print(f"\n  CASHBACK ({len(cashkaro_results)+len(gopaisa_results)} found):")
    for c in (cashkaro_results+gopaisa_results)[:4]:
        print(f"    {c.get('source','?'):12} | {c.get('cashback','?'):15} | {c.get('name','')[:40]}")

    print(f"\n  COUPONS ({len(fk_coupons)+len(amz_coupons)} found):")
    for c in (fk_coupons+amz_coupons)[:4]:
        print(f"    {c.get('store','?'):15} | {c.get('code','?'):15} | {c.get('description','')[:40]}")

    print(f"\n  TELEGRAM DEALS ({len(tg_deals)} found):")
    for d in tg_deals[:3]:
        print(f"    {d.get('price_mentioned','?'):10} | {d.get('text','')[:60]}")

    return {
        "query": query,
        "prices": all_prices[:10],
        "cashback": cashkaro_results + gopaisa_results,
        "coupons": fk_coupons + amz_coupons,
        "telegram_deals": tg_deals,
        "best_price": all_prices[0] if all_prices else None,
        "total_sources": len(all_prices),
    }

async def main():
    print("SAM DEEP SYSTEM - VGAS COMPLETE")
    print("="*55)

    queries = ["iPhone 16", "Samsung Galaxy S24", "Sony WH-1000XM5", "Nike Air Max", "boAt headphones"]

    all_data = {}
    for q in queries:
        data = await get_everything(q)
        all_data[q] = data

    with open("sam_deep_report.json","w",encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("\nSAM: Full report -> sam_deep_report.json")
    print("SAM DEEP MISSION: COMPLETE")

asyncio.run(main())
