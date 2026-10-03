from fastapi import Request, HTTPException, Depends
from app.core.redis_cache import get_cache, set_cache, increment_cache
from app.api.v1.auth import oauth2_scheme, get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_optional_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        token_key = f"token:{token}"
        user_id = await get_cache(token_key)
        if not user_id:
            return None
        return await get_cache(f"user_id:{user_id}")
    except Exception as e:
        logger.warning(f"Error resolving optional user: {e}")
        return None

async def check_search_quota(request: Request, user: dict = Depends(get_optional_user)):
    """Check daily search quota for Free/Anonymous users (limit: 50 searches/day)"""
    if user and user.get("plan") in ["pro", "premium"]:
        return  # Unlimited for Pro/Premium
    
    # Identify user by ID or client IP
    identifier = user["id"] if user else f"anon:{request.client.host}"
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    cache_key = f"quota:search:{identifier}:{date_str}"
    
    current_count = await get_cache(cache_key) or 0
    if int(current_count) >= 50:
        raise HTTPException(
            status_code=402,
            detail="Daily search quota (50 searches) exceeded. Upgrade to Pro/Premium for unlimited searches!"
        )
    
    await increment_cache(cache_key, 1, expire_seconds=86400)

async def check_compare_quota(request: Request, user: dict = Depends(get_optional_user)):
    """Check daily comparison quota for Free/Anonymous users (limit: 5 comparisons/day)"""
    if user and user.get("plan") in ["pro", "premium"]:
        return  # Unlimited for Pro/Premium
        
    identifier = user["id"] if user else f"anon:{request.client.host}"
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    cache_key = f"quota:compare:{identifier}:{date_str}"
    
    current_count = await get_cache(cache_key) or 0
    if int(current_count) >= 5:
        raise HTTPException(
            status_code=402,
            detail="Daily comparison quota (5 comparisons) exceeded. Upgrade to Pro/Premium for unlimited comparisons!"
        )
        
    await increment_cache(cache_key, 1, expire_seconds=86400)
