"""
Amazon Scraper for VGAS Shopping AI
"""

from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup
import re
import asyncio
from urllib.parse import urlparse, urljoin
from datetime import datetime
import logging

from app.scrapers.base_scraper import BaseScraper
from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """Scraper for Amazon e-commerce platforms"""

    def __init__(self, country: str = "in"):
        country_map = {
            "in": "India",
            "us": "USA",
            "uk": "UK",
            "de": "Germany",
            "fr": "France",
            "jp": "Japan",
            "ae": "UAE",
            "ca": "Canada",
            "au": "Australia",
        }

        country_name = country_map.get(country, "India")
        currency = {
            "in": "INR",
            "us": "USD",
            "uk": "GBP",
            "de": "EUR",
            "fr": "EUR",
            "jp": "JPY",
            "ae": "AED",
        }.get(country, "INR")

        super().__init__(
            name=f"Amazon {country_name}", country=country_name, currency=currency
        )

        self.country_code = country
        self.base_url = f"https://www.amazon.{country}"
        self.search_url = f"https://www.amazon.{country}/s"

        # Amazon-specific headers
        self.headers.update(
            {
                "Accept-Language": f"en-{country},en;q=0.9",
                "Sec-Fetch-Site": "same-origin",
            }
        )

    async def extract_product_from_url(self, url: str) -> Optional[Dict]:
        """Extract product details from Amazon URL"""
        try:
            # Normalize URL
            url = await self.normalize_url(url)

            # Check if it's an Amazon URL
            domain = await self.extract_domain(url)
            if "amazon" not in domain:
                return None

            # Check cache
            cache_key = CacheKeys.PRODUCT_BY_URL.format(url)
            cached_data = await get_cache(cache_key)
            if cached_data:
                vgas_logger.debug(f"Cache hit for Amazon product: {url}")
                return cached_data

            # Get page
            soup = await self.get_soup(url)
            if not soup:
                return None

            # Extract data
            product_data = {
                "url": url,
                "scraper": self.name,
                "store": "Amazon",
                "store_domain": domain,
                "country": self.country,
                "currency": self.currency,
                "scraped_at": datetime.utcnow().isoformat(),
            }

            # Extract from JSON-LD
            json_ld = await self.extract_json_ld(soup, "Product")
            if json_ld:
                product_data.update(self._extract_from_json_ld(json_ld))

            # Extract title
            title_elem = soup.find("span", {"id": "productTitle"})
            if title_elem:
                product_data["name"] = await self.clean_text(title_elem.get_text())
            if not product_data.get("name") and json_ld:
                product_data["name"] = json_ld.get("name", product_data.get("name"))

            # Ensure image fallback from JSON-LD or page metadata
            if (
                not product_data.get("images")
                or len(product_data.get("images", [])) == 0
            ):
                og_image = soup.find("meta", {"property": "og:image"})
                if og_image and og_image.get("content"):
                    product_data["images"] = [og_image["content"]]
                    product_data["main_image"] = og_image["content"]
            if not product_data.get("image") and product_data.get("main_image"):
                product_data["image"] = product_data.get("main_image")
            price_data = await self._extract_price(soup, json_ld)
            product_data.update(price_data)

            # Extract rating
            rating_data = self._extract_rating(soup)
            product_data.update(rating_data)

            # Extract images
            images_data = self._extract_images(soup)
            product_data.update(images_data)

            # Extract stock
            stock_data = self._extract_stock(soup)
            product_data.update(stock_data)

            # Extract specifications
            specs_data = await self._extract_specifications(soup)
            product_data.update(specs_data)

            # Extract ASIN
            asin_data = self._extract_asin(soup, url)
            product_data.update(asin_data)

            # Generate affiliate URL
            affiliate_url = await self.generate_affiliate_link(url)
            product_data["affiliate_url"] = affiliate_url

            # Cache the result
            await set_cache(cache_key, product_data, expire_seconds=86400)  # 24 hours

            vgas_logger.info(
                f"Scraped Amazon product: {product_data.get('name', 'Unknown')}"
            )

            return product_data

        except Exception as e:
            logger.error(f"Error scraping Amazon URL {url}: {e}")
            return None

    async def search_products(self, query: str, page: int = 1, limit: int = 20) -> Dict:
        """Search products on Amazon"""
        try:
            # Check cache
            cache_key = f"amazon_search:{self.country_code}:{query}:{page}:{limit}"
            cached_result = await get_cache(cache_key)
            if cached_result:
                vgas_logger.debug(f"Cache hit for Amazon search: {query}")
                return cached_result

            # Build search URL
            params = {"k": query, "page": page, "ref": "nb_sb_noss"}

            # Use search URL
            search_url = f"{self.search_url}?k={query}&page={page}"

            # Get page (with small wait so lazy-loaded images appear)
            soup = await self.get_soup(search_url)
            if not soup:
                return {
                    "query": query,
                    "page": page,
                    "results": [],
                    "total": 0,
                    "scraper": self.name,
                }

            # Give lazy-loaded content a moment to render
            try:
                if self.page:
                    await self.page.wait_for_timeout(1500)
                    soup = BeautifulSoup(await self.page.content(), "lxml")
            except Exception:
                pass

            # Extract search results (modern Amazon layout)
            results = []
            items = soup.find_all("div", {"data-component-type": "s-search-result"})
            if not items:
                items = soup.find_all("div", {"class": "s-result-item"})

            for item in items[:limit]:
                product_data = await self._extract_search_result(item, query)
                if product_data:
                    results.append(product_data)

            # Get total results
            total_elem = soup.find("span", {"class": "sg-col-inner"})
            total_text = total_elem.get_text() if total_elem else ""
            total_match = re.search(r"(\d+,?\d+)", total_text)
            total_results = (
                int(total_match.group(1).replace(",", ""))
                if total_match
                else len(results)
            )

            response = {
                "query": query,
                "page": page,
                "limit": limit,
                "total": total_results,
                "results": results,
                "scraper": self.name,
                "store": "Amazon",
                "country": self.country,
                "currency": self.currency,
            }

            # Cache the result
            await set_cache(cache_key, response, expire_seconds=300)  # 5 minutes

            vgas_logger.info(f"Amazon search: {query} -> {len(results)} results")

            return response

        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return {
                "query": query,
                "page": page,
                "results": [],
                "total": 0,
                "scraper": self.name,
            }

    async def generate_affiliate_link(self, product_url: str) -> str:
        """Generate Amazon affiliate link"""
        try:
            # Get affiliate tag from settings
            affiliate_tag = settings.AMAZON_AFFILIATE_ID

            # Parse URL
            parsed = urlparse(product_url)

            # Add or replace tag parameter
            query_params = parsed.query

            # Check if tag already exists
            if f"tag={affiliate_tag}" in query_params:
                return product_url

            # Add tag parameter
            separator = "&" if query_params else "?"
            affiliate_url = f"{product_url}{separator}tag={affiliate_tag}"

            return affiliate_url

        except Exception as e:
            logger.error(f"Error generating Amazon affiliate link: {e}")
            return product_url

    def _extract_from_json_ld(self, json_ld: Dict) -> Dict:
        """Extract product data from JSON-LD"""
        data = {}

        try:
            if "name" in json_ld:
                data["name"] = json_ld["name"]
            if "description" in json_ld:
                data["description"] = json_ld["description"]
            if "brand" in json_ld:
                data["brand"] = json_ld["brand"]
            if "model" in json_ld:
                data["model"] = json_ld["model"]
            if "sku" in json_ld:
                data["sku"] = json_ld["sku"]
            if "category" in json_ld:
                data["category"] = json_ld["category"]
            if "image" in json_ld:
                data["images"] = (
                    [json_ld["image"]]
                    if isinstance(json_ld["image"], str)
                    else json_ld["image"]
                )
            if "aggregateRating" in json_ld:
                rating = json_ld["aggregateRating"]
                data["rating"] = float(rating.get("ratingValue", 0))
                data["rating_count"] = int(rating.get("reviewCount", 0))

            # Extract offers
            if "offers" in json_ld:
                offers = json_ld["offers"]
                if isinstance(offers, dict):
                    offers = [offers]

                for offer in offers:
                    if "price" in offer:
                        data["current_price"] = float(offer["price"])
                    if "priceCurrency" in offer:
                        data["currency"] = offer["priceCurrency"]
                    if "availability" in offer:
                        data["stock_status"] = (
                            "in_stock"
                            if offer["availability"] == "https://schema.org/InStock"
                            else "out_of_stock"
                        )
                    if "url" in offer:
                        data["url"] = offer["url"]

        except Exception as e:
            logger.error(f"Error extracting from JSON-LD: {e}")

        return data

    async def _extract_price(
        self, soup: BeautifulSoup, json_ld: Optional[Dict] = None
    ) -> Dict:
        """Extract price information"""
        data = {}

        try:
            # Current price
            price_elem = soup.find("span", {"class": "a-price-whole"})
            if price_elem:
                price_text = price_elem.get_text().strip()
                currency, amount = await self.extract_currency(price_text)
                data["current_price"] = amount
                data["currency"] = currency

            # Original price (if discounted)
            original_price_elem = soup.find("span", {"class": "a-price-a-offscreen"})
            if not original_price_elem:
                original_price_elem = soup.find(
                    "span", {"class": re.compile(r"a-offscreen")}
                )

            if original_price_elem:
                original_price_text = original_price_elem.get_text().strip()
                currency, amount = await self.extract_currency(original_price_text)
                data["original_price"] = amount
                data["currency"] = currency

            # Discount percentage
            discount_elem = soup.find(
                "span",
                {
                    "class": "a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsInPriceShowing"
                },
            )
            if not discount_elem:
                discount_elem = soup.find(
                    "span", {"class": re.compile(r"savingPrice.*percentage")}
                )

            if discount_elem:
                discount_text = discount_elem.get_text().strip()
                discount_match = re.search(r"(\d+\.?\d*)%", discount_text)
                if discount_match:
                    data["discount_percentage"] = float(discount_match.group(1))

            # If we have both prices but no discount percentage, calculate it
            if (
                "current_price" in data
                and "original_price" in data
                and "discount_percentage" not in data
            ):
                if data["original_price"] > 0:
                    discount = (
                        (data["original_price"] - data["current_price"])
                        / data["original_price"]
                    ) * 100
                    data["discount_percentage"] = round(discount, 2)

            # Shipping cost
            shipping_elem = soup.find("span", {"id": "ourprice_shippingmessage"})
            if shipping_elem:
                shipping_text = shipping_elem.get_text().strip()
                if "free" in shipping_text.lower():
                    data["shipping_cost"] = 0.0
                else:
                    currency, amount = await self.extract_currency(shipping_text)
                    data["shipping_cost"] = amount

            # Try JSON-LD price offers if page selectors fail
            if (
                data.get("current_price", 0) == 0 or data.get("currency") == "INR"
            ) and json_ld:
                offers = json_ld.get("offers")
                if isinstance(offers, dict):
                    if not data.get("current_price"):
                        price = offers.get("price")
                        if price:
                            data["current_price"] = float(price)
                    if not data.get("original_price"):
                        list_price = offers.get("priceCurrency")
                        if list_price and list_price != data.get("currency"):
                            data["currency"] = list_price
                elif isinstance(offers, list) and offers:
                    offer = offers[0]
                    if not data.get("current_price") and offer.get("price"):
                        data["current_price"] = float(offer.get("price"))
                    if not data.get("currency") and offer.get("priceCurrency"):
                        data["currency"] = offer.get("priceCurrency")

        except Exception as e:
            logger.error(f"Error extracting price: {e}")

        return data

    def _extract_rating(self, soup: BeautifulSoup) -> Dict:
        """Extract rating information"""
        data = {}

        try:
            # Rating
            rating_elem = soup.find("i", {"class": "a-icon-star-small"})
            if rating_elem:
                rating_text = rating_elem.get_text().strip()
                rating_match = re.search(r"(\d+\.\d+)", rating_text)
                if rating_match:
                    data["rating"] = float(rating_match.group(1))

            # Rating count
            rating_count_elem = soup.find("span", {"id": "acrCustomerReviewText"})
            if rating_count_elem:
                rating_count_text = rating_count_elem.get_text().strip()
                rating_count_match = re.search(r"(\d+,?\d+)", rating_count_text)
                if rating_count_match:
                    data["rating_count"] = int(
                        rating_count_match.group(1).replace(",", "")
                    )

            # Review count
            review_count_elem = soup.find("span", {"data-hook": "total-review-count"})
            if review_count_elem:
                review_count_text = review_count_elem.get_text().strip()
                review_count_match = re.search(r"(\d+,?\d+)", review_count_text)
                if review_count_match:
                    data["review_count"] = int(
                        review_count_match.group(1).replace(",", "")
                    )

        except Exception as e:
            logger.error(f"Error extracting rating: {e}")

        return data

    def _extract_images(self, soup: BeautifulSoup) -> Dict:
        """Extract product images"""
        data = {}

        try:
            images = []

            # Main image
            main_img_elem = soup.find("img", {"id": "landingImage"})
            if main_img_elem and main_img_elem.get("src"):
                images.append(main_img_elem["src"])

            # Alternative main image
            if not images:
                main_img_elem = soup.find("img", {"class": "a-dynamic-image"})
                if main_img_elem and main_img_elem.get("src"):
                    images.append(main_img_elem["src"])

            # Thumbnail images
            thumbnail_imgs = soup.find_all("img", {"class": "imgThumbnail"})
            for img in thumbnail_imgs:
                if img.get("src") and img["src"] not in images:
                    images.append(img["src"])

            if images:
                data["images"] = images
                data["main_image"] = images[0]

        except Exception as e:
            logger.error(f"Error extracting images: {e}")

        return data

    def _extract_stock(self, soup: BeautifulSoup) -> Dict:
        """Extract stock information"""
        data = {}

        try:
            # Check stock status
            stock_elem = soup.find("div", {"id": "outOfStock"})
            if stock_elem:
                data["stock_status"] = "out_of_stock"
                data["is_in_stock"] = False
            else:
                data["stock_status"] = "in_stock"
                data["is_in_stock"] = True

            # Check for pre-order
            preorder_elem = soup.find("div", {"id": "preorder"})
            if preorder_elem:
                data["stock_status"] = "pre_order"
                data["is_in_stock"] = False

            # Delivery time
            delivery_elem = soup.find("div", {"id": "ddmDeliveryMessage"})
            if delivery_elem:
                delivery_text = delivery_elem.get_text().strip()
                data["estimated_delivery"] = delivery_text

        except Exception as e:
            logger.error(f"Error extracting stock: {e}")

        return data

    async def _extract_specifications(self, soup: BeautifulSoup) -> Dict:
        """Extract product specifications"""
        data = {}

        try:
            specs = {}

            # Product details table
            detail_rows = soup.find_all("tr", {"class": re.compile(r"po-.*")})
            for row in detail_rows:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    key = await self.clean_text(th.get_text())
                    value = await self.clean_text(td.get_text())
                    specs[key] = value

            # Feature bullets
            feature_items = soup.find_all("span", {"class": "a-list-item"})
            for item in feature_items:
                text = await self.clean_text(item.get_text())
                if text and len(specs) < 50:  # Limit to 50 specs
                    # Try to split into key-value
                    if ":" in text:
                        key, value = text.split(":", 1)
                        specs[key.strip()] = value.strip()
                    else:
                        specs[f"Feature {len(specs) + 1}"] = text

            if specs:
                data["specifications"] = specs

            # Extract some common fields
            for key in [
                "Color",
                "Size",
                "Weight",
                "Dimensions",
                "Warranty",
                "Model",
                "Brand",
            ]:
                if key in specs:
                    data[key.lower()] = specs[key]

        except Exception as e:
            logger.error(f"Error extracting specifications: {e}")

        return data

    def _extract_asin(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract ASIN from page or URL"""
        data = {}

        try:
            # Try to find ASIN in URL
            asin_match = re.search(r"/dp/([A-Z0-9]{10})", url)
            if asin_match:
                data["asin"] = asin_match.group(1)
                return data

            # Try to find ASIN in page
            asin_elem = soup.find("input", {"name": "ASIN"})
            if asin_elem and asin_elem.get("value"):
                data["asin"] = asin_elem["value"]

            # Try to find in data-asin attribute
            asin_elem = soup.find(attrs={"data-asin": True})
            if asin_elem and asin_elem.get("data-asin"):
                data["asin"] = asin_elem["data-asin"]

        except Exception as e:
            logger.error(f"Error extracting ASIN: {e}")

        return data

    def _upgrade_image_url(self, image_url: str) -> str:
        """Upgrade Amazon thumbnail image URL to a larger size for display"""
        if not image_url:
            return image_url
        # Replace small thumbnails (_AC_UY218_, _AC_UL320_ etc.) with a larger version
        return re.sub(r"\._(?:AC|UL)[A-Z0-9_]*_", "._SL500_", image_url)

    async def _extract_search_result(
        self, item: BeautifulSoup, query: str
    ) -> Optional[Dict]:
        """Extract product data from search result item (modern Amazon layout)"""
        try:
            data = {
                "scraper": self.name,
                "store": "Amazon",
                "store_domain": self.base_url,
                "country": self.country,
                "currency": self.currency,
                "scraped_at": datetime.utcnow().isoformat(),
            }

            # Title (modern layout: h2 > span, fallback to old layout)
            title_elem = item.find("h2", recursive=True)
            if title_elem:
                name_span = title_elem.find("span")
                if name_span:
                    data["name"] = await self.clean_text(name_span.get_text())
                if not data.get("name"):
                    data["name"] = await self.clean_text(title_elem.get_text())
            if not data.get("name"):
                title_elem = item.find(
                    "span", {"class": re.compile(r"a-text-normal|a-size-medium")}
                )
                if title_elem:
                    data["name"] = await self.clean_text(title_elem.get_text())

            # URL (prefer direct /dp/ product link over sponsored /sspa/ links)
            link_elem = None
            direct_link = item.find(
                "a", href=re.compile(r"/dp/[A-Z0-9]{10}"), recursive=True
            )
            if direct_link:
                link_elem = direct_link
            else:
                link_elem = item.find("a", {"class": "a-link-normal"}, href=True)
            if link_elem and link_elem.get("href"):
                url = urljoin(self.base_url, link_elem["href"])
                # Keep only the base product URL (strip tracking params)
                dp_match = re.search(r"(https?://[^/]+/[^/]+/dp/[A-Z0-9]{10})", url)
                if dp_match:
                    url = dp_match.group(1)
                data["url"] = url

            # Price (modern layout: span.a-price > span.a-offscreen)
            price_el = item.select_one(".a-price .a-offscreen")
            if not price_el:
                # Fallback: priceblock IDs (common on Amazon)
                price_el = item.find("span", {"id": re.compile(r"priceblock_(ourprice|dealprice)")})
            if not price_el:
                # Fallback: data-price attribute
                price_el = item.find(attrs={"data-price": True})
            if price_el:
                price_text = price_el.get_text().strip() if price_el.get_text() else str(price_el.get("data-price", ""))
                currency, amount = await self.extract_currency(price_text)
                data["current_price"] = amount
                data["currency"] = currency

            # Original price (modern layout)
            original_price_elem = item.find(
                "span", {"class": "a-price-a-offscreen"}
            )
            if not original_price_elem:
                # Strikes/other price blocks
                for sp in item.find_all("span", {"class": "a-offscreen"}):
                    text = sp.get_text().strip()
                    if text and "₹" in text and sp is not price_el:
                        currency, amount = await self.extract_currency(text)
                        if amount and amount < data.get("current_price", 0):
                            continue
                        if amount:
                            data["original_price"] = amount
                            break

            # Discount percentage badge
            discount_elem = item.find(
                "span", {"class": re.compile(r"savingsPercentage|a-color-price")}
            )
            if discount_elem:
                discount_text = discount_elem.get_text().strip()
                discount_match = re.search(r"(\d+\.?\d*)%", discount_text)
                if discount_match:
                    data["discount_percentage"] = float(discount_match.group(1))

            # Image (modern layout: img.s-image)
            img_elem = item.find("img", {"class": "s-image"}, src=True)
            if not img_elem:
                img_elem = item.find("img", src=True)
            if img_elem and img_elem.get("src"):
                data["image"] = self._upgrade_image_url(img_elem["src"])

            # Rating (modern layout: a-icon-star-small > a-icon-alt)
            rating_elem = item.find("i", {"class": "a-icon-star-small"})
            if not rating_elem:
                rating_elem = item.find("i", {"class": re.compile(r"a-icon-star")})
            if rating_elem:
                rating_text = rating_elem.get_text().strip()
                rating_match = re.search(r"(\d+\.\d)", rating_text)
                if rating_match:
                    data["rating"] = float(rating_match.group(1))

            # Rating count (modern layout)
            rating_count_elem = item.find(
                "span", {"class": "a-size-base s-underline-text"}
            )
            if not rating_count_elem:
                rating_count_elem = item.find("span", {"class": "a-size-small"})
            if rating_count_elem:
                rating_count_text = rating_count_elem.get_text().strip()
                rating_count_match = re.search(r"(\d+,?\d+)", rating_count_text)
                if rating_count_match:
                    data["rating_count"] = int(
                        rating_count_match.group(1).replace(",", "")
                    )

            # Brand (modern layout)
            brand_elem = item.find("span", {"class": "a-size-base-plus a-color-base"})
            if not brand_elem:
                brand_elem = item.find("span", {"class": "a-size-small a-color-base"})
            if brand_elem:
                data["brand"] = await self.clean_text(brand_elem.get_text())

            # Compute discount if not found but both prices present
            if (
                data.get("original_price")
                and data.get("current_price")
                and not data.get("discount_percentage")
                and data["original_price"] > data["current_price"]
            ):
                data["discount_percentage"] = round(
                    ((data["original_price"] - data["current_price"])
                     / data["original_price"]) * 100, 2
                )

            # Generate affiliate URL
            if "url" in data:
                data["affiliate_url"] = await self.generate_affiliate_link(data["url"])

            # Stock status
            data["is_in_stock"] = True
            data["stock_status"] = "in_stock"

            # Check if valid (skip sponsored-only cards without direct product link)
            if not data.get("name") or not data.get("url") or "sspa/click" in data.get("url", ""):
                return None

            return data

        except Exception as e:
            logger.error(f"Error extracting Amazon search result: {e}")
            return None
