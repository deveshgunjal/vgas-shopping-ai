# SAM SKILL: VGAS REAL DEALS ENGINE v3.0
# Token: Minimal | Real Working | No Placeholders
# Cache in D:\Sam\memory_vault\

import asyncio, sys, re, json, time, os
sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# MINIMAL WORKING ENGINE - CACHED SELECTORS
# ============================================================
SELECTORS = json.dumps({
    "flipkart": {
        "card": "div[data-id] div._1YokD2",
        "name": "div[class*='KzDlHZ'],a.s1Q9rs", 
        "price": "div[class*='Nx9bqj'],div[class*='jeq3']"
    },
    "amazon": {
        "card": "div[data-component-type='s-search-result']",
        "name": "h2 a span",
        "price": "span.a-price-whole"
    },
    "meesho": {
        "card": "div[class*='ProductCard'],div.NewProductCard",
        "name": "p[class*='Named'],h5",
        "price": "h5[class*='price'],span[class*='Price']"
    }
})

CACHE = {}
CACHE_TTL = 3600

pp = lambda t: float(re.sub(r"[^\d.]","",str(t)) or 0) if t else 0.0

async def get(url):
    try:
        from curl_cffi.requests import AsyncSession
        async with AsyncSession(impersonate="chrome124") as s:
            r = await s.get(url, timeout=10, headers={"Accept-Language":"en-IN"})
            return r.text if r.status_code==200 else ""
    except: return ""

async def browser(url):
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        c = BrowserConfig(headless=True, verbose=False)
        r = CrawlerRunConfig(page_timeout=18000, simulate_user=True, magic=True)
        async with AsyncWebCrawler(config=c) as w:
            res = await w.arun(url=url, config=r)
            return res.html if res.success else ""
    except: return ""

def pf(html, store):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "lxml")
    sel = json.loads(SELECTORS).get(store, {})
    out = []
    for c in s.select(sel.get("card","div[data-id]"))[:5]:
        n = c.select_one(sel.get("name","h2,h3,a"))
        p = c.select_one(sel.get("price","[class*='price']"))
        l = c.select_one("a[href]")
        if n and p:
            price = pp(p.get_text())
            if price > 0:
                out.append({"n":n.get_text(strip=True)[:80],"p":price,"s":store,"u":l["href"] if l else ""})
    return out

async def search(q):
    q2 = q.replace(" ","+")
    res = await asyncio.gather(
        get(f"https://www.amazon.in/s?k={q2}"),
        browser(f"https://www.flipkart.com/search?q={q2}&sort=price_asc"),
        browser(f"https://www.meesho.com/search?q={q2}"),
        return_exceptions=True
    )
    out = []
    if isinstance(res[0],str) and res[0]: out.extend(pf(res[0],"amazon"))
    if isinstance(res[1],str) and res[1]: out.extend(pf(res[1],"flipkart"))
    if isinstance(res[2],str) and res[2]: out.extend(pf(res[2],"meesho"))
    return sorted([x for x in out if x.get("p",0)>0], key=lambda x:x["p"])

# ============================================================
# RUN
# ============================================================
async def main():
    print("SAM VGAS ENGINE v3.0 - Token Optimized")
    for q in ["boAt Airdopes 141","iPhone 16","laptop 50000"]:
        t0 = time.time()
        r = await search(q)
        print(f"\n{q}: {len(r)} results in {time.time()-t0:.1f}s")
        for x in r[:3]: print(f"  {x['s']:12} Rs {x['p']:>8,.0f}  {x['n'][:40]}")
        if r: print(f"  LOWEST: Rs {r[0]['p']:,.0f}")

asyncio.run(main())
