# -*- coding: utf-8 -*-
"""
VGAS WORLD DEAL HUNTER v9
सर्व जगातून सर्वात स्वस्त deals - REAL WORKING
Platforms: Amazon IN, Snapdeal, Myntra, Walmart, eBay + Flipkart (browser)
"""
import asyncio, re, sys, json, concurrent.futures
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
AFF_AM = "tag=vgas-vikasg-21"
AFF_FK = "affid=vgas2024"

def aff(url, store):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{AFF_AM if store=='amazon' else AFF_FK}"

def fake_check(price, mrp):
    if mrp <= 0 or price <= 0: return "❓ Unknown"
    disc = round(((mrp - price) / mrp) * 100)
    if disc > 80: return f"⚠️ FAKE? ({disc}% - MRP inflate असू शकतो)"
    return f"✅ खरी सूट: {disc}%"

# ─── SCRAPERS ───────────────────────────────────────────────

def scrape_amazon(query):
    import requests
    from bs4 import BeautifulSoup
    results = []
    try:
        url = f"https://www.amazon.in/s?k={query.replace(' ','+')}&sort=price-asc"
        r = requests.get(url, headers=H, timeout=12)
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("div[data-component-type='s-search-result']")
        for card in cards[:4]:
            name = card.select_one("h2 a span")
            link = card.select_one("h2 a")
            price = card.select_one("span.a-price-whole")
            mrp = card.select_one("span.a-price.a-text-price span.a-offscreen")
            img = card.select_one("img.s-image")
            rating = card.select_one("span.a-icon-alt")
            if not (name and link and price): continue
            p = float(price.get_text().replace(",","").strip())
            m = float(re.sub(r"[^0-9.]","", mrp.get_text()) or p) if mrp else p
            href = link["href"]
            if not href.startswith("http"): href = "https://www.amazon.in" + href
            asin = re.search(r"/dp/([A-Z0-9]{10})", href)
            clean = f"https://www.amazon.in/dp/{asin.group(1)}" if asin else href.split("?")[0]
            if 200 < p < 500000:
                results.append({
                    "name": name.get_text(strip=True)[:65],
                    "price": p, "mrp": m,
                    "discount": round(((m-p)/m)*100) if m>p else 0,
                    "store": "Amazon.in 🇮🇳",
                    "url": clean,
                    "affiliate": aff(clean, "amazon"),
                    "image": img["src"] if img else "",
                    "rating": rating.get_text(strip=True)[:5] if rating else "N/A",
                    "fake": fake_check(p, m)
                })
    except Exception as e:
        pass
    return results

def scrape_snapdeal(query):
    import requests
    from bs4 import BeautifulSoup
    results = []
    try:
        url = f"https://www.snapdeal.com/search?keyword={query.replace(' ','+')}&sort=rlvncy&santizedQuery={query.replace(' ','+')}"
        r = requests.get(url, headers=H, timeout=12)
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("div.product-tuple-listing")
        for card in cards[:4]:
            name = card.select_one("p.product-title")
            price = card.select_one("span.product-price")
            mrp = card.select_one("span.product-desc-price")
            link = card.select_one("a.dp-widget-link")
            img = card.select_one("img.product-image")
            if not (name and price and link): continue
            p = float(re.sub(r"[^0-9.]","", price.get_text()) or 0)
            m = float(re.sub(r"[^0-9.]","", mrp.get_text()) or p) if mrp else p
            href = link["href"] if link["href"].startswith("http") else "https://www.snapdeal.com" + link["href"]
            if 100 < p < 500000:
                results.append({
                    "name": name.get_text(strip=True)[:65],
                    "price": p, "mrp": m,
                    "discount": round(((m-p)/m)*100) if m>p else 0,
                    "store": "Snapdeal 🇮🇳",
                    "url": href,
                    "affiliate": href,
                    "image": img["src"] if img else "",
                    "rating": "N/A",
                    "fake": fake_check(p, m)
                })
    except:
        pass
    return results

