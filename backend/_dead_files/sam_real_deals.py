# -*- coding: utf-8 -*-
"""
SAM FINAL ORDER - VGAS REAL DEALS ENGINE
Goal: Real cheapest/free deals for every user forever
Tools: Scrapling + curl_cffi + free proxies + price alerts + WhatsApp
"""
import asyncio, sys, re, json, time, os, random
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))

MISTRAL_KEY = os.environ.get("MISTRAL_API_KEY", "")
WHATSAPP_NUM = "919881300933"
ALERT_FILE = "price_alerts.json"
HISTORY_FILE = "price_history.json"

# ============================================================
# FREE PROXY MANAGER (GitHub: clarketm/proxy-list)
# ============================================================
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working = []

    async def fetch_free_proxies(self):
        """Fetch from multiple free proxy sources"""
        sources = [
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        ]
        from curl_cffi.requests import AsyncSession
        for src in sources:
            try:
                async with AsyncSession(impersonate="chrome124") as s:
                    r = await s.get(src, timeout=8)
                    lines = [l.strip() for l in r.text.split("\n") if ":" in l.strip()]
                    self.proxies.extend(lines[:50])
            except: continue
        self.proxies = list(set(self.proxies))
        print(f"  Proxies loaded: {len(self.proxies)}")
        return self.proxies

    async def test_proxy(self, proxy):
        try:
            from curl_cffi.requests import AsyncSession
            async with AsyncSession(impersonate="chrome124") as s:
                r = await s.get("https://httpbin.org/ip", proxies={"http":f"http://{proxy}","https":f"http://{proxy}"}, timeout=5)
                if r.status_code == 200:
                    return proxy
        except: pass
        return None

    async def get_working(self, count=5):
        if self.working: return self.working[:count]
        tasks = [self.test_proxy(p) for p in self.proxies[:30]]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        self.working = [r for r in results if isinstance(r,str)]
        print(f"  Working proxies: {len(self.working)}")
        return self.working[:count]

    def random_proxy(self):
        if self.working: return {"http":f"http://{random.choice(self.working)}","https":f"http://{random.choice(self.working)}"}
        return None

proxy_mgr = ProxyManager()

# ============================================================
# SMART HTTP - curl_cffi + proxy rotation
# ============================================================
async def smart_get(url, use_proxy=False):
    from curl_cffi.requests import AsyncSession
    proxy = proxy_mgr.random_proxy() if use_proxy and proxy_mgr.working else None
    try:
        async with AsyncSession(impersonate="chrome124") as s:
            kwargs = {"timeout":12,"headers":{"Accept-Language":"en-IN,en;q=0.9"}}
            if proxy: kwargs["proxies"] = proxy
            r = await s.get(url, **kwargs)
            if r.status_code == 200: return r.text
    except: pass
    # Fallback without proxy
    try:
        async with AsyncSession(impersonate="chrome110") as s:
            r = await s.get(url, timeout=12, headers={"Accept-Language":"en-IN,en;q=0.9"})
            return r.text if r.status_code == 200 else ""
    except: return ""

async def browser_get(url):
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        async with AsyncWebCrawler(config=BrowserConfig(headless=True,verbose=False)) as c:
            r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=20000,simulate_user=True,magic=True))
            return r.html if r.success else ""
    except: return ""

# ============================================================
# PRICE PARSER
# ============================================================
def pp(t):
    from price_parser import Price
    try:
        p = Price.fromstring(str(t))
        if p.amount: return float(p.amount)
    except: pass
    try: return float(re.sub(r"[^\d.]","",str(t)) or 0)
    except: return 0.0

