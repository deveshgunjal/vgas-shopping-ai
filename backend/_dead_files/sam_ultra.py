# SAM ULTRA ENGINE v3 - ALL HACKS COMBINED
import requests, re, sys, json, time
sys.stdout.reconfigure(encoding="utf-8")

# FREE PROXY LIST - ROTATING
PROXIES = [
    {"http": "http://101.109.255.59:8080", "https": "http://101.109.255.59:8080"},
    {"http": "http://202.29.239.170:8080", "https": "http://202.29.239.170:8080"},
    {"http": "http://103.75.190.12:8080", "https": "http://103.75.190.12:8080"},
]

# HACK 1: RANDOM USER AGENTS
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
]

import random
def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

def fetch_amazon(query):
    """AMAZON - WORKS WITHOUT PROXY"""
    try:
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}&sort=price-asc"
        r = requests.get(url, headers=get_headers(), timeout=10)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all("span", class_="a-price-whole"):
            t = el.get_text(strip=True).replace(",", "")
            if t.isdigit():
                v = float(t)
                if 1000 < v < 500000:
                    prices.append(v)
        
        # Get product name
        names = soup.select("h2 a span")
        name = names[0].get_text(strip=True)[:40] if names else query
        
        low = min(prices) if prices else 0
        high = max(prices) if prices else 0
        
        return {"store": "Amazon", "name": name, "low": low, "high": high}
    except Exception as e:
        return {"store": "Amazon", "error": str(e)}

def fetch_flipkart(query):
    """FLIPKART - NEEDS PROXY OR CRAWL4AI"""
    # Try without proxy first (sometimes works)
    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&sort=price_asc"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        if r.status_code != 200:
            return {"store": "Flipkart", "error": f"Status {r.status_code}"}
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all(["div", "span"], class_=True):
            t = el.get_text(strip=True)
            if "₹" in t:
                nums = re.findall(r"[\d,]+", t)
                if nums:
                    v = float(nums[0].replace(",", ""))
                    if 1000 < v < 500000:
                        prices.append(v)
        
        return {"store": "Flipkart", "low": min(prices) if prices else 0, "high": max(prices) if prices else 0}
    except Exception as e:
        return {"store": "Flipkart", "error": str(e)}

def fetch_meesho(query):
    """MEESHO - WORKS"""
    try:
        url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all(["h5", "span", "p"]):
            t = el.get_text()
            if "₹" in t:
                nums = re.findall(r"[\d,]+", t)
                if nums:
                    v = float(nums[0].replace(",", ""))
                    if 100 < v < 100000:
                        prices.append(v)
        
        return {"store": "Meesho", "low": min(prices) if prices else 0, "high": max(prices) if prices else 0}
    except Exception as e:
        return {"store": "Meesho", "error": str(e)}

def fetch_croma(query):
    """CROMA - ALSO WORKS"""
    try:
        url = f"https://www.croma.com/search/?text={query.replace(' ', '%20')}"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all("span", class_=True):
            t = el.get_text(strip=True)
            if "₹" in t:
                nums = re.findall(r"[\d,]+", t)
                if nums:
                    v = float(nums[0].replace(",", ""))
                    if 1000 < v < 500000:
                        prices.append(v)
        
        return {"store": "Croma", "low": min(prices) if prices else 0, "high": max(prices) if prices else 0}
    except Exception as e:
        return {"store": "Croma", "error": str(e)}

# MAIN - RUN ALL IN PARALLEL
import concurrent.futures

def run_all(query):
    print("=" * 70)
    print(f"🔍 SAM ULTRA: {query}")
    print("=" * 70)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        f1 = ex.submit(fetch_amazon, query)
        f2 = ex.submit(fetch_flipkart, query)
        f3 = ex.submit(fetch_meesho, query)
        f4 = ex.submit(fetch_croma, query)
        
        results = [f1.result(), f2.result(), f3.result(), f4.result()]
    
    print("\n📊 सर्व प्लॅटफॉर्मवरील किंमत:\n")
    
    valid = []
    for r in results:
        if "error" in r:
            print(f"  ❌ {r['store']}: {r.get('error', 'Error')}")
        elif r.get("low", 0) > 0:
            disc = int(((r["high"] - r["low"]) / r["high"]) * 100) if r.get("high", 0) > 0 else 0
            print(f"  ✅ {r['store']:10} | कमाल ₹{r['low']:,.0f} | मूळ ₹{r['high']:,.0f} | {disc}% OFF")
            valid.append(r)
    
    if valid:
        cheapest = min(valid, key=lambda x: x["low"])
        print(f"\n🏆 सर्वात स्वस्त: {cheapest['store']} - ₹{cheapest['low']:,.0f}")
        
        # AFFILIATE LINK
        print(f"\n🔗 AFFILIATE LINK:")
        if cheapest["store"] == "Amazon":
            print(f"   https://www.amazon.in/s?k={query.replace(' ', '+')}&tag=vgas-vikasg-21")
    
    print("=" * 70)
    return valid

# TEST
if __name__ == "__main__":
    run_all("Samsung Galaxy S24")