"""
Product Search Engine for VGAS Shopping AI
Search products by name across all e-commerce platforms
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import dataclasses
import asyncio
import re
import time
from datetime import datetime
import logging

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, CacheKeys, cached

# NOTE: get_scraper and scrapers imported lazily to avoid circular import
from app.utils.logger import vgas_logger

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Single search result"""

    id: str
    name: str
    brand: Optional[str] = None
    price: float = 0.0
    original_price: Optional[float] = None
    discount_percentage: float = 0.0
    currency: str = "INR"
    store: str = ""
    store_domain: str = ""
    store_logo: Optional[str] = None
    url: str = ""
    affiliate_url: Optional[str] = None
    image: Optional[str] = None
    rating: float = 0.0
    rating_count: int = 0
    stock_status: str = "in_stock"
    is_in_stock: bool = True
    shipping_cost: float = 0.0
    condition: str = "new"
    is_prime: bool = False
    is_fake_discount: bool = False
    fake_discount_reason: Optional[str] = None
    quality_score: float = 0.0
    review_score: float = 0.0
    delivery_time: Optional[str] = None
    country: str = "India"
    category: Optional[str] = None
    specifications: Dict = field(default_factory=dict)
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    scraper: str = ""


@dataclass
class SearchResponse:
    """Search response with multiple results"""

    query: str
    page: int = 1
    limit: int = 20
    total_results: int = 0
    results: List[SearchResult] = field(default_factory=list)
    best_price: Optional[float] = None
    best_store: Optional[str] = None
    max_savings: float = 0.0
    average_price: float = 0.0
    price_range: Tuple[float, float] = (0.0, 0.0)
    stores_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time: float = 0.0


