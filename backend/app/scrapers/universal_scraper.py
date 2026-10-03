# -*- coding: utf-8 -*-
"""
VGAS Universal Smart Scraper
SAM Innovation: Crawl4AI + ScrapeGraphAI + Mistral AI
Free, Real-time, No disturbance, All platforms
"""
import asyncio, re, json, logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

# Platform configs
PLATFORMS = {
    "amazon.in":    {"affiliate": "vgas-vikasg-21", "tag_param": "tag"},
    "flipkart.com": {"affiliate": "vgas2024",        "tag_param": "affid"},
    "myntra.com":   {"affiliate": "vgas",            "tag_param": "utm_source"},
    "ajio.com":     {"affiliate": "vgas",            "tag_param": "utm_source"},
    "meesho.com":   {"affiliate": "vgas",            "tag_param": "utm_source"},
    "snapdeal.com": {"affiliate": "vgas",            "tag_param": "utm_source"},
    "tatacliq.com": {"affiliate": "vgas",            "tag_param": "utm_source"},
    "croma.com":    {"affiliate": "vgas",            "tag_param": "utm_source"},
    "nykaa.com":    {"affiliate": "vgas",            "tag_param": "utm_source"},
    "amazon.com":   {"affiliate": "vgas-us-21",      "tag_param": "tag"},
    "walmart.com":  {"affiliate": "vgas",            "tag_param": "utm_source"},
    "ebay.com":     {"affiliate": "vgas",            "tag_param": "campid"},
    "aliexpress.com":{"affiliate": "vgas",           "tag_param": "utm_source"},
    "noon.com":     {"affiliate": "vgas",            "tag_param": "utm_source"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}

# In-memory cache (Redis fallback)
_cache: Dict[str, Any] = {}
CACHE_TTL = 3600  # 1 hour


def _cache_get(key: str):
    if key in _cache:
        data, ts = _cache[key]
        if (datetime.now().timestamp() - ts) < CACHE_TTL:
            return data
    return None


def _cache_set(key: str, data: Any):
    _cache[key] = (data, datetime.now().timestamp())


def _affiliate_url(url: str, platform: str) -> str:
    cfg = PLATFORMS.get(platform, {})
    if not cfg:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{cfg['tag_param']}={cfg['affiliate']}&vgas=1"


def _detect_platform(url: str) -> str:
    for p in PLATFORMS:
        if p in url:
            return p
    return "unknown"


def _to_float(text: str) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", str(text)) or 0)
    except:
        return 0.0


def _to_int(text: str) -> int:
    try:
        return int(re.sub(r"[^\d]", "", str(text)) or 0)
    except:
        return 0


async def _scrape_with_crawl4ai(url: str) -> str:
    """Browser scrape with Crawl4AI - handles JS, anti-bot"""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        cfg = BrowserConfig(headless=True, verbose=False)
        rcfg = CrawlerRunConfig(page_timeout=30000, simulate_user=True, magic=True)
        async with AsyncWebCrawler(config=cfg) as c:
            res = await c.arun(url=url, config=rcfg)
            if res.success:
                return res.html
    except Exception as e:
        logger.warning(f"Crawl4AI: {e}")
    return ""


async def _scrape_with_aiohttp(url: str) -> str:
    """Fast HTTP scrape fallback"""
    try:
        import aiohttp, ssl
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(headers=HEADERS) as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=15), ssl=ssl_ctx) as r:
                return await r.text()
    except Exception as e:
        logger.warning(f"aiohttp: {e}")
    return ""


def _extract_with_ai_prompt(html: str, url: str) -> Dict[str, Any]:
    """ScrapeGraphAI - Mistral AI extracts data from HTML - no CSS selectors needed"""
    try:
        from scrapegraphai.graphs import SmartScraperGraph
        graph = SmartScraperGraph(
            prompt="Extract: product name, current price (number only), original/MRP price, discount percentage, rating, image URL, in stock status",
            source=url,
            config={
                "llm": {
                    "api_key": MISTRAL_API_KEY,
                    "model": "mistralai/mistral-large-latest",
                },
                "verbose": False,
                "headless": True,
            }
        )
        result = graph.run()
        if result and isinstance(result, dict):
            return {
                "name": result.get("product name") or result.get("name", ""),
                "price": _to_float(result.get("current price") or result.get("price", 0)),
                "original_price": _to_float(result.get("original price") or result.get("mrp", 0)),
                "discount_percentage": _to_int(result.get("discount percentage") or result.get("discount", 0)),
                "rating": _to_float(result.get("rating", 0)),
                "image": result.get("image URL") or result.get("image", ""),
                "in_stock": bool(result.get("in stock", True)),
                "source": "scrapegraphai+mistral",
            }
    except Exception as e:
        logger.warning(f"ScrapeGraphAI: {e}")
    return {}