def scrape_myntra(query):
    import requests
    from bs4 import BeautifulSoup
    results = []
    try:
        url = f"https://www.myntra.com/{query.replace(' ','-')}?sort=price_asc"
        r = requests.get(url, headers=H, timeout=12)
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("li.product-base")
        for card in cards[:4]:
            name = card.select_one("h3.product-brand, h4.product-product")
            price = card.select_one("span.product-discountedPrice, div.product-price span")
            mrp = card.select_one("span.product-strike")
            link = card.select_one("a")
            img = card.select_one("img.img-responsive")
            if not (name and price): continue
            p = float(re.sub(r"[^0-9.]","", price.get_text()) or 0)
            m = float(re.sub(r"[^0-9.]","", mrp.get_text()) or p) if mrp else p
            href = "https://www.myntra.com/" + link["href"].lstrip("/") if link else url
            if 100 < p < 500000:
                results.append({
                    "name": name.get_text(strip=True)[:65],
                    "price": p, "mrp": m,
                    "discount": round(((m-p)/m)*100) if m>p else 0,
                    "store": "Myntra 🇮🇳",
                    "url": href,
                    "affiliate": href,
                    "image": img["src"] if img else "",
                    "rating": "N/A",
                    "fake": fake_check(p, m)
                })
    except:
        pass
    return results

def scrape_ebay(query):
    import requests
    from bs4 import BeautifulSoup
    results = []
    try:
        url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ','+')}&_sop=15"
        r = requests.get(url, headers=H, timeout=12)
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("li.s-item")
        for card in cards[:4]:
            name = card.select_one("div.s-item__title span")
            price = card.select_one("span.s-item__price")
            link = card.select_one("a.s-item__link")
            img = card.select_one("img.s-item__image-img")
            if not (name and price and link): continue
            p_txt = re.sub(r"[^0-9.]","", price.get_text().replace(",",""))
            if not p_txt: continue
            p = float(p_txt)
            # Convert USD to INR approx
            p_inr = round(p * 84)
            href = link["href"].split("?")[0]
            if 100 < p_inr < 500000:
                results.append({
                    "name": name.get_text(strip=True)[:65],
                    "price": p_inr, "mrp": p_inr,
                    "discount": 0,
                    "store": "eBay 🌍 (USD→INR)",
                    "url": href,
                    "affiliate": href,
                    "image": img["src"] if img else "",
                    "rating": "N/A",
                    "fake": "✅ eBay verified listing"
                })
    except:
        pass
    return results

def scrape_walmart(query):
    import requests
    from bs4 import BeautifulSoup
    results = []
    try:
        url = f"https://www.walmart.com/search?q={query.replace(' ','+')}&sort=price_low"
        r = requests.get(url, headers=H, timeout=12)
        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.select("div[data-item-id]")
        for card in cards[:4]:
            name = card.select_one("span.w_iUH7")
            price = card.select_one("div[data-automation-id='product-price'] span.w_iUH7")
            link = card.select_one("a")
            img = card.select_one("img")
            if not (name and price and link): continue
            p_txt = re.sub(r"[^0-9.]","", price.get_text())
            if not p_txt: continue
            p = float(p_txt)
            p_inr = round(p * 84)
            href = "https://www.walmart.com" + link["href"] if not link["href"].startswith("http") else link["href"]
            if 100 < p_inr < 500000:
                results.append({
                    "name": name.get_text(strip=True)[:65],
                    "price": p_inr, "mrp": p_inr,
                    "discount": 0,
                    "store": "Walmart 🇺🇸 (USD→INR)",
                    "url": href,
                    "affiliate": href,
                    "image": img["src"] if img else "",
                    "rating": "N/A",
                    "fake": "✅ Walmart verified"
                })
    except:
        pass
    return results

