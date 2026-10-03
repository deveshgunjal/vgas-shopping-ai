"""
System API endpoints for VGAS Shopping AI
Health check, system stats, configuration, monitoring
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import platform
import psutil
import os

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/system", tags=["System"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """System health check"""
    try:
        return {
            "status": "healthy",
            "service": "VGAS Shopping AI",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu": {
                "percent": cpu_percent,
                "cores": psutil.cpu_count(),
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent,
            },
            "platform": {
                "system": platform.system(),
                "version": platform.version(),
                "python": platform.python_version(),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"System stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config():
    """Get system configuration (non-sensitive)"""
    try:
        return {
            "app_name": settings.APP_NAME,
            "version": "1.0.0",
            "debug": settings.DEBUG,
            "cors_origins": settings.CORS_ORIGINS,
            "rate_limit": settings.RATE_LIMIT,
            "supported_countries": ["India", "USA", "UK", "UAE", "Japan", "Germany"],
            "supported_stores": [
                "Amazon",
                "Flipkart",
                "Myntra",
                "Ajio",
                "Croma",
                "Tata CLiQ",
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uptime")
async def get_uptime():
    """Get system uptime"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.utcnow() - boot_time).total_seconds()

        return {
            "boot_time": boot_time.isoformat(),
            "uptime_seconds": int(uptime_seconds),
            "uptime_days": round(uptime_seconds / 86400, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Uptime error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version")
async def get_version():
    """Get application version"""
    return {
        "app": "VGAS Shopping AI",
        "version": "1.0.0",
        "build": "20260810",
        "api_version": "v1",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/env")
async def get_environment():
    """Get environment info"""
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "node": os.getenv("NODE_NAME", "main"),
        "region": os.getenv("REGION", "india"),
        "timestamp": datetime.utcnow().isoformat(),
    }
