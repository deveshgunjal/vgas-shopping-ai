"""
Products API endpoints for VGAS Shopping AI
Get product details by URL, ID, image, voice, batch
"""

from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from urllib.parse import urlparse

from app.scrapers import get_scraper
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/products", tags=["Products"])
logger = logging.getLogger(__name__)


class ProductByUrlRequest(BaseModel):
    url: str = Field(..., description="Product URL")


class ProductBatchRequest(BaseModel):
    urls: List[str] = Field(..., description="List of product URLs")


@router.get("/by-url")
async def get_product_by_url(
    url: str = Query(..., min_length=1, description="Product URL"),
):
    """Get product details by URL"""
    try:
        vgas_logger.info(f"Product URL request: {url}")

        # Check cache
        cache_key = CacheKeys.PRODUCT_BY_URL.format(url)
        cached = await get_cache(cache_key)
        if cached:
            vgas_logger.debug(f"Cache hit for product: {url}")
            return {
                "product": cached,
                "from_cache": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Extract domain and get scraper
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        scraper = get_scraper(domain)
        if not scraper:
            raise HTTPException(
                status_code=400, detail=f"No scraper available for domain: {domain}"
            )

        # Scrape product
        product_data = await scraper.extract_product_from_url(url)
        if not product_data:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found or could not be scraped: {url}",
            )

        # Cache result
        await set_cache(cache_key, product_data, expire_seconds=86400)

        return {
            "product": product_data,
            "from_cache": False,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product by URL error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch product: {str(e)}"
        )


@router.get("/by-id")
async def get_product_by_id(
    product_id: str = Query(..., description="Product ID/ASIN/SKU"),
    store: Optional[str] = Query(default=None, description="Store domain"),
):
    """Get product by ID, ASIN, or SKU"""
    try:
        # Check cache
        cache_key = CacheKeys.PRODUCT_BY_ID.format(product_id)
        cached = await get_cache(cache_key)
        if cached:
            return {
                "product": cached,
                "from_cache": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # If ASIN, construct Amazon URL
        if len(product_id) == 10 and store:
            url = f"https://www.{store}/dp/{product_id}"
            scraper = get_scraper(store)
            product_data = (
                await scraper.extract_product_from_url(url) if scraper else None
            )

            if product_data:
                await set_cache(cache_key, product_data, expire_seconds=86400)
                return {
                    "product": product_data,
                    "from_cache": False,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        raise HTTPException(status_code=404, detail=f"Product not found: {product_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product by ID error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/by-image")
async def search_by_image(
    image: UploadFile = File(..., description="Product image"),
    country: str = Form(default="India", description="Target country"),
):
    """Search products by uploading an image"""
    try:
        vgas_logger.info(f"Image search request from {country}")

        # Read image data
        image_data = await image.read()

        # Save image temporarily
        from app.core.config import settings
        import os

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        filename = f"{datetime.utcnow().timestamp()}_{image.filename}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)

        # Use search engine image search
        from app.scrapers.search_engine import ProductSearchEngine

        results = await ProductSearchEngine.search_by_image(
            image_url=filepath, country=country
        )

        return {
            "message": "Image search processed",
            "results": [],
            "note": "Image search requires Google Vision API or similar service configuration",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Image search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/by-voice")
async def search_by_voice(
    audio: UploadFile = File(..., description="Audio file"),
    language: str = Form(default="en", description="Language code"),
):
    """Search products by voice input"""
    try:
        vgas_logger.info(f"Voice search request in {language}")

        # Read audio data
        audio_data = await audio.read()

        # Use search engine voice search
        from app.scrapers.search_engine import ProductSearchEngine

        query = await ProductSearchEngine.search_by_voice(
            audio_data=audio_data, language=language
        )

        return {
            "message": "Voice search processed",
            "transcribed_query": query,
            "note": "Voice search requires Google Speech-to-Text API configuration",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Voice search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/details")
async def get_product_details(
    url: str = Query(..., description="Product URL"),
    include_reviews: bool = Query(default=False, description="Include reviews"),
    include_specs: bool = Query(default=True, description="Include specifications"),
):
    """Get detailed product information"""
    try:
        # Reuse by-url endpoint logic
        cache_key = CacheKeys.PRODUCT_BY_URL.format(url)
        cached = await get_cache(cache_key)

        if cached:
            product = cached
        else:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            scraper = get_scraper(domain)
            if not scraper:
                raise HTTPException(status_code=400, detail=f"No scraper for: {domain}")
            product = await scraper.extract_product_from_url(url)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            await set_cache(cache_key, product, expire_seconds=86400)

        # Build response
        response = {
            "product": product,
            "include_reviews": include_reviews,
            "include_specs": include_specs,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if include_reviews:
            response["reviews"] = []
            response["reviews_note"] = (
                "Reviews extraction requires additional scraper configuration"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch")
async def get_products_batch(
    urls: str = Query(..., description="Comma-separated product URLs"),
):
    """Get multiple products in a single request"""
    try:
        url_list = [u.strip() for u in urls.split(",") if u.strip()]
        if not url_list:
            raise HTTPException(status_code=400, detail="No URLs provided")

        results = []
        errors = []

        for url in url_list:
            try:
                cache_key = CacheKeys.PRODUCT_BY_URL.format(url)
                cached = await get_cache(cache_key)

                if cached:
                    results.append({"url": url, "product": cached, "from_cache": True})
                else:
                    parsed = urlparse(url)
                    domain = parsed.netloc.lower()
                    scraper = get_scraper(domain)
                    if scraper:
                        product = await scraper.extract_product_from_url(url)
                        if product:
                            await set_cache(cache_key, product, expire_seconds=86400)
                            results.append(
                                {"url": url, "product": product, "from_cache": False}
                            )
                        else:
                            errors.append({"url": url, "error": "Product not found"})
                    else:
                        errors.append({"url": url, "error": f"No scraper for {domain}"})
            except Exception as e:
                errors.append({"url": url, "error": str(e)})

        return {
            "results": results,
            "errors": errors,
            "total_success": len(results),
            "total_errors": len(errors),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Batch products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