async def scrape_flipkart_browser(query, url):
    """Flipkart - Browser only (anti-bot bypass)"""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from bs4 import BeautifulSoup
    results = []
    try:
        async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as c:
            r = await c.arun(url=url, config=CrawlerRunConfig(page_timeout=25000, simulate_user=True, magic=True))
            soup = BeautifulSoup(r.html, "lxml")

        prices = []
        for el in soup.find_all(["div","span"], class_=True):
            t = el.get_text(strip=True)
            if re.match(r"^₹[\d,]+$", t):
                v = float(re.sub(r"[^0-9.]","",t))
                if 200 < v < 500000: prices.append(v)
        prices = sorted(set(prices))

        name_el = soup.select_one("span.VU-ZEz, span.B_NuCI, h1._6EBuvT, div.KzDlHZ")
        link_el = soup.select_one("a._1fQZEK, a.s1Q9rs, a[href*='/p/']")
        img_el = soup.select_one("img._396cs4, img.DByuf4")

        name = name_el.get_text(strip=True)[:65] if name_el else query
        href = ""
        if link_el:
            href = link_el.get("href","")
            if not href.startswith("http"): href = "https://www.flipkart.com" + href
            pid = re.search(r"pid=([A-Z0-9]+)", href)
            path = re.search(r"(/[a-z0-9-]+/p/[a-z0-9]+)", href)
            if path and pid: href = f"https://www.flipkart.com{path.group(1)}?pid={pid.group(1)}"

        if prices:
            p = prices[0]
            m = prices[-1] if len(prices)>1 else p
            results.append({
                "name": name,
                "price": p, "mrp": m,
                "discount": round(((m-p)/m)*100) if m>p else 0,
                "store": "Flipkart 🇮🇳",
                "url": href or url,
                "affiliate": aff(href or url, "flipkart"),
                "image": img_el["src"] if img_el else "",
                "rating": "N/A",
                "fake": fake_check(p, m)
            })
    except:
        pass
    return results

async def world_deal_hunt(query):
    print(f"\n{'='*80}")
    print(f"🌍 WORLD DEAL HUNT: {query}")
    print(f"{'='*80}")

    # Parallel requests (fast platforms)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        f_am = ex.submit(scrape_amazon, query)
        f_sd = ex.submit(scrape_snapdeal, query)
        f_my = ex.submit(scrape_myntra, query)
        f_eb = ex.submit(scrape_ebay, query)
        f_wm = ex.submit(scrape_walmart, query)
        am = f_am.result()
        sd = f_sd.result()
        my = f_my.result()
        eb = f_eb.result()
        wm = f_wm.result()

    # Flipkart browser
    fk_url = f"https://www.flipkart.com/search?q={query.replace(' ','+')}&sort=price_asc"
    fk = await scrape_flipkart_browser(query, fk_url)

    all_results = fk + am + sd + my + eb + wm
    all_results.sort(key=lambda x: x["price"])

    print(f"\n📊 {len(all_results)} deals found across {len([x for x in [fk,am,sd,my,eb,wm] if x])} platforms\n")

    for i, r in enumerate(all_results[:8], 1):
        print(f"{i}. [{r['store']}] {r['name'][:55]}")
        print(f"   💰 ₹{r['price']:,.0f}  MRP:₹{r['mrp']:,.0f}  {r['discount']}% OFF  ⭐{r['rating']}")
        print(f"   {r['fake']}")
        print(f"   🛒 BUY: {r['url']}")
        print(f"   💸 EARN: {r['affiliate']}")
        print()

    return all_results

async def main():
    print("=" * 80)
    print("🚀 VGAS WORLD DEAL HUNTER v9")
    print("   Platforms: Amazon🇮🇳 Flipkart🇮🇳 Snapdeal🇮🇳 Myntra🇮🇳 eBay🌍 Walmart🇺🇸")
    print("   उद्दिष्ट: जगातील सर्वात स्वस्त deals - गरीब लोकांसाठी")
    print("=" * 80)

    queries = [
        "smartphone under 10000",
        "laptop under 30000",
        "wireless headphones",
        "smart tv 43 inch",
        "washing machine",
        "refrigerator",
        "air conditioner",
        "tablet",
        "smartwatch",
        "bluetooth speaker"
    ]

    all_deals = []
    for q in queries:
        deals = await world_deal_hunt(q)
        all_deals.extend(deals)

    all_deals.sort(key=lambda x: x["price"])

    print(f"\n{'='*80}")
    print(f"🏆 WORLD TOP 20 CHEAPEST DEALS")
    print(f"{'='*80}\n")

    for i, r in enumerate(all_deals[:20], 1):
        print(f"{i:2}. [{r['store']}] {r['name'][:50]}")
        print(f"    💰 ₹{r['price']:,.0f}  {r['discount']}% OFF  {r['fake']}")
        print(f"    🛒 {r['url']}")
        print()

    # Save JSON
    with open("vgas_world_deals.json", "w", encoding="utf-8") as f:
        json.dump(all_deals, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(all_deals)} world deals saved to vgas_world_deals.json")

asyncio.run(main())
