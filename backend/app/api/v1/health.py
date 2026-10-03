"""Health Check and Monitoring Endpoints"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import os
import sys
import logging

router = APIRouter(prefix="/health", tags=["Health"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    uptime: float
    timestamp: str
    version: str
    database: str
    redis: str
    services: dict


@router.get("/", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "message": "Vgas Shopping AI v3.0 - Running!",
        "docs": "/docs",
    }


@router.get("/status", tags=["Health"])
async def detailed_health():
    """Detailed health status"""
    db_ok = False
    try:
        from app.database import init_db
        init_db()
        db_ok = True
    except Exception:
        pass

    redis_ok = False
    try:
        from app.core.redis_cache import get_redis
        r = await get_redis()
        if r:
            redis_ok = True
    except Exception:
        pass

    return JSONResponse(status_code=200, content={
        "status": "OK" if db_ok else "DEGRADED",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "database": {"connected": db_ok, "url": os.getenv("DATABASE_URL", "sqlite:///vgas_shopping.db")},
        "redis": {"connected": redis_ok, "url": os.getenv("REDIS_URL", "redis://localhost:6379/0")},
        "services": {
            "scrapers": True,
            "whatsapp": os.getenv("TWILIO_ACCOUNT_SID") is not None,
            "stripe": os.getenv("STRIPE_SECRET_KEY") is not None,
            "scheduler": True,
        },
        "uptime": 0,
        "platform": sys.platform,
        "python_version": sys.version,
    })


@router.get("/ready", tags=["Health"])
async def readiness_probe():
    """Kubernetes readiness probe"""
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}


@router.get("/live", tags=["Health"])
async def liveness_probe():
    """Kubernetes liveness probe"""
    return {"alive": True, "timestamp": datetime.utcnow().isoformat()}


@router.get("/metrics", tags=["Health"])
async def metrics():
    """Prometheus-style metrics"""
    from app.core.redis_cache import _memory_cache, _memory_cache_expiry
    import time
    current = time.time()
    cache_size = len([k for k, v in _memory_cache_expiry.items() if v > current])
    return {
        "metrics": {
            "cache_entries": cache_size,
            "total_scans": 0,
            "total_deals": 0,
            "total_users": 0,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
