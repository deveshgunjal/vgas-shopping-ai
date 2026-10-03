"""
Ajio Scraper for VGAS Shopping AI
Scrapes product data from ajio.com
"""

from app.scrapers.base_scraper import BaseScraper
from typing import Dict, List, Optional
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class AjioScraper(BaseScraper):
    """Scraper for Ajio.com"""

    def __init__(self):
        super().__init__(name="Ajio", country="in", currency="INR")
        self.base_url = "https://www.ajio.com"
        self.search_url = "https://www.ajio.com/search/?text="
        self.affiliate_tag = ""

    async def search_products(self, query: str, page: int = 1, limit: int = 20) -> Dict:
        """Search products on Ajio"""
        results = []
        try:
            search_url = f"{self.search_url}{query.replace(' ', '%20')}"
            soup = await self.get_soup(search_url)

            if not soup:
                return {"query": query, "page": page, "limit": limit, "results": [], "total": 0, "scraper": self.name}

            # Extract product cards
            product_cards = soup.select("div.item, div.rilrtl-products-list__item, div._1B4v3, div.product-card")

            for card in product_cards[:limit]:
                try:
                    product = await self._parse_product_card(card)
                    if product:
                        results.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing Ajio product card: {e}")
                    continue

        except Exception as e:
            logger.error(f"Ajio search error: {e}")

        return {
            "query": query,
            "page": page,
            "limit": limit,
            "results": results,
            "total": len(results),
            "scraper": self.name
        }

    async def _parse_product_card(self, card) -> Optional[Dict]:
        """Parse a product card element"""
        try:
            # Product name
            name_el = card.select_one("div.nameCls, .brand, .product-name, h3")
            name = await self.clean_text(name_el.get_text()) if name_el else None
            if not name:
                return None

            # Price
            price_el = card.select_one("span.price, .orginal-price, .sale-price")
            price_text = price_el.get_text() if price_el else "0"
            _, current_price = await self.extract_currency(price_text)

            # Original price
            orig_el = card.select_one("span.orginal-price, .strike-price, del")
            orig_text = orig_el.get_text() if orig_el else "0"
            _, original_price = await self.extract_currency(orig_text)
            if original_price == 0:
                original_price = current_price

            # Discount
            discount_el = card.select_one("span.discount, .offer-text")
            discount_text = discount_el.get_text() if discount_el else ""
            discount_pct = 0
            if discount_text:
                nums = re.findall(r'\d+', discount_text)
                if nums:
                    discount_pct = int(nums[0])
            elif original_price > current_price > 0:
                discount_pct = round((1 - current_price / original_price) * 100)

            # Image
            img_el = card.select_one("img")
            image = img_el.get("src", "") or img_el.get("data-src", "") if img_el else ""
            if image and not image.startswith("http"):
                image = f"https:{image}" if image.startswith("//") else f"{self.base_url}{image}"

            # URL
            link_el = card.select_one("a")
            url = link_el.get("href", "") if link_el else ""
            if url and not url.startswith("http"):
                url = f"{self.base_url}{url}"

            # Rating
            rating_el = card.select_one("span.rating, .star-rating")
            rating = 0.0
            if rating_el:
                rating_nums = re.findall(r'[\d.]+', rating_el.get_text())
                if rating_nums:
                    rating = float(rating_nums[0])

            return {
                "name": name,
                "price": current_price,
                "current_price": current_price,
                "original_price": original_price,
                "discount_percentage": discount_pct,
                "currency": "INR",
                "image": image,
                "url": url,
                "affiliate_url": url,
                "store": "Ajio",
                "rating": rating,
                "in_stock": True,
                "scraped_at": datetime.utcnow().isoformat(),
                "scraper": self.name,
                "fake_discount": False
            }

        except Exception as e:
            logger.error(f"Error parsing Ajio product: {e}")
            return None

    async def extract_product_from_url(self, url: str) -> Optional[Dict]:
        """Extract product details from Ajio product URL"""
        try:
            soup = await self.get_soup(url)
            if not soup:
                return None

            # Try JSON-LD first
            json_ld = await self.extract_json_ld(soup)
            if json_ld:
                name = json_ld.get("name", "")
                offers = json_ld.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}

                current_price = float(offers.get("price", 0))
                currency = offers.get("priceCurrency", "INR")
                image = json_ld.get("image", "")
                if isinstance(image, list):
                    image = image[0] if image else ""

                return {
                    "name": name,
                    "price": current_price,
                    "current_price": current_price,
                    "original_price": current_price,
                    "discount_percentage": 0,
                    "currency": currency,
                    "image": image,
                    "url": url,
                    "affiliate_url": url,
                    "store": "Ajio",
                    "rating": float(json_ld.get("aggregateRating", {}).get("ratingValue", 0)),
                    "in_stock": offers.get("availability", "").lower() != "outofstock",
                    "description": json_ld.get("description", ""),
                    "brand": json_ld.get("brand", {}).get("name", ""),
                    "scraped_at": datetime.utcnow().isoformat(),
                    "scraper": self.name,
                    "fake_discount": False
                }

            # Fallback: HTML parsing
            name_el = soup.select_one("h1.prod-name, h1, .prod-header-section h1")
            name = await self.clean_text(name_el.get_text()) if name_el else "Unknown Product"

            price_el = soup.select_one("span.prod-sp, .sale-price, .prod-price")
            price_text = price_el.get_text() if price_el else "0"
            _, current_price = await self.extract_currency(price_text)

            orig_el = soup.select_one("span.prod-cp, .prod-strike, .original-price")
            orig_text = orig_el.get_text() if orig_el else "0"
            _, original_price = await self.extract_currency(orig_text)
            if original_price == 0:
                original_price = current_price

            img_el = soup.select_one("img.rilrtl-lazy-img, .zoom-image img, .product-image img")
            image = img_el.get("src", "") if img_el else ""

            discount_pct = 0
            if original_price > current_price > 0:
                discount_pct = round((1 - current_price / original_price) * 100)

            # Fake discount detection
            fake_result = await self.detect_fake_discount({
                "current_price": current_price,
                "original_price": original_price,
                "discount_percentage": discount_pct
            })

            return {
                "name": name,
                "price": current_price,
                "current_price": current_price,
                "original_price": original_price,
                "discount_percentage": discount_pct,
                "currency": "INR",
                "image": image,
                "url": url,
                "affiliate_url": url,
                "store": "Ajio",
                "rating": 0.0,
                "in_stock": True,
                "scraped_at": datetime.utcnow().isoformat(),
                "scraper": self.name,
                "fake_discount": fake_result.get("is_fake_discount", False),
                "fake_discount_details": fake_result
            }

        except Exception as e:
            logger.error(f"Ajio URL extraction error: {e}")
            return None

    async def generate_affiliate_link(self, product_url: str) -> str:
        """Generate affiliate link for Ajio"""
        # Ajio affiliate links are typically through EarnKaro or Cuelinks
        return product_url