def _extract_from_html(html: str, url: str, platform: str) -> Dict[str, Any]:
    """Smart HTML extraction with dynamic rupee/price scan"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # Universal name extraction
    name = ""
    for sel in ["span.VU-ZEz", "span.B_NuCI", "h1.yhB1nd", "#productTitle",
                "h1.x-item-title__mainTitle", "h1", "title"]:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t and len(t) > 3:
                name = t[:150]; break

    # Universal price scan - rupee + dollar + pound
    price_els = []
    for el in soup.find_all(["div", "span"], class_=True):
        t = el.get_text(strip=True)
        # Only direct text, not nested children combined
        direct_text = "".join(c for c in el.children if isinstance(c, str)).strip()
        check_text = direct_text if direct_text else t
        for sym in ["\u20b9", "$", "£", "€", "AED"]:
            if sym in check_text and 3 < len(check_text) < 15:
                val = _to_float(check_text)
                if 100 < val < 10000000:  # sanity: Rs 100 to 1 crore
                    price_els.append(val)
                break

    price_els = sorted(set(price_els))
    price = price_els[0] if price_els else 0.0
    orig = price_els[-1] if len(price_els) > 1 else price

    # Discount
    disc = 0
    for sel in ["div.UkUFwK span", "div._3Ay6Sb span", "span.savingsPercentage",
                "span.a-color-price", "[class*='discount']", "[class*='saving']"]:
        el = soup.select_one(sel)
        if el:
            disc = _to_int(el.get_text()); break
    if not disc and orig > price > 0:
        disc = round(((orig - price) / orig) * 100)

    # Rating
    rating = 0.0
    for sel in ["div.XQDdHH", "div._3LWZlK", "span.a-icon-alt",
                "div.ipqd2A", "[class*='rating']"]:
        el = soup.select_one(sel)
        if el:
            rating = _to_float(el.get_text()); break

    # Image
    img = ""
    for sel in ["img._396cs4", "img.DByuf4", "#landingImage",
                "img.s-image", "img[data-old-hires]"]:
        el = soup.select_one(sel)
        if el and (el.get("src") or el.get("data-old-hires")):
            img = el.get("data-old-hires") or el.get("src", ""); break

    # Fake discount detection
    fake = False
    fake_msg = "Cannot verify"
    if orig > price > 0:
        actual_disc = round(((orig - price) / orig) * 100)
        fake = abs(actual_disc - disc) > 10
        fake_msg = f"FAKE! Claimed {disc}% actual {actual_disc}%" if fake else f"GENUINE {disc}% discount"

    return {
        "name": name or "Unknown",
        "price": price,
        "original_price": orig,
        "discount_percentage": disc,
        "rating": rating,
        "image": img,
        "in_stock": True,
        "fake_discount": fake,
        "fake_discount_msg": fake_msg,
        "source": "html_parser",
    }


async def scrape_product(url: str, use_browser: bool = True) -> Dict[str, Any]:
    """
    MAIN FUNCTION - scrape any product URL
    Strategy: Cache -> aiohttp -> Crawl4AI browser -> ScrapeGraphAI+Mistral
    """
    # Cache check
    cached = _cache_get(url)
    if cached:
        cached["from_cache"] = True
        return cached

    platform = _detect_platform(url)

    # Flipkart needs browser (JS rendered)
    needs_browser = any(p in url for p in ["flipkart", "meesho", "ajio"])

    # Step 1: Try fast aiohttp first (skip for JS-heavy sites)
    html = ""
    if not needs_browser:
        html = await _scrape_with_aiohttp(url)

    result = {}
    if html:
        result = _extract_from_html(html, url, platform)

    # Step 2: Browser scrape for JS sites or if price missing
    if (not result.get("price") or needs_browser) and use_browser:
        logger.info(f"Browser scrape: {platform}")
        html = await _scrape_with_crawl4ai(url)
        if html:
            result = _extract_from_html(html, url, platform)

    # Step 3: If still missing, use ScrapeGraphAI + Mistral AI
    if not result.get("price") or result.get("name") == "Unknown":
        logger.info(f"AI extraction: {platform}")
        ai_result = _extract_with_ai_prompt(html, url)
        if ai_result:
            result.update({k: v for k, v in ai_result.items() if v})

    # Add metadata
    result.update({
        "url": url,
        "affiliate_url": _affiliate_url(url, platform),
        "store": platform,
        "currency": "INR" if any(x in url for x in ["amazon.in", "flipkart", "myntra", "ajio", "meesho"]) else "USD",
        "scraped_at": datetime.now().isoformat(),
        "from_cache": False,
    })

    # Cache result
    if result.get("price", 0) > 0:
        _cache_set(url, result)

    return result


async def search_all_platforms(query: str, platforms: List[str] = None, limit: int = 5) -> Dict[str, List]:
    """Search product across multiple platforms simultaneously"""
    if not platforms:
        platforms = ["amazon.in", "flipkart.com", "myntra.com", "ajio.com", "meesho.com"]

    search_urls = {
        "amazon.in":    f"https://www.amazon.in/s?k={query.replace(' ', '+')}",
        "flipkart.com": f"https://www.flipkart.com/search?q={query.replace(' ', '+')}",
        "myntra.com":   f"https://www.myntra.com/{query.replace(' ', '-')}",
        "ajio.com":     f"https://www.ajio.com/search/?text={query.replace(' ', '+')}",
        "meesho.com":   f"https://www.meesho.com/search?q={query.replace(' ', '+')}",
        "walmart.com":  f"https://www.walmart.com/search?q={query.replace(' ', '+')}",
        "ebay.com":     f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}",
    }

    tasks = []
    active_platforms = []
    for p in platforms:
        if p in search_urls:
            tasks.append(_scrape_with_aiohttp(search_urls[p]))
            active_platforms.append(p)

    # Run all platforms in parallel
    htmls = await asyncio.gather(*tasks, return_exceptions=True)

    results = {}
    for platform, html in zip(active_platforms, htmls):
        if isinstance(html, str) and html:
            results[platform] = _parse_search_results(html, platform, limit)
        else:
            results[platform] = []

    return results


def _parse_search_results(html: str, platform: str, limit: int) -> List[Dict]:
    """Parse search results page"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    products = []

    # Universal product card selectors
    card_selectors = {
        "amazon.in":    "div[data-component-type='s-search-result']",
        "flipkart.com": "div[data-id]",
        "default":      "div[class*='product'], div[class*='item'], article",
    }
    sel = card_selectors.get(platform, card_selectors["default"])
    cards = soup.select(sel)[:limit]

    for card in cards:
        try:
            # Name
            name = ""
            for ns in ["h2 a span", "div._4rR01T", "span.VU-ZEz", "a.s1Q9rs", "h2", "h3"]:
                el = card.select_one(ns)
                if el and el.get_text(strip=True):
                    name = el.get_text(strip=True)[:100]; break

            # Price - scan for currency symbols
            price = 0.0
            for el in card.find_all(["span", "div"], class_=True):
                t = el.get_text(strip=True)
                if any(s in t for s in ["\u20b9", "$", "£"]) and len(t) < 15:
                    v = _to_float(t)
                    if v > 0:
                        price = v; break

            # Link
            link_el = card.select_one("a[href]")
            link = ""
            if link_el:
                href = link_el.get("href", "")
                link = href if href.startswith("http") else f"https://www.{platform}{href}"

            if name and price:
                products.append({
                    "name": name,
                    "price": price,
                    "url": _affiliate_url(link, platform),
                    "store": platform,
                    "currency": "INR" if "amazon.in" in platform or "flipkart" in platform else "USD",
                })
        except:
            continue

    return products


# SAM TEST
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    async def sam_test():
        print("SAM: Testing Universal Scraper...")
        print("="*50)

        # Test 1: Flipkart iPhone 16
        url = "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G"
        print(f"\nTest 1: {url[:60]}...")
        r = await scrape_product(url)
        print(f"  Name    : {r.get('name')}")
        print(f"  Price   : {r.get('currency')} {r.get('price')}")
        print(f"  Orig    : {r.get('currency')} {r.get('original_price')}")
        print(f"  Disc    : {r.get('discount_percentage')}%")
        print(f"  Fake    : {r.get('fake_discount_msg')}")
        print(f"  Aff URL : {r.get('affiliate_url','')[:70]}")

        # Test 2: Search all platforms
        print(f"\nTest 2: Search 'iPhone 16' on all platforms...")
        results = await search_all_platforms("iPhone 16", limit=3)
        for platform, items in results.items():
            print(f"\n  {platform}: {len(items)} results")
            for item in items[:2]:
                print(f"    - {item.get('name','')[:50]} | {item.get('currency')} {item.get('price')}")

        print("\nSAM: ALL TESTS COMPLETE")

    asyncio.run(sam_test())
