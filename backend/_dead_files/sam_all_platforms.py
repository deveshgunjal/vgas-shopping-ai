# FAST MULTI-PLATFORM TEST
import requests, re, sys, concurrent.futures
sys.stdout.reconfigure(encoding="utf-8")

headers = {"User-Agent": "Mozilla/5.0 Chrome/124.0.0.0"}

def get_flipkart():
    try:
        r = requests.get("https://www.flipkart.com/search?q=samsung+galaxy+s24&sort=price_asc", headers=headers, timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        prices = []
        for t in soup.find_all(["div","span"], class_=True):
            txt = t.get_text(strip=True)
            if re.match(r"^₹[\d,]+$", txt):
                v = float(re.sub(r"[^0-9]","",txt))
                if 5000 < v < 500000: prices.append(v)
        return ("Flipkart", min(prices) if prices else 0, max(prices) if prices else 0)
    except: return ("Flipkart", 0, 0)

def get_amazon():
    try:
        r = requests.get("https://www.amazon.in/s?k=samsung+galaxy+s24&sort=price-asc", headers=headers, timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        prices = [float(re.sub(r"[^0-9]","",t.get_text())) for t in soup.find_all("span", class_="a-price-whole") if 5000<float(re.sub(r"[^0-9]","",t.get_text()))<500000]
        return ("Amazon", min(prices) if prices else 0, max(prices) if prices else 0)
    except: return ("Amazon", 0, 0)

def get_meesho():
    try:
        r = requests.get("https://www.meesho.com/search?q=samsung+galaxy+s24", headers=headers, timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        prices = []
        for t in soup.find_all(["h5","span","div"]):
            txt = t.get_text()
            if "₹" in txt:
                v = float(re.sub(r"[^0-9]","",txt))
                if 5000 < v < 500000: prices.append(v)
        return ("Meesho", min(prices) if prices else 0, max(prices) if prices else 0)
    except: return ("Meesho", 0, 0)

print("Testing 3 platforms simultaneously...")
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    results = list(ex.map(lambda f: f(), [get_flipkart, get_amazon, get_meesho]))

print()
print("=" * 60)
print("SAMSUNG GALAXY S24 - ALL PLATFORMS")
print("=" * 60)
for name, low, high in results:
    if low > 0:
        disc = int(((high - low) / high) * 100) if high > 0 else 0
        print(f"{name:12} LOW: Rs {low:>7,.0f}  HIGH: Rs {high:>7,.0f}  DISCOUNT: {disc}%")
print("=" * 60)