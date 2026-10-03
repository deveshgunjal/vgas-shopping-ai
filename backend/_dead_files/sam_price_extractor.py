# -*- coding: utf-8 -*-
"""SAM PRICE EXTRACTOR - Real Prices from HTML"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")

def extract_prices(html, platform):
    """Extract rupee prices from HTML"""
    prices = []
    
    # Pattern: ₹ followed by digits (with optional commas)
    pattern = r'₹\s*([\d,]+(?:\.\d+)?)'
    matches = re.findall(pattern, html)
    
    for m in matches:
        try:
            price = float(m.replace(',', ''))
            # Filter realistic prices (100 to 500000 INR)
            if 100 < price < 500000:
                prices.append(price)
        except:
            continue
    
    prices = sorted(set(prices))
    return prices[:10]  # Return top 10 unique prices

# Sample HTML snippets from platforms
sample_html = {
    "Flipkart": """
        <div class="_1psv1ze2c">₹23,999</div>
        <div class="_1psv1zekc">₹76,900</div>
        <div class="Nx9bqj">₹24,999</div>
    """,
    "Amazon": """
        <span class="a-price-whole">₹25,999</span>
        <span class="a-price-audio">₹79,999</span>
    """,
    "Meesho": """
        <h5>₹19,999</h5>
        <span>₹29,999</span>
    """
}

print("💰 SAM PRICE EXTRACTOR - Real Prices")
print("=" * 60)

for platform, html in sample_html.items():
    prices = extract_prices(html, platform)
    if prices:
        print(f"\n{platform}:")
        print(f"  Lowest: ₹{prices[0]:,.0f}")
        print(f"  Highest: ₹{prices[-1]:,.0f}")
        if len(prices) > 1:
            discount = round(((prices[-1] - prices[0]) / prices[-1]) * 100)
            print(f"  Discount: {discount}%")

print("\n✅ SAM Multi-Platform Price Extraction Ready!")
