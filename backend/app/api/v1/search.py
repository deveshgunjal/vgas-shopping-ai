"""
Search API endpoints for VGAS Shopping AI
Product search by name, trending, loot deals, refurbished
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.scrapers.search_engine import ProductSearchEngine
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger
from app.utils.quota import check_search_quota

router = APIRouter(prefix="/search", tags=["Search"])
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    query: str = Field(..., description="Product search query")
    country: str = Field(default="India", description="Target country")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Results per page")
    sort_by: str = Field(
        default="price_asc",
        description="Sorting: price_asc, price_desc, rating, discount",
    )
    min_price: Optional[float] = Field(default=None, description="Minimum price filter")
    max_price: Optional[float] = Field(default=None, description="Maximum price filter")
    brand: Optional[str] = Field(default=None, description="Filter by brand")
    category: Optional[str] = Field(default=None, description="Filter by category")
    in_stock: bool = Field(default=True, description="Only in-stock items")


class SearchResponse(BaseModel):
    query: str
    page: int
    limit: int
    total_results: int
    results: List[Dict[str, Any]]
    best_price: Optional[float]
    best_store: Optional[str]
    max_savings: float
    average_price: float
    stores_count: int
    execution_time: float
    timestamp: str


@router.get("/", response_model=SearchResponse, dependencies=[Depends(check_search_quota)])
async def search_products(
    query: str = Query(..., min_length=1, description="Product search query"),
    country: str = Query(default="India", description="Target country"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Results per page"),
    sort_by: str = Query(default="price_asc", description="Sorting option"),
    min_price: Optional[float] = Query(default=None, description="Minimum price"),
    max_price: Optional[float] = Query(default=None, description="Maximum price"),
    brand: Optional[str] = Query(default=None, description="Brand filter"),
    category: Optional[str] = Query(default=None, description="Category filter"),
    in_stock: bool = Query(default=True, description="In-stock only"),
):
    """Search products by name across all e-commerce platforms"""
    try:
        vgas_logger.info(f"Search request: '{query}' in {country}")

        search_result = await ProductSearchEngine.search(
            query=query,
            country=country,
            page=page,
            limit=limit,
            sort_by=sort_by,
            min_price=min_price,
            max_price=max_price,
            brand=brand,
            category=category,
            in_stock=in_stock,
        )

        # Convert SearchResult objects to dicts
        results_list = []
        for r in search_result.results:
            results_list.append(
                {
                    "id": r.id,
                    "name": r.name,
                    "brand": r.brand,
                    "price": r.price,
                    "original_price": r.original_price,
                    "discount_percentage": r.discount_percentage,
                    "currency": r.currency,
                    "store": r.store,
                    "store_domain": r.store_domain,
                    "url": r.url,
                    "affiliate_url": r.affiliate_url,
                    "image": r.image,
                    "rating": r.rating,
                    "rating_count": r.rating_count,
                    "stock_status": r.stock_status,
                    "shipping_cost": r.shipping_cost,
                    "condition": r.condition,
                    "is_fake_discount": r.is_fake_discount,
                    "fake_discount_reason": r.fake_discount_reason,
                    "quality_score": r.quality_score,
                    "delivery_time": r.delivery_time,
                    "country": r.country,
                    "category": r.category,
                    "scraped_at": r.scraped_at,
                }
            )

        return SearchResponse(
            query=search_result.query,
            page=search_result.page,
            limit=search_result.limit,
            total_results=search_result.total_results,
            results=results_list,
            best_price=search_result.best_price,
            best_store=search_result.best_store,
            max_savings=search_result.max_savings,
            average_price=search_result.average_price,
            stores_count=search_result.stores_count,
            execution_time=search_result.execution_time,
            timestamp=search_result.timestamp,
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/quick", dependencies=[Depends(check_search_quota)])
async def quick_search(
    query: str = Query(..., min_length=1),
    country: str = Query(default="India"),
    limit: int = Query(default=5, ge=1, le=10),
):
    """Quick search with limited results for fast response"""
    try:
        search_result = await ProductSearchEngine.search(
            query=query,
            country=country,
            limit=limit,
            sort_by="price_asc",
            use_cache=True,
        )

        results_list = []
        for r in search_result.results[:limit]:
            results_list.append(
                {
                    "name": r.name,
                    "price": r.price,
                    "currency": r.currency,
                    "store": r.store,
                    "url": r.url,
                    "affiliate_url": r.affiliate_url,
                    "image": r.image,
                    "rating": r.rating,
                    "discount_percentage": r.discount_percentage,
                }
            )

        return {
            "query": query,
            "results": results_list,
            "total": len(results_list),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Quick search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autocomplete")
async def autocomplete(
    prefix: str = Query(..., min_length=2, description="Search prefix"),
):
    """Get search suggestions based on prefix"""
    try:
        cache_key = f"autocomplete:{prefix.lower()}"
        cached = await get_cache(cache_key)
        if cached:
            return {"prefix": prefix, "suggestions": cached}

        # Common product suggestions
        all_suggestions = [
            "iPhone 15",
            "iPhone 15 Pro",
            "iPhone 14",
            "Samsung Galaxy S24",
            "Samsung Galaxy S23",
            "OnePlus 12",
            "OnePlus Nord",
            "MacBook Air M3",
            "MacBook Pro",
            "Dell Laptop",
            "HP Laptop",
            "Lenovo ThinkPad",
            "Sony Headphones",
            "Boat Earphones",
            "JBL Speaker",
            "Samsung TV",
            "LG TV",
            "OnePlus TV",
            "Mi TV",
            "Nike Shoes",
            "Puma Shoes",
            "Adidas Shoes",
            "Reebok Shoes",
            "Men Shirt",
            "Women Dress",
            "Kids T-Shirt",
            "Saree",
            "Kurta",
            "Kitchen Mixer",
            "Refrigerator",
            "Washing Machine",
            "AC Split",
            "iPad",
            "Samsung Tab",
            "Fire HD Tablet",
            "Smart Watch",
            "Fitness Band",
            "Power Bank",
        ]

        suggestions = [s for s in all_suggestions if prefix.lower() in s.lower()][:10]

        await set_cache(cache_key, suggestions, expire_seconds=3600)

        return {
            "prefix": prefix,
            "suggestions": suggestions,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending")
async def get_trending(
    country: str = Query(default="India"),
    limit: int = Query(default=10, ge=1, le=50),
):
    """Get trending products"""
    try:
        trending = await ProductSearchEngine.get_trending_products(
            country=country, limit=limit
        )

        results_list = []
        for r in trending:
            results_list.append(
                {
                    "name": r.name,
                    "price": r.price,
                    "currency": r.currency,
                    "store": r.store,
                    "url": r.url,
                    "image": r.image,
                    "rating": r.rating,
                    "discount_percentage": r.discount_percentage,
                }
            )

        return {
            "country": country,
            "trending_products": results_list,
            "total": len(results_list),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Trending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loot-deals")
async def get_loot_deals(
    country: str = Query(default="India"),
    limit: int = Query(default=20, ge=1, le=50),
):
    """Get 80-90% discount loot deals"""
    try:
        deals_response = await ProductSearchEngine.get_loot_deals(
            country=country, limit=limit
        )

        results_list = []
        for r in (
            deals_response.results
            if hasattr(deals_response, "results")
            else deals_response
        ):
            results_list.append(
                {
                    "name": r.name,
                    "price": r.price,
                    "original_price": r.original_price,
                    "discount_percentage": r.discount_percentage,
                    "currency": r.currency,
                    "store": r.store,
                    "url": r.url,
                    "affiliate_url": r.affiliate_url,
                    "image": r.image,
                    "rating": r.rating,
                }
            )

        return {
            "country": country,
            "loot_deals": results_list,
            "total": len(results_list),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Loot deals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/refurbished")
async def get_refurbished(
    country: str = Query(default="India"),
    limit: int = Query(default=20, ge=1, le=50),
):
    """Get refurbished/open-box products"""
    try:
        refurbished = await ProductSearchEngine.get_refurbished_products(
            country=country, limit=limit
        )

        results_list = []
        for r in refurbished:
            results_list.append(
                {
                    "name": r.name,
                    "price": r.price,
                    "currency": r.currency,
                    "store": r.store,
                    "url": r.url,
                    "image": r.image,
                    "condition": r.condition,
                    "rating": r.rating,
                }
            )

        return {
            "country": country,
            "refurbished_products": results_list,
            "total": len(results_list),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Refurbished error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get all product categories"""
    from app.scrapers.search_engine import ProductSearchEngine

    categories = []
    for cat_name, keywords in ProductSearchEngine.CATEGORY_KEYWORDS.items():
        categories.append(
            {
                "name": cat_name,
                "keywords": keywords,
                "count": len(keywords),
            }
        )

    return {
        "categories": categories,
        "total": len(categories),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stores")
async def get_stores(
    country: Optional[str] = Query(default=None, description="Filter by country"),
):
    """Get all supported stores"""
    from app.scrapers.search_engine import ProductSearchEngine

    if country:
        domains = ProductSearchEngine.STORE_DOMAINS.get(country, [])
        return {
            "country": country,
            "stores": [
                {"domain": d, "name": d.replace(".", " ").title()} for d in domains
            ],
            "total": len(domains),
        }

    all_stores = {}
    for country_name, domains in ProductSearchEngine.STORE_DOMAINS.items():
        all_stores[country_name] = [
            {"domain": d, "name": d.replace(".", " ").title()} for d in domains
        ]

    return {
        "stores_by_country": all_stores,
        "countries": list(ProductSearchEngine.STORE_DOMAINS.keys()),
        "timestamp": datetime.utcnow().isoformat(),
    }
