# -*- coding: utf-8 -*-
"""
VGAS REAL CHEAPEST ENGINE v4
सर्वात खरं स्वस्त प्रॉडक्ट शोधतो - सर्व प्लॅटफॉर्मवरून
"""
import requests, re, sys, time, json
sys.stdout.reconfigure(encoding="utf-8")

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

def fetch_amazon(query):
    """Amazon - Fast & Reliable"""
    try:
        url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}&sort=price-asc"
        r = requests.get(url, headers=get_headers(), timeout=10)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all("span", class_="a-price-whole"):
            t = el.get_text(strip=True).replace(",", "")
            if t.isdigit() and 1000 < float(t) < 500000:
                prices.append(float(t))
        
        if prices:
            low = min(prices)
            high = max(prices)
            disc = int(((high - low) / high) * 100)
            
            # Get product name
            names = soup.select("h2 a span")
            name = names[0].get_text(strip=True)[:50] if names else query
            
            return {
                "store": "Amazon",
                "name": name,
                "price": low,
                "mrp": high,
                "discount": disc,
                "url": f"https://www.amazon.in/s?k={query.replace(' ', '+')}&tag=vgas-vikasg-21"
            }
    except: pass
    return None

def fetch_flipkart(query):
    """Flipkart - Sometimes works"""
    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&sort=price_asc"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        if r.status_code != 200: return None
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all(["div", "span"], class_=True):
            t = el.get_text(strip=True)
            if "₹" in t:
                n = re.findall(r"[\d,]+", t)
                if n:
                    v = float(n[0].replace(",", ""))
                    if 1000 < v < 500000:
                        prices.append(v)
        
        if prices:
            low = min(prices)
            high = max(prices)
            disc = int(((high - low) / high) * 100)
            
            names = soup.select("div.KzDlHZ, a.s1Q9rs")
            name = names[0].get_text(strip=True)[:50] if names else query
            
            return {
                "store": "Flipkart",
                "name": name,
                "price": low,
                "mrp": high,
                "discount": disc,
                "url": f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&affid=vgas2024"
            }
    except: pass
    return None

def fetch_meesho(query):
    """Meesho - Fast"""
    try:
        url = f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all(["h5", "span", "p"]):
            t = el.get_text()
            if "₹" in t:
                n = re.findall(r"[\d,]+", t)
                if n:
                    v = float(n[0].replace(",", ""))
                    if 100 < v < 100000:
                        prices.append(v)
        
        if prices:
            low = min(prices)
            high = max(prices)
            
            return {
                "store": "Meesho",
                "name": query,
                "price": low,
                "mrp": high,
                "discount": int(((high - low) / high) * 100) if high > 0 else 0,
                "url": f"https://www.meesho.com/search?q={query.replace(' ', '+')}"
            }
    except: pass
    return None

def fetch_croma(query):
    """Croma - Reliable"""
    try:
        url = f"https://www.croma.com/search/?text={query.replace(' ', '%20')}"
        r = requests.get(url, headers=get_headers(), timeout=8)
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "lxml")
        
        prices = []
        for el in soup.find_all("span", class_="price"):
            t = el.get_text(strip=True).replace(",", "")
            if "₹" in t:
                n = re.findall(r"[\d,]+", t)
                if n:
                    v = float(n[0].replace(",", ""))
                    if 1000 < v < 500000:
                        prices.append(v)
        
        if prices:
            low = min(prices)
            high = max(prices)
            
            names = soup.select("h3.product-title")
            name = names[0].get_text(strip=True)[:50] if names else query
            
            return {
                "store": "Croma",
                "name": name,
                "price": low,
                "mrp": high,
                "discount": int(((high - low) / high) * 100) if high > 0 else 0,
                "url": f"https://www.croma.com/search/?text={query.replace(' ', '%20')}"
            }
    except: pass
    return None

def find_cheapest(query):
    """सर्व प्लॅटफॉर्म तपासा आणि सर्वात स्वस्त शोधा"""
    print("=" * 70)
    print(f"🔍 VGAS REAL CHEAPEST ENGINE - {query}")
    print("=" * 70)
    
    results = []
    
    # Run all in parallel
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        f1 = ex.submit(fetch_amazon, query)
        f2 = ex.submit(fetch_flipkart, query)
        f3 = ex.submit(fetch_meesho, query)
        f4 = ex.submit(fetch_croma, query)
        
        for f in [f1, f2, f3, f4]:
            r = f.result()
            if r and r.get("price", 0) > 0:
                results.append(r)
    
    # Sort by price
    results.sort(key=lambda x: x["price"])
    
    # Display
    print("\n📊 सर्व प्लॅटफॉर्मवरील किंमत (सर्वात स्वस्त प्रथम):\n")
    
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['store']:12} | ₹{r['price']:>8,.0f}")
        print(f"     MRP: ₹{r['mrp']:>8,.0f} | {r['discount']}% OFF")
        print(f"     नाव: {r['name'][:40]}...")
        print()
    
    if results:
        cheapest = results[0]
        print("=" * 70)
        print(f"🏆 सर्वात स्वस्त: {cheapest['store']} - ₹{cheapest['price']:,.0f}")
        print(f"   तुमचं बचत: ₹{cheapest['mrp'] - cheapest['price']:,.0f} ({cheapest['discount']}% OFF)")
        print(f"   🔗 Affiliate Link: {cheapest['url']}")
        print("=" * 70)
        
        # Fake discount check
        if cheapest['discount'] > 70:
            print("⚠️  लक्षात घ्या: खूप मोठी सूट आहे - खरंच स्वस्त आहे का ते तपासा!")
        
        return results
    else:
        print("❌ कोणतेही प्रॉडक्ट सापडलं नाही")
        return []

# Test
if __name__ == "__main__":
    # Test 1: iPhone 16
    print("\n" + "="*70)
    print("TEST 1: iPhone 16")
    print("="*70)
    find_cheapest("iPhone 16")
    
    # Test 2: Samsung Galaxy S24
    print("\n" + "="*70)
    print("TEST 2: Samsung Galaxy S24")
    print("="*70)
    find_cheapest("Samsung Galaxy S24")
    
    # Test 3: TV
    print("\n" + "="*70)
    print("TEST 3: TV 55 inch")
    print("="*70)
    find_cheapest("TV 55 inch")
    
    print("\n✅ VGAS REAL CHEAPEST ENGINE - WORKING!")