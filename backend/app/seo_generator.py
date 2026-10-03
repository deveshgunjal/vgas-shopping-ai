"""Programmatic SEO Page Generator"""
from typing import Dict, List
from pathlib import Path

class SEOGenerator:
    """Auto-generate thousands of SEO landing pages"""
    
    def __init__(self):
        self.template_dir = Path("web/templates")
    
    def generate_deal_page(self, product: Dict) -> str:
        """Generate SEO-optimized deal page"""
        title = f"Best Deals on {product['name']} - {product.get('category', 'Products')}"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="Find the best deals on {product['name']}. Compare prices across Amazon, Flipkart, and more.">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "{product['name']}",
        "offers": {{
            "@type": "Offer",
            "price": "{product.get('price', '0')}",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock"
        }}
    }}
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-white">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold mb-4">{title}</h1>
        <p class="text-gray-400 mb-8">Compare prices and find the best deals.</p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-gray-800 rounded-lg p-6">
                <h3 class="font-bold text-lg mb-2">Current Price</h3>
                <p class="text-3xl text-green-400 font-bold">INR {product.get('price', 'N/A')}</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-6">
                <h3 class="font-bold text-lg mb-2">Best Price</h3>
                <p class="text-3xl text-blue-400 font-bold">INR {product.get('best_price', 'N/A')}</p>
            </div>
            <div class="bg-gray-800 rounded-lg p-6">
                <h3 class="font-bold text-lg mb-2">You Save</h3>
                <p class="text-3xl text-yellow-400 font-bold">INR {product.get('savings', '0')}</p>
            </div>
        </div>
        
        <a href="{product.get('url', '#')}" class="mt-8 inline-block bg-green-600 hover:bg-green-700 px-8 py-3 rounded-lg font-bold">
            Buy Now
        </a>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_category_pages(self, category: str, products: List[Dict]) -> List[str]:
        """Generate pages for all products in a category"""
        pages = []
        for product in products:
            page = self.generate_deal_page(product)
            pages.append(page)
        return pages

seo_generator = SEOGenerator()
