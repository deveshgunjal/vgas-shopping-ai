# FAST SAM - Simple requests, no browser
import requests, re, sys
sys.stdout.reconfigure(encoding="utf-8")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Accept": "text/html"
}

# FAST test - Flipkart search
url = "https://www.flipkart.com/search?q=samsung+galaxy+s24&sort=price_asc"
print("FAST SAM - Fetching...")
r = requests.get(url, headers=headers, timeout=10)

from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, "lxml")

# Extract prices
prices = []
for el in soup.find_all(["div","span"], class_=True):
    t = el.get_text(strip=True)
    if re.match(r'^₹[\d,]+$', t):
        v = float(re.sub(r'[^0-9.]','',t))
        if 5000 < v < 500000:
            prices.append(v)

prices = sorted(set(prices))

print("=" * 60)
print("PRODUCT: Samsung Galaxy S24")
print("PLATFORM: Flipkart")
print("=" * 60)
if prices:
    print(f"LOWEST: Rs {prices[0]:,.0f}")
    print(f"HIGHEST: Rs {prices[-1]:,.0f}")
    if len(prices)>1:
        print(f"DISCOUNT: {round(((prices[-1]-prices[0])/prices[-1])*100)}%")
print("=" * 60)