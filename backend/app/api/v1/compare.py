"""
Compare API endpoints for VGAS Shopping AI
Compare multiple products side-by-side
"""

from fastapi import APIRouter, Query, HTTPException, Body, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from urllib.parse import urlparse

from app.scrapers import get_scraper
from app.core.redis_cache import get_cache, set_cache
from app.utils.logger import vgas_logger
from app.utils.quota import check_compare_quota

router = APIRouter(prefix="/compare", tags=["Comparison"])
logger = logging.getLogger(__name__)


class CompareRequest(BaseModel):
    urls: List[str] = Field(
        ..., min_items=2, max_items=10, description="Product URLs to compare"
    )


class CompareByQueryRequest(BaseModel):
    products: List[Dict[str, str]] = Field(
        ...,
        min_items=2,
        max_items=10,
        description="List of products with 'name' and optional 'brand'",
    )
    country: str = Field(default="India")


@router.post("/", dependencies=[Depends(check_compare_quota)])
async def compare_products(request: CompareRequest = Body(...)):
    """Compare multiple products by URLs"""
    try:
        if len(request.urls) < 2:
            raise HTTPException(
                status_code=400, detail="At least 2 URLs required for comparison"
            )

        vgas_logger.info(f"Compare request for {len(request.urls)} products")

        products = []
        errors = []

        for url in request.urls:
            try:
                cache_key = f"product:url:{url}"
                cached = await get_cache(cache_key)

                if cached:
                    products.append(cached)
                else:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    scraper = get_scraper(domain)
                    if scraper:
                        product = await scraper.extract_product_from_url(url)
                        if product:
                            await set_cache(cache_key, product, expire_seconds=86400)
                            products.append(product)
                        else:
                            errors.append({"url": url, "error": "Product not found"})
                    else:
                        errors.append({"url": url, "error": f"No scraper for {domain}"})
            except Exception as e:
                errors.append({"url": url, "error": str(e)})

        if len(products) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"Need at least 2 valid products to compare. Got {len(products)}",
            )

        # Generate comparison
        comparison = _generate_comparison(products)

        return {
            "comparison": comparison,
            "products_count": len(products),
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compare error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick", dependencies=[Depends(check_compare_quota)])
async def quick_compare(urls: str = Query(..., description="Comma-separated URLs")):
    """Quick compare by comma-separated URLs"""
    try:
        url_list = [u.strip() for u in urls.split(",") if u.strip()]
        if len(url_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 URLs required")

        return await compare_products(CompareRequest(urls=url_list))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick compare error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/by-query", dependencies=[Depends(check_compare_quota)])
async def compare_by_query(request: CompareByQueryRequest = Body(...)):
    """Compare products by searching their names"""
    try:
        from app.scrapers.search_engine import ProductSearchEngine

        products = []

        for prod in request.products:
            name = prod.get("name", "")
            if not name:
                continue

            # Search for each product
            result = await ProductSearchEngine.search(
                query=name,
                country=request.country,
                limit=1,
                sort_by="price_asc",
            )

            if result.results:
                best = result.results[0]
                products.append(
                    {
                        "name": best.name,
                        "price": best.price,
                        "currency": best.currency,
                        "store": best.store,
                        "url": best.url,
                        "image": best.image,
                        "rating": best.rating,
                        "discount_percentage": best.discount_percentage,
                    }
                )

        if len(products) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"Found only {len(products)} products. Need at least 2 to compare.",
            )

        comparison = _generate_comparison(products)

        return {
            "comparison": comparison,
            "products_count": len(products),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compare by query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_comparison(products: List[Dict]) -> Dict[str, Any]:
    """Generate detailed comparison between products"""
    if not products:
        return {}

    # Find best price
    prices = [
        p.get("price", p.get("current_price", 0))
        for p in products
        if p.get("price", p.get("current_price", 0)) > 0
    ]
    best_price = min(prices) if prices else 0
    best_product = next(
        (
            p
            for p in products
            if p.get("price", p.get("current_price", 0)) == best_price
        ),
        None,
    )

    # Find best rating
    ratings = [p.get("rating", 0) for p in products if p.get("rating", 0) > 0]
    best_rating = max(ratings) if ratings else 0

    # Find best discount
    discounts = [
        p.get("discount_percentage", 0)
        for p in products
        if p.get("discount_percentage", 0) > 0
    ]
    best_discount = max(discounts) if discounts else 0

    # Calculate max savings
    max_price = max(prices) if prices else 0
    max_savings = max_price - best_price if best_price > 0 else 0

    # Build comparison table
    comparison_table = []
    for p in products:
        comparison_table.append(
            {
                "name": p.get("name", "Unknown"),
                "price": p.get("price", p.get("current_price", 0)),
                "original_price": p.get("original_price", 0),
                "discount_percentage": p.get("discount_percentage", 0),
                "currency": p.get("currency", "INR"),
                "store": p.get("store", ""),
                "rating": p.get("rating", 0),
                "rating_count": p.get("rating_count", 0),
                "image": p.get("image", p.get("main_image", "")),
                "url": p.get("url", ""),
                "affiliate_url": p.get("affiliate_url", p.get("url", "")),
                "is_in_stock": p.get(
                    "is_in_stock", p.get("stock_status") == "in_stock", True
                ),
                "shipping_cost": p.get("shipping_cost", 0),
                "is_best_price": p.get("price", p.get("current_price", 0))
                == best_price,
            }
        )

    return {
        "products": comparison_table,
        "best_price": {
            "price": best_price,
            "store": best_product.get("store", "") if best_product else "",
            "url": best_product.get("url", "") if best_product else "",
        }
        if best_product
        else None,
        "best_rating": best_rating,
        "best_discount": best_discount,
        "max_savings": round(max_savings, 2),
        "price_range": {
            "min": round(best_price, 2),
            "max": round(max_price, 2),
        },
        "average_price": round(sum(prices) / len(prices), 2) if prices else 0,
        "recommendation": _get_recommendation(comparison_table),
    }


def _get_recommendation(products: List[Dict]) -> str:
    """Get AI-based recommendation"""
    if not products:
        return ""

    best_price = next((p for p in products if p.get("is_best_price")), None)
    best_rating = max(products, key=lambda x: x.get("rating", 0)) if products else None

    if best_price and best_price.get("rating", 0) >= 4.0:
        return f"🏆 Best choice: {best_price['name']} at {best_price['store']} - Great price with good rating!"

    if best_price and best_rating and best_price.get("name") != best_rating.get("name"):
        return f"💰 Best price: {best_price['name']} | ⭐ Best rating: {best_rating['name']} - Choose based on your priority!"

    return f"📊 All {len(products)} products compared. Pick based on price, rating, and your needs!"
