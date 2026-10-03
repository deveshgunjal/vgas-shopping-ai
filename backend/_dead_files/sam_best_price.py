# SAM MULTI-PLATFORM v2 - ALL AT ONCE
import requests, re, sys
sys.stdout.reconfigure(encoding="utf-8")

def get_flipkart():
    try:
        h = {"User-Agent": "Mozilla/5.0 Chrome/124.0.0.0"}
        r = requests.get("https://www.flipkart.com/search?q=samsung+galaxy+s24&sort=price_asc", headers=h, timeout=12)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        prices = []
        for el in soup.find_all(["div","span"], class_=True):
            t = el.get_text(strip=True)
            if "₹" in t:
                nums = re.findall(r"[\d,]+", t)
                if nums:
                    v = float(nums[0].replace(",",""))
                    if 5000 < v < 500000: prices.append(v)
        return ("FLIPKART", min(prices) if prices else 0, max(prices) if prices else 0)
    except Exception as e:
        return ("FLIPKART", 0, 0)

def get_amazon():
    try:
        h = {"User-Agent": "Mozilla/5.0 Chrome/124.0.0.0"}
        r = requests.get("https://www.amazon.in/s?k=samsung+galaxy+s24", headers=h, timeout=12)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        prices = []
        for el in soup.find_all("span", class_="a-price-whole"):
            t = el.get_text(strip=True).replace(",","")
            if t.isdigit():
                v = float(t)
                if 5000 < v < 500000: prices.append(v)
        return ("AMAZON", min(prices) if prices else 0, max(prices) if prices else 0)
    except:
        return ("AMAZON", 0, 0)

def get_meesho():
    try:
        h = {"User-Agent": "Mozilla/5.0 Chrome/124.0.0.0"}
        r = requests.get("https://www.meesho.com/search?q=samsung+galaxy+s24", headers=h, timeout=12)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        prices = []
        for el in soup.find_all(["h5","span"]):
            t = el.get_text()
            if "₹" in t:
                nums = re.findall(r"[\d,]+", t)
                if nums:
                    v = float(nums[0].replace(",",""))
                    if 5000 < v < 500000: prices.append(v)
        return ("MEESHO", min(prices) if prices else 0, max(prices) if prices else 0)
    except:
        return ("MEESHO", 0, 0)

print("=" * 60)
print("SAMSUNG GALAXY S24 - BEST PRICES")
print("=" * 60)

fk = get_flipkart()
am = get_amazon()
me = get_meesho()

all_results = [fk, am, me]

for name, low, high in all_results:
    if low > 0:
        disc = int(((high - low) / high) * 100) if high > 0 else 0
        print(f"{name}: Rs {low:,} - Rs {high:,} | {disc}% OFF")

# Find cheapest
cheapest = min([r for r in all_results if r[1] > 0], key=lambda x: x[1])
print()
print(f"🏆 CHEAPEST: {cheapest[0]} at Rs {cheapest[1]:,}")
print("=" * 60)