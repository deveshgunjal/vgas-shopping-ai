"""
Redis cache configuration for VGAS Shopping AI
"""

import redis.asyncio as redis
import json
from datetime import timedelta
from typing import Any, Optional, Dict, List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client
redis_client: Optional[redis.Redis] = None

# In-memory fallback cache (when Redis not available)
_memory_cache: Dict[str, Any] = {}
_memory_cache_expiry: Dict[str, float] = {}


async def init_redis():
    """Initialize Redis connection with in-memory fallback"""
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=False
        )
        pong = await redis_client.ping()
        if pong:
            logger.info("✅ Redis connection established")
    except Exception as e:
        logger.warning(f"⚠️ Redis not available ({e}). Using in-memory cache fallback.")
        redis_client = None


async def get_redis():
    """Get Redis client"""
    if redis_client is None:
        await init_redis()
    return redis_client


# Cache helpers
import time as _time


def _mem_set(key: str, value: Any, expire_seconds: int = 3600):
    _memory_cache[key] = value
    _memory_cache_expiry[key] = _time.time() + expire_seconds


def _mem_get(key: str) -> Optional[Any]:
    expiry = _memory_cache_expiry.get(key, 0)
    if _time.time() > expiry:
        _memory_cache.pop(key, None)
        _memory_cache_expiry.pop(key, None)
        return None
    return _memory_cache.get(key)


async def set_cache(key: str, value: Any, expire_seconds: int = 3600) -> bool:
    """Set value in cache (Redis or memory fallback)"""
    try:
        if redis_client:
            serialized = json.dumps(value) if isinstance(value, (dict, list)) else value
            await redis_client.setex(key, expire_seconds, serialized)
        else:
            _mem_set(key, value, expire_seconds)
        return True
    except Exception as e:
        _mem_set(key, value, expire_seconds)
        return True


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache (Redis or memory fallback)"""
    try:
        if redis_client:
            value = await redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        else:
            return _mem_get(key)
    except Exception as e:
        return _mem_get(key)


async def delete_cache(key: str) -> bool:
    """Delete value from cache"""
    try:
        if redis_client:
            await redis_client.delete(key)
        _memory_cache.pop(key, None)
        _memory_cache_expiry.pop(key, None)
        return True
    except Exception as e:
        return False


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache"""
    try:
        if redis_client:
            return await redis_client.exists(key) > 0
        return _mem_get(key) is not None
    except Exception as e:
        return False


async def increment_cache(key: str, amount: int = 1, expire_seconds: int = None) -> int:
    """Increment cache value"""
    try:
        if redis_client:
            if expire_seconds:
                await redis_client.expire(key, expire_seconds)
            return await redis_client.incrby(key, amount)
        current = _mem_get(key) or 0
        new_val = int(current) + amount
        _mem_set(key, new_val, expire_seconds or 3600)
        return new_val
    except Exception as e:
        return 0


# Cache keys constants
class CacheKeys:
    """Cache key constants"""
    
    # Product cache
    PRODUCT_BY_URL = "product:url:{}"
    PRODUCT_BY_ID = "product:id:{}"
    PRODUCT_BY_ASIN = "product:asin:{}"
    PRODUCT_SEARCH = "search:{}:{}"  # query:page
    
    # Store cache
    STORE_BY_DOMAIN = "store:domain:{}"
    STORE_BY_ID = "store:id:{}"
    
    # Price history
    PRICE_HISTORY = "price_history:{}"  # product_id
    
    # Affiliate
    AFFILIATE_LINK = "affiliate:{}"  # original_url
    
    # AI
    AI_CHAT_SESSION = "ai_session:{}"  # session_id
    
    # Stats
    TOTAL_USERS = "stats:total_users"
    TOTAL_SEARCHES = "stats:total_searches"
    TOTAL_PRODUCTS = "stats:total_products"
    DAILY_SEARCHES = "stats:daily_searches:{}"  # date
    
    # Rate limiting
    RATE_LIMIT = "rate_limit:{}"  # ip_address
    
    # WhatsApp
    WHATSAPP_SESSION = "whatsapp:session"
    WHATSAPP_QR = "whatsapp:qr"
    
    # Currency
    EXCHANGE_RATES = "exchange_rates"
    
    # Comparison
    COMPARISON_RESULT = "comparison:{}"  # comparison_id


# Cache decorators
def cached(timeout: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        import functools
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            import hashlib
            key_data = f"{func.__name__}:{args}:{frozenset(kwargs.items())}"
            cache_key = f"func:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # Check cache
            cached_value = await get_cache(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await set_cache(cache_key, result, timeout)
            return result
        return wrapper
    return decorator
