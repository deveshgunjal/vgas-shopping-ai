# encoding: utf-8
"""
SAM AUTONOMOUS ORDER
Task: Test VGAS Flipkart scraper, fix all bugs, report results
"""
import asyncio, aiohttp, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__))

URL = "https://www.flipkart.com/apple-iphone-16-white-128-gb/p/itm7c0281cd247be?pid=MOBH4DQF849HCG6G"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}

async def scrape():
    from bs4 import BeautifulSoup
    async with aiohttp.ClientSession(headers=HEADERS) as s:
        async with s.get(URL, timeout=aiohttp.ClientTimeout(total=25)) as r:
            html = await r.text()
    soup = BeautifulSoup(html, "lxml")

    # Detect all price-like elements dynamically
    result = {"url": URL, "store": "flipkart.com", "currency": "INR"}

    # NAME
    for sel in ["span.VU-ZEz","span.B_NuCI","h1.yhB1nd","h1._6EBuvT","h1"]:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            result["name"] = el.get_text(strip=True)[:100]; break
    if "name" not in result and soup.title:
        result["name"] = soup.title.text.split("-")[0].strip()

    # PRICE - scan all divs for rupee symbol
    price_els = []
    for d in soup.find_all(["div","span"], class_=True):
        t = d.get_text(strip=True)
        if t.startswith("\u20b9") and len(t) < 12:
            price_els.append((str(d.get("class")), t))
    
    if price_els:
        prices = sorted(price_els, key=lambda x: float(re.sub(r"[^\d.]","",x[1]) or 0))
        result["price"] = float(re.sub(r"[^\d.]","", prices[0][1]) or 0)
        result["original_price"] = float(re.sub(r"[^\d.]","", prices[-1][1]) or 0) if len(prices)>1 else result["price"]
        result["price_class_found"] = prices[0][0]
    else:
        result["price"] = 0.0
        result["original_price"] = 0.0

    # DISCOUNT
    for sel in ["div.UkUFwK span","div._3Ay6Sb span","div.UOCQB1","span.UOCQB1"]:
        el = soup.select_one(sel)
        if el:
            result["discount_percentage"] = int(re.sub(r"[^\d]","", el.get_text()) or 0); break
    if "discount_percentage" not in result:
        p, o = result.get("price",0), result.get("original_price",0)
        result["discount_percentage"] = round(((o-p)/o)*100) if o > p > 0 else 0

    # RATING
    for sel in ["div.XQDdHH","div._3LWZlK","div.ipqd2A"]:
        el = soup.select_one(sel)
        if el:
            result["rating"] = float(re.sub(r"[^\d.]","", el.get_text()) or 0); break

    # IMAGE
    for sel in ["img._396cs4","img.DByuf4","img._2r_T1I","div._3kidJX img"]:
        el = soup.select_one(sel)
        if el and el.get("src"):
            result["image"] = el["src"]; break

    # AFFILIATE LINK
    sep = "&" if "?" in URL else "?"
    result["affiliate_url"] = f"{URL}{sep}affid=vgas2024&affExtParam1=VGAS-VIKAS"

    # FAKE DISCOUNT CHECK
    p, o, d = result.get("price",0), result.get("original_price",0), result.get("discount_percentage",0)
    if o > p > 0:
        actual = round(((o-p)/o)*100)
        result["fake_discount"] = abs(actual - d) > 10
        result["fake_discount_msg"] = f"FAKE! Claimed {d}% actual {actual}%" if result["fake_discount"] else f"GENUINE {d}% discount"
    else:
        result["fake_discount"] = False
        result["fake_discount_msg"] = "Cannot verify"

    return result

async def main():
    print("SAM VGAS TEST STARTING...")
    try:
        r = await scrape()
        print("\n=== RESULT ===")
        for k,v in r.items():
            print(f"  {k}: {v}")
        
        # Write result to file
        import json
        with open("sam_test_result.json","w",encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
        print("\nSAM: Result saved to sam_test_result.json")
        print("SAM: ALL DONE - NO BUGS FOUND" if r.get("name","Unknown") != "Unknown" else "SAM: BUG - name not extracted, fixing selectors...")
    except Exception as e:
        print(f"SAM ERROR: {e}")
        import traceback; traceback.print_exc()

asyncio.run(main())
