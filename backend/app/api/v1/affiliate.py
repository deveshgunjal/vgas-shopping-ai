"""
Affiliate API endpoints for VGAS Shopping AI
Convert URLs to affiliate links, batch convert, stats
"""

from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/affiliate", tags=["Affiliate"])
logger = logging.getLogger(__name__)

# Affiliate network configuration
AFFILIATE_NETWORKS = {
    "amazon": {
        "domains": [
            "amazon.in",
            "amazon.com",
            "amazon.co.uk",
            "amazon.de",
            "amazon.jp",
            "amazon.ae",
        ],
        "param": "tag",
        "default_id": settings.AMAZON_AFFILIATE_ID,
    },
    "flipkart": {
        "domains": ["flipkart.com"],
        "param": "affid",
        "default_id": "vgas2024",
    },
    "myntra": {
        "domains": ["myntra.com"],
        "param": "refId",
        "default_id": "vgas-affiliate",
    },
    "ajio": {
        "domains": ["ajio.com"],
        "param": "ref",
        "default_id": "vgas",
    },
    "earnkaro": {
        "domains": ["earnkaro.com"],
        "param": "ref",
        "default_id": settings.EARNKARO_API_KEY or "vgas",
    },
}


class AffiliateConvertRequest(BaseModel):
    url: str = Field(..., description="Product URL")
    network: Optional[str] = Field(default=None, description="Affiliate network")


class AffiliateBatchRequest(BaseModel):
    urls: List[str] = Field(..., min_items=1, max_items=50)
    network: Optional[str] = Field(default=None)


@router.get("/convert")
async def convert_to_affiliate(
    url: str = Query(..., description="Product URL to convert"),
    network: Optional[str] = Query(default=None, description="Affiliate network"),
):
    """Convert a product URL to affiliate URL"""
    try:
        vgas_logger.info(f"Affiliate convert: {url}")

        # Check cache
        cache_key = CacheKeys.AFFILIATE_LINK.format(url)
        cached = await get_cache(cache_key)
        if cached:
            return {
                "original_url": url,
                "affiliate_url": cached,
                "from_cache": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        affiliate_url = _convert_url(url, network)

        # Detect network & commission rate
        detected_network, commission_rate = _detect_network(url)

        # Cache result
        await set_cache(cache_key, affiliate_url, expire_seconds=86400 * 30)

        return {
            "original_url": url,
            "affiliate_url": affiliate_url,
            "network": detected_network or "Unknown",
            "commission_rate": commission_rate,
            "from_cache": False,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Affiliate convert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_convert(request: AffiliateBatchRequest = Body(...)):
    """Batch convert multiple URLs to affiliate URLs"""
    try:
        results = []
        for url in request.urls:
            try:
                affiliate_url = _convert_url(url, request.network)
                results.append(
                    {
                        "original_url": url,
                        "affiliate_url": affiliate_url,
                        "success": True,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "original_url": url,
                        "affiliate_url": url,
                        "success": False,
                        "error": str(e),
                    }
                )

        return {
            "results": results,
            "total": len(request.urls),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Batch convert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/redirect")
async def affiliate_redirect(
    url: str = Query(..., description="Original product URL"),
):
    """Redirect to affiliate URL"""
    try:
        from fastapi.responses import RedirectResponse

        affiliate_url = _convert_url(url)
        return RedirectResponse(url=affiliate_url, status_code=302)

    except Exception as e:
        logger.error(f"Redirect error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_affiliate_stats(
    days: int = Query(default=7, ge=1, le=365, description="Last N days"),
):
    """Get affiliate statistics"""
    try:
        cache_key = f"affiliate_stats:{days}"
        cached = await get_cache(cache_key)
        if cached:
            return cached

        stats = {
            "period_days": days,
            "total_clicks": 0,
            "total_conversions": 0,
            "total_earnings": 0.0,
            "conversion_rate": 0.0,
            "top_networks": [
                {"network": "Amazon", "clicks": 0, "earnings": 0.0},
                {"network": "Flipkart", "clicks": 0, "earnings": 0.0},
                {"network": "Myntra", "clicks": 0, "earnings": 0.0},
            ],
            "note": "Stats will be populated as affiliate links are tracked",
            "timestamp": datetime.utcnow().isoformat(),
        }

        await set_cache(cache_key, stats, expire_seconds=3600)
        return stats

    except Exception as e:
        logger.error(f"Affiliate stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/link-info")
async def get_link_info(
    url: str = Query(..., description="Affiliate URL to analyze"),
):
    """Analyze an affiliate link"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        info = {
            "url": url,
            "domain": domain,
            "is_affiliate": False,
            "network": None,
            "affiliate_id": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Check if it's an affiliate link
        query_params = parse_qs(parsed.query)

        for network_name, config in AFFILIATE_NETWORKS.items():
            if any(d in domain for d in config["domains"]):
                info["network"] = network_name
                aff_id = query_params.get(config["param"], [None])[0]
                if aff_id:
                    info["is_affiliate"] = True
                    info["affiliate_id"] = aff_id
                break

        return info

    except Exception as e:
        logger.error(f"Link info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _detect_network(url: str) -> tuple:
    """Detect affiliate network and commission rate from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    commission_rates = {
        "amazon": 3.0,
        "flipkart": 4.0,
        "myntra": 5.0,
        "ajio": 4.5,
        "earnkaro": 6.0,
    }

    for network_name, config in AFFILIATE_NETWORKS.items():
        if any(d in domain for d in config["domains"]):
            return network_name, commission_rates.get(network_name, 2.0)

    return None, 0.0


def _convert_url(url: str, network: Optional[str] = None) -> str:
    """Convert URL to affiliate URL"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    query_params = parse_qs(parsed.query)

    # Auto-detect network if not specified
    detected_network = network
    if not detected_network:
        for network_name, config in AFFILIATE_NETWORKS.items():
            if any(d in domain for d in config["domains"]):
                detected_network = network_name
                break

    if not detected_network or detected_network not in AFFILIATE_NETWORKS:
        return url

    config = AFFILIATE_NETWORKS[detected_network]
    param = config["param"]
    aff_id = config["default_id"]

    # Don't add if already has affiliate param
    if param in query_params:
        return url

    # Add affiliate parameter
    query_params[param] = [aff_id]
    new_query = urlencode(query_params, doseq=True)

    new_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )

    return new_url