# ============================================================
# PLATFORM PARSERS
# ============================================================
def parse_amazon(html, domain="amazon.in"):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    cur = "INR" if "amazon.in" in domain else "USD"
    rate = 1 if cur=="INR" else 84
    out = []
    for card in soup.select("div[data-component-type='s-search-result']")[:6]:
        n = card.select_one("h2 a span")
        p = card.select_one("span.a-price-whole")
        l = card.select_one("h2 a")
        i = card.select_one("img.s-image")
        rt= card.select_one("span.a-icon-alt")
        if not n or not p: continue
        price = pp(p.get_text())
        if price <= 0: continue
        href = l["href"] if l else ""
        link = f"https://www.{domain}{href}" if not href.startswith("http") else href
        out.append({
            "name":n.get_text(strip=True)[:100],"price":price,
            "price_inr":price*rate,"currency":cur,"store":domain,
            "url":f"{link}&tag=vgas-vikasg-21",
            "image":i.get("src","") if i else "",
            "rating":pp(rt.get_text()) if rt else 0.0,
        })
    return out

def parse_flipkart(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    out = []
    for card in soup.select("div[data-id]")[:6]:
        n = card.select_one("div._4rR01T,a.s1Q9rs,div.KzDlHZ,div._2WkVRV")
        p = card.select_one("div._1psv1ze2c,div.css-g5y9jx,div._30jeq3,div.Nx9bqj")
        l = card.select_one("a[href*='/p/']")
        i = card.select_one("img._396cs4,img.DByuf4")
        if not n: continue
        price = pp(p.get_text()) if p else 0.0
        if price <= 0: continue
        href = l["href"] if l else ""
        link = f"https://www.flipkart.com{href}" if not href.startswith("http") else href
        out.append({
            "name":n.get_text(strip=True)[:100],"price":price,
            "price_inr":price,"currency":"INR","store":"flipkart.com",
            "url":f"{link}&affid=vgas2024",
            "image":i.get("src","") if i else "",
        })
    return out

def parse_meesho(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    out = []
    for card in soup.select("div[class*='ProductList'],div[class*='product-card'],div[class*='NewProductCard']")[:6]:
        n = card.select_one("p[class*='ProductTitle'],h5,p[class*='name']")
        p = card.select_one("h5[class*='price'],span[class*='price'],div[class*='price']")
        l = card.select_one("a[href]")
        i = card.select_one("img")
        if not n: continue
        price = pp(p.get_text()) if p else 0.0
        if price <= 0: continue
        href = l["href"] if l else ""
        link = f"https://www.meesho.com{href}" if not href.startswith("http") else href
        out.append({
            "name":n.get_text(strip=True)[:100],"price":price,
            "price_inr":price,"currency":"INR","store":"meesho.com",
            "url":f"{link}?utm_source=vgas","image":i.get("src","") if i else "",
        })
    return out

def parse_ebay(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    out = []
    for card in soup.select("li.s-item")[:6]:
        n = card.select_one("div.s-item__title")
        p = card.select_one("span.s-item__price")
        l = card.select_one("a.s-item__link")
        i = card.select_one("img")
        if not n or not p: continue
        name = n.get_text(strip=True)
        if "Shop on eBay" in name: continue
        price = pp(p.get_text())
        if price <= 0: continue
        out.append({
            "name":name[:100],"price":price,"price_inr":price*84,
            "currency":"USD","store":"ebay.com",
            "url":l["href"] if l else "","image":i.get("src","") if i else "",
        })
    return out

def parse_snapdeal(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html,"lxml")
    out = []
    for card in soup.select("li.product-tuple-listing")[:6]:
        n = card.select_one("p.product-title")
        p = card.select_one("span.product-price")
        l = card.select_one("a[href]")
        i = card.select_one("img")
        if not n or not p: continue
        price = pp(p.get_text())
        if price <= 0: continue
        out.append({
            "name":n.get_text(strip=True)[:100],"price":price,
            "price_inr":price,"currency":"INR","store":"snapdeal.com",
            "url":l["href"] if l else "","image":i.get("src","") if i else "",
        })
    return out

# ============================================================
# LOOT DEALS - FREE / 90%+ OFF
# ============================================================
async def get_loot_deals():
    """Real loot deals from Telegram public channels"""
    deals = []
    channels = [
        "https://t.me/s/lootdeals",
        "https://t.me/s/dealsnloot",
        "https://t.me/s/loothub",
        "https://t.me/s/indiandealshunter",
        "https://t.me/s/dealsforindians",
    ]
    from bs4 import BeautifulSoup
    for ch in channels:
        html = await smart_get(ch)
        if not html: continue
        soup = BeautifulSoup(html,"lxml")
        for msg in soup.select("div.tgme_widget_message_text")[:10]:
            text = msg.get_text(strip=True)
            price_m = re.search(r'[\u20b9Rs\.]+\s*[\d,]+', text)
            free = any(w in text.lower() for w in ["free","loot","99%","90%","₹0","rs 0","rs0"])
            if price_m or free:
                deals.append({
                    "text": text[:200],
                    "price": price_m.group() if price_m else "FREE",
                    "is_free": free,
                    "source": ch.split("/")[-1],
                    "type": "LOOT" if free else "DEAL",
                })
        if len(deals) >= 15: break
    return deals

# ============================================================
# CASHBACK AGGREGATOR
# ============================================================
async def get_cashback_offers(query):
    """CashKaro + GoPaisa cashback"""
    offers = []
    from bs4 import BeautifulSoup

    # CashKaro
    html = await smart_get(f"https://cashkaro.com/search?q={query.replace(' ','+')}")
    if html:
        soup = BeautifulSoup(html,"lxml")
        for card in soup.select("div[class*='store'],div[class*='deal'],div[class*='offer']")[:5]:
            cb = card.select_one("[class*='cashback'],[class*='earn']")
            name = card.select_one("h3,h4,a")
            if cb and name:
                offers.append({"platform":"CashKaro","name":name.get_text(strip=True)[:60],"cashback":cb.get_text(strip=True)})

    # GoPaisa
    html2 = await smart_get(f"https://www.gopaisa.com/search?q={query.replace(' ','+')}")
    if html2:
        soup2 = BeautifulSoup(html2,"lxml")
        for card in soup2.select("div[class*='deal'],div[class*='offer']")[:5]:
            cb = card.select_one("[class*='cashback'],[class*='earn']")
            name = card.select_one("h3,h4,a")
            if cb and name:
                offers.append({"platform":"GoPaisa","name":name.get_text(strip=True)[:60],"cashback":cb.get_text(strip=True)})

    return offers

# ============================================================
# PRICE HISTORY + ALERTS
# ============================================================
def save_price(name, price, store):
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE,"r",encoding="utf-8") as f:
            history = json.load(f)
    key = name[:50]
    if key not in history: history[key] = []
    history[key].append({"price":price,"store":store,"date":time.strftime("%Y-%m-%d %H:%M")})
    history[key] = history[key][-50:]
    with open(HISTORY_FILE,"w",encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def check_fake_discount(price, orig):
    if orig <= price or price <= 0: return False, 0
    actual = round(((orig-price)/orig)*100)
    return actual > 5, actual

def set_price_alert(user, product, target_price, current_url):
    alerts = {}
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE,"r",encoding="utf-8") as f:
            alerts = json.load(f)
    if user not in alerts: alerts[user] = []
    alerts[user].append({
        "product":product,"target_price":target_price,
        "url":current_url,"created":time.strftime("%Y-%m-%d %H:%M")
    })
    with open(ALERT_FILE,"w",encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)
    return True

async def send_whatsapp_alert(phone, message):
    """Send WhatsApp alert via VGAS bot backend"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "http://localhost:8001/api/v1/whatsapp/send",
                json={"phone":phone,"message":message},
                timeout=5
            )
            return r.status_code == 200
    except: return False

# ============================================================
# MAIN SEARCH ENGINE
# ============================================================
async def search_world(query, limit=5):
    """Search all platforms in parallel"""
    q = query.replace(" ","+")

    amz_in, amz_com, fk, ebay, snap, meesho = await asyncio.gather(
        smart_get(f"https://www.amazon.in/s?k={q}&sort=price-asc-rank"),
        smart_get(f"https://www.amazon.com/s?k={q}&sort=price-asc-rank"),
        browser_get(f"https://www.flipkart.com/search?q={q}&sort=price_asc"),
        smart_get(f"https://www.ebay.com/sch/i.html?_nkw={q}&_sop=15"),
        smart_get(f"https://www.snapdeal.com/search?keyword={q}&sort=rlvncy"),
        browser_get(f"https://www.meesho.com/search?q={q}"),
        return_exceptions=True
    )

    products = []
    if isinstance(amz_in,str) and amz_in:   products.extend(parse_amazon(amz_in,"amazon.in"))
    if isinstance(amz_com,str) and amz_com: products.extend(parse_amazon(amz_com,"amazon.com"))
    if isinstance(fk,str) and fk:           products.extend(parse_flipkart(fk))
    if isinstance(ebay,str) and ebay:       products.extend(parse_ebay(ebay))
    if isinstance(snap,str) and snap:       products.extend(parse_snapdeal(snap))
    if isinstance(meesho,str) and meesho:   products.extend(parse_meesho(meesho))

    products = sorted([p for p in products if p.get("price_inr",0)>0], key=lambda x:x["price_inr"])

    # Save price history
    for p in products[:3]:
        save_price(p["name"], p["price_inr"], p["store"])

    return products

# ============================================================
# SAM TEST - FULL REAL WORKING
# ============================================================
async def main():
    print("SAM VGAS REAL DEALS ENGINE")
    print("="*55)

    # Step 1: Load proxies
    print("\n[1] Loading free proxies...")
    await proxy_mgr.fetch_free_proxies()
    await proxy_mgr.get_working(count=3)

    # Step 2: Search products
    queries = ["iPhone 16 128GB","Samsung Galaxy S24","boAt Airdopes 141","laptop under 50000","Nike shoes"]
    all_results = {}

    print("\n[2] World Search - All Platforms...")
    for query in queries:
        t0 = time.time()
        products = await search_world(query)
        elapsed = time.time()-t0
        all_results[query] = products[:8]

        print(f"\n  [{query}] {len(products)} results in {elapsed:.1f}s")
        print(f"  {'STORE':22} {'PRICE':>10} {'INR':>10}  NAME")
        print(f"  {'-'*65}")
        for p in products[:5]:
            sym = {"INR":"Rs","USD":"$","GBP":"£"}.get(p["currency"],"")
            print(f"  {p['store']:22} {sym+str(int(p['price'])):>10} {int(p['price_inr']):>10}  {p['name'][:30]}")
        if products:
            best = products[0]
            print(f"  LOWEST: Rs {best['price_inr']:,.0f} @ {best['store']}")
            print(f"  BUY   : {best['url'][:65]}")

            # Set demo price alert
            set_price_alert(WHATSAPP_NUM, query, best["price_inr"]*0.9, best["url"])

    # Step 3: Loot deals
    print("\n[3] Getting LOOT DEALS (Free/90%+ off)...")
    loot = await get_loot_deals()
    print(f"  Found {len(loot)} loot deals")
    for d in loot[:5]:
        tag = "FREE" if d["is_free"] else "DEAL"
        print(f"  [{tag}] {d['price']:10} | {d['text'][:60]}")

    # Step 4: Cashback
    print("\n[4] Cashback offers...")
    cb = await get_cashback_offers("iPhone")
    print(f"  Found {len(cb)} cashback offers")
    for c in cb[:3]:
        print(f"  {c['platform']:12} | {c['cashback']:15} | {c['name'][:40]}")

    # Step 5: Price alerts status
    print("\n[5] Price Alerts saved...")
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE,"r",encoding="utf-8") as f:
            alerts = json.load(f)
        total = sum(len(v) for v in alerts.values())
        print(f"  Total alerts: {total}")

    # Save full report
    report = {
        "search_results": all_results,
        "loot_deals": loot[:10],
        "cashback": cb,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_products_found": sum(len(v) for v in all_results.values()),
    }
    with open("sam_real_deals_report.json","w",encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nSAM: Report -> sam_real_deals_report.json")
    print(f"Total products: {report['total_products_found']}")
    print("SAM MISSION: COMPLETE")

asyncio.run(main())