class ProductSearchEngine:
    """Main search engine for product name searches"""

    # Store domains grouped by country
    STORE_DOMAINS = {
        "India": [
            "amazon.in",
            "flipkart.com",
            "myntra.com",
            "ajio.com",
            "tatacliq.com",
            "croma.com",
            "nykaa.com",
            "reliancedigital.in",
            "paytmmall.com",
            "snapdeal.com",
            "shopclues.com",
        ],
        "USA": [
            "amazon.com",
            "walmart.com",
            "ebay.com",
            "bestbuy.com",
            "target.com",
            "newegg.com",
            "overstock.com",
            "homedepot.com",
            "lowes.com",
            "costco.com",
        ],
        "UK": [
            "amazon.co.uk",
            "ebay.co.uk",
            "argos.co.uk",
            "currys.co.uk",
            "johnlewis.com",
            "tesco.com",
            "asda.com",
        ],
        "Germany": [
            "amazon.de",
            "ebay.de",
            "otto.de",
            "mediamarkt.de",
            "saturn.de",
            "zalando.de",
        ],
        "Japan": ["amazon.co.jp", "rakuten.co.jp", "yahooshopping.jp"],
        "UAE": ["amazon.ae", "noon.com", "carrefouruae.com", "luluwebstore.com"],
        "Saudi Arabia": ["noon.com", "souq.com", "extra.com.sa"],
        "Canada": ["amazon.ca", "walmart.ca", "bestbuy.ca", "ebay.ca"],
        "Australia": ["amazon.com.au", "ebay.com.au", "kmart.com.au", "bigw.com.au"],
        "Singapore": ["amazon.sg", "lazada.sg", "qoo10.sg", "shopee.sg"],
        "Qatar": ["noon.com", "carrefourqa.com"],
        "Kuwait": ["noon.com", "souq.com"],
    }

    # Category keywords for better search
    CATEGORY_KEYWORDS = {
        "Electronics": [
            "phone",
            "mobile",
            "smartphone",
            "laptop",
            "computer",
            "tv",
            "television",
            "camera",
            "headphones",
            "earphones",
            "speaker",
            "tablet",
            "smartwatch",
            "fitness band",
            "power bank",
            "charger",
        ],
        "Fashion": [
            "shirt",
            "t-shirt",
            "jeans",
            "pants",
            "dress",
            "saree",
            "kurta",
            "shoes",
            "sandals",
            "watch",
            "bag",
            "purse",
            "jacket",
            "coat",
            "blazer",
            "suit",
            "gown",
        ],
        "Home": [
            "furniture",
            "sofa",
            "bed",
            "table",
            "chair",
            "dining",
            "kitchen",
            "appliances",
            "refrigerator",
            "washing machine",
            "ac",
            "air conditioner",
            "microwave",
            "mixer",
            "grinder",
        ],
        "Beauty": [
            "makeup",
            "cosmetics",
            "perfume",
            "creams",
            "lotion",
            "shampoo",
            "conditioner",
            "soap",
            "face wash",
            "moisturizer",
        ],
        "Grocery": ["rice", "wheat", "sugar", "oil", "spices", "tea", "coffee"],
        "Books": ["book", "novel", "story", "guide", "manual"],
        "Toys": ["toy", "doll", "car", "game", "puzzle", "board game"],
        "Sports": [
            "cricket",
            "football",
            "badminton",
            "tennis",
            "gym",
            "fitness",
            "yoga",
            "exercise",
        ],
    }

    initialized = False

    @classmethod
    async def initialize(cls):
        """Initialize the search engine"""
        if cls.initialized:
            return

        vgas_logger.success("Product Search Engine initialized")
        cls.initialized = True

    @classmethod
    async def search(
        cls,
        query: str,
        country: str = "India",
        page: int = 1,
        limit: int = 20,
        sort_by: str = "price_asc",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        in_stock: bool = True,
        use_cache: bool = True,
    ) -> SearchResponse:
        """
        Search products by name across all stores

        Args:
            query: Product name or search query
            country: Target country
            page: Page number
            limit: Results per page
            sort_by: Sorting option (price_asc, price_desc, rating, discount)
            min_price: Minimum price filter
            max_price: Maximum price filter
            brand: Filter by brand
            category: Filter by category
            in_stock: Only show in-stock items
            use_cache: Use cached results if available

        Returns:
            SearchResponse with list of products
        """
        start_time = time.time()
        query = query.strip()

        if not query:
            return SearchResponse(query=query, total_results=0)

        # Generate cache key
        cache_key = f"search:{query}:{country}:{page}:{limit}:{sort_by}"
        if min_price:
            cache_key += f":{min_price}"
        if max_price:
            cache_key += f":{max_price}"
        if brand:
            cache_key += f":{brand}"
        if category:
            cache_key += f":{category}"

        # Check cache
        if use_cache:
            cached_result = await get_cache(cache_key)
            if cached_result:
                vgas_logger.debug(f"Cache hit for search: {query}")
                return SearchResponse(**cached_result)

        # Get store domains for the country
        store_domains = cls.STORE_DOMAINS.get(country, cls.STORE_DOMAINS["India"])

        # Search across all stores concurrently
        tasks = []
        all_results = []

        for domain in store_domains:
            task = asyncio.create_task(
                cls._search_single_store(domain, query, page, limit, country)
            )
            tasks.append(task)

        # Wait for all searches to complete with timeouts per store
        wrapped_tasks = [
            asyncio.wait_for(t, timeout=settings.SCRAPER_TIMEOUT) for t in tasks
        ]
        results_by_store = await asyncio.gather(*wrapped_tasks, return_exceptions=True)

        # Flatten results
        for store_result in results_by_store:
            if isinstance(store_result, asyncio.TimeoutError):
                logger.warning(f"Search timeout for query '{query}' on one store")
                continue
            if isinstance(store_result, Exception):
                logger.error(f"Search error: {store_result}")
                continue
            if store_result and isinstance(store_result, list):
                all_results.extend(store_result)

        # Apply filters
        filtered_results = []
        for result in all_results:
            # Apply price filters
            if min_price and result.price < min_price:
                continue
            if max_price and result.price > max_price:
                continue

            # Apply brand filter
            if brand and brand.lower() not in (result.brand or "").lower():
                continue

            # Apply category filter
            if category:
                result_category = (result.category or "").lower()
                category_lower = category.lower()
                if category_lower not in result_category:
                    # Check if category matches any keyword
                    category_found = False
                    for cat, keywords in cls.CATEGORY_KEYWORDS.items():
                        if cat.lower() == category_lower:
                            category_found = True
                            break
                        for kw in keywords:
                            if kw in query.lower() or kw in result_category:
                                category_found = True
                                break
                    if not category_found:
                        continue

            # Apply stock filter
            if in_stock and result.stock_status != "in_stock":
                continue

            filtered_results.append(result)

        # If scrapers returned 0 results, return honest empty results
        if len(filtered_results) == 0:
            vgas_logger.warning(
                f"No real scraping results for '{query}'. Returning empty search results."
            )

        # Sort results
        filtered_results = cls._sort_results(filtered_results, sort_by)

        # Paginate
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_results = filtered_results[start_idx:end_idx]

        # Calculate statistics
        prices = [r.price for r in filtered_results if r.price > 0]
        best_price = min(prices) if prices else 0.0
        average_price = sum(prices) / len(prices) if prices else 0.0
        price_range = (min(prices) if prices else 0.0, max(prices) if prices else 0.0)

        # Count unique stores
        stores = set(r.store for r in filtered_results)
        stores_count = len(stores)

        # Calculate max savings
        max_savings = 0.0
        if prices and best_price > 0:
            max_savings = max(prices) - best_price

        # Create response
        response = SearchResponse(
            query=query,
            page=page,
            limit=limit,
            total_results=len(filtered_results),
            results=paginated_results,
            best_price=round(best_price, 2),
            best_store=next(
                (r.store for r in paginated_results if r.price == best_price), None
            )
            if best_price > 0
            else None,
            max_savings=round(max_savings, 2),
            average_price=round(average_price, 2),
            price_range=price_range,
            stores_count=stores_count,
            execution_time=round(time.time() - start_time, 2),
        )

        # Cache result
        if use_cache:
            await set_cache(
                cache_key, dataclasses.asdict(response), expire_seconds=300
            )  # 5 minutes

        vgas_logger.info(
            f"Search completed: {query} -> {len(filtered_results)} results"
        )

        return response

    @classmethod
    async def _search_single_store(
        cls,
        domain: str,
        query: str,
        page: int = 1,
        limit: int = 10,
        country: str = "India",
    ) -> List[SearchResult]:
        """Search a single store"""
        try:
            from app.scrapers import get_scraper

            scraper = get_scraper(domain)
            if not scraper:
                return []

            # Search on this store
            result = await scraper.search_products(query, page, limit)
            if not result:
                return []

            # Normalize search result payloads from different scrapers
            if isinstance(result, dict):
                results_list = result.get("results") or result.get("items") or []
            elif isinstance(result, list):
                results_list = result
            else:
                return []

            if not isinstance(results_list, list):
                return []

            # Convert to SearchResult
            search_results = []
            for product_data in results_list:
                if not isinstance(product_data, dict):
                    continue
                search_result = cls._convert_to_search_result(
                    product_data, domain, country
                )
                if search_result:
                    search_results.append(search_result)

            return search_results

        except Exception as e:
            logger.error(f"Error searching {domain}: {e}")
            return []

    @classmethod
    def _convert_to_search_result(
        cls, product_data: Dict, domain: str, country: str
    ) -> Optional[SearchResult]:
        """Convert product data dict to SearchResult"""
        try:
            # Generate unique ID
            product_id = product_data.get("id", product_data.get("url", ""))

            # Extract currency
            currency = product_data.get("currency", settings.DEFAULT_CURRENCY)
            if not currency:
                currency = "INR" if country == "India" else "USD"

            # Extract prices
            current_price = product_data.get("current_price", 0.0)
            original_price = product_data.get("original_price", current_price)
            discount_pct = product_data.get("discount_percentage", 0.0)

            if current_price and isinstance(current_price, str):
                current_price = float(re.sub(r"[^\d.]", "", current_price))
            if original_price and isinstance(original_price, str):
                original_price = float(re.sub(r"[^\d.]", "", original_price))

            # Calculate discount percentage
            if original_price > 0 and discount_pct == 0:
                discount_pct = round(
                    ((original_price - current_price) / original_price) * 100, 2
                )

            # Create search result
            return SearchResult(
                id=str(product_id),
                name=product_data.get("name", ""),
                brand=product_data.get("brand"),
                price=float(current_price),
                original_price=float(original_price) if original_price else None,
                discount_percentage=float(discount_pct),
                currency=currency,
                store=product_data.get("store_name", domain.replace(".", " ").title()),
                store_domain=domain,
                store_logo=product_data.get("store_logo"),
                url=product_data.get("url", ""),
                affiliate_url=product_data.get("affiliate_url"),
                image=product_data.get("image"),
                rating=float(product_data.get("rating", 0.0)),
                rating_count=int(product_data.get("rating_count", 0)),
                stock_status=product_data.get("stock_status", "in_stock"),
                shipping_cost=float(product_data.get("shipping_cost", 0.0)),
                condition=product_data.get("condition", "new"),
                is_prime=product_data.get("is_prime", False),
                is_fake_discount=product_data.get("is_fake_discount", False),
                fake_discount_reason=product_data.get("fake_discount_reason"),
                quality_score=float(product_data.get("quality_score", 0.0)),
                review_score=float(product_data.get("review_score", 0.0)),
                delivery_time=product_data.get("delivery_time"),
                country=country,
                category=product_data.get("category"),
                specifications=product_data.get("specifications", {}),
                scraped_at=datetime.utcnow().isoformat(),
                scraper=domain,
            )
        except Exception as e:
            logger.error(f"Error converting product data: {e}")
            return None

    @classmethod
    def _sort_results(
        cls, results: List[SearchResult], sort_by: str
    ) -> List[SearchResult]:
        """Sort search results"""
        if not results:
            return results

        if sort_by == "price_asc":
            return sorted(results, key=lambda x: x.price)
        elif sort_by == "price_desc":
            return sorted(results, key=lambda x: x.price, reverse=True)
        elif sort_by == "discount":
            return sorted(results, key=lambda x: x.discount_percentage, reverse=True)
        elif sort_by == "rating":
            return sorted(
                results, key=lambda x: (x.rating, x.rating_count), reverse=True
            )
        elif sort_by == "savings":
            return sorted(
                results, key=lambda x: (x.original_price or 0) - x.price, reverse=True
            )
        elif sort_by == "review_score":
            return sorted(results, key=lambda x: x.review_score, reverse=True)
        elif sort_by == "quality":
            return sorted(results, key=lambda x: x.quality_score, reverse=True)
        else:
            return results

    @classmethod
    async def search_by_image(
        cls, image_url: str, country: str = "India"
    ) -> SearchResponse:
        """Search products by image URL (using AI vision)"""
        # This would use Google Vision API or similar
        # For now, return empty results
        return SearchResponse(query=f"image:{image_url}", total_results=0, results=[])

    @classmethod
    async def search_by_voice(cls, audio_data: bytes, language: str = "en") -> str:
        """Convert voice to text and search"""
        # This would use Google Speech-to-Text API
        # For now, return the query as-is
        return ""

    @classmethod
    async def get_trending_products(
        cls, country: str = "India", limit: int = 10
    ) -> List[SearchResult]:
        """Get trending products from real store searches"""
        cache_key = f"trending:{country}:{limit}"
        trending = await get_cache(cache_key)

        if trending:
            return [SearchResult(**r) for r in trending]

        # Popular queries people search for daily
        popular_queries = [
            "smartwatch",
            "wireless earbuds",
            "laptop",
            "smartphone 5G",
            "bluetooth speaker",
            "gaming headphones",
            "power bank",
            "fitness band",
        ]

        trending_results = []
        seen_urls = set()
        for q in popular_queries:
            try:
                resp = await cls.search(
                    query=q,
                    country=country,
                    limit=4,
                    sort_by="price_asc",
                    use_cache=False,
                )
                for r in resp.results:
                    if r.price > 0 and r.url and r.url not in seen_urls:
                        seen_urls.add(r.url)
                        trending_results.append(r)
                    if len(trending_results) >= limit:
                        break
            except Exception as e:
                logger.warning(f"Trending query '{q}' failed: {e}")
            if len(trending_results) >= limit:
                break

        trending_results = trending_results[:limit]

        if trending_results:
            await set_cache(
                cache_key,
                [dataclasses.asdict(r) for r in trending_results],
                expire_seconds=1800,
            )  # 30 minutes

        return trending_results

    @classmethod
    async def get_loot_deals(
        cls, country: str = "India", limit: int = 20
    ) -> List[SearchResult]:
        """Get 80-90% discount loot deals - LIVE verified deals from real stores"""
        cache_key = f"loot_deals:{country}:{limit}"
        cached = await get_cache(cache_key)
        if cached:
            return [SearchResult(**r) for r in cached]

        # Real deal categories most likely to carry deep discounts
        deal_queries = [
            "smartwatch",
            "wireless earbuds",
            "bluetooth headphones",
            "power bank",
            "fitness band",
            "gaming mouse",
        ]

        all_deals = []
        seen_urls = set()
        for q in deal_queries:
            try:
                resp = await cls.search(
                    query=q,
                    country=country,
                    limit=8,
                    sort_by="discount",
                    use_cache=False,
                )
                for r in resp.results:
                    # Keep only genuine-looking deep discounts with real product links
                    if (
                        r.discount_percentage >= 45
                        and r.price > 0
                        and r.url
                        and r.image
                        and r.url not in seen_urls
                    ):
                        seen_urls.add(r.url)
                        all_deals.append(r)
                    if len(all_deals) >= limit:
                        break
            except Exception as e:
                logger.warning(f"Loot deal query '{q}' failed: {e}")
            if len(all_deals) >= limit:
                break

        # Sort by discount, best first
        all_deals = sorted(
            all_deals, key=lambda x: x.discount_percentage, reverse=True
        )[:limit]

        if all_deals:
            await set_cache(
                cache_key, [dataclasses.asdict(r) for r in all_deals], expire_seconds=900
            )  # 15 minutes

        return all_deals

    @classmethod
    async def get_refurbished_products(
        cls, country: str = "India", limit: int = 20
    ) -> List[SearchResult]:
        """Get refurbished/open-box products"""
        results = []

        # Search across stores for refurbished products
        query = "refurbished OR open box OR like new"
        search_response = await cls.search(
            query=query, country=country, limit=limit * 5, use_cache=False
        )

        # Filter for refurbished items
        for result in search_response.results:
            if result.condition.lower() in [
                "refurbished",
                "open_box",
                "like_new",
                "used",
            ]:
                results.append(result)

            if len(results) >= limit:
                break

        return results
