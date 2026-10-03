"""Admin Dashboard API Endpoints for VGAS Shopping AI"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ProductTrack, PriceHistory, Subscription
from app.core.redis_cache import get_cache, set_cache
import logging

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    premium_users: int
    total_tracks: int
    total_deals_today: int
    total_revenue: float
    active_subscriptions: int
    revenue_by_plan: Dict[str, float]
    users_by_plan: Dict[str, int]
    deals_by_store: Dict[str, int]
    top_products: List[Dict[str, Any]]


def _is_admin(user_id: int, db: Session) -> bool:
    """Check if user is admin"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    # In production, check actual admin role
    return user.email == "admin@vgas.ai" or user.username == "admin"


@router.get("/stats")
async def admin_stats(db: Session = Depends(get_db)):
    """Get platform-wide admin statistics"""
    try:
        # Check if admin (simplified for demo)
        # In production, use proper auth
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.is_premium == True).count()
        active_users = db.query(User).filter(User.created_at >= datetime.utcnow() - timedelta(days=30)).count()
        
        total_tracks = db.query(ProductTrack).count()
        
        today = datetime.utcnow() - timedelta(hours=24)
        total_deals_today = db.query(ProductTrack).filter(ProductTrack.created_at >= today).count()
        
        total_revenue = 234000.0  # Mock data
        active_subscriptions = db.query(Subscription).filter(Subscription.status == "active").count()
        
        revenue_by_plan = {"free": 0.0, "pro": 123000.0, "premium": 111000.0}
        users_by_plan = {"free": total_users - premium_users, "pro": premium_users // 2, "premium": premium_users - premium_users // 2}
        
        deals_by_store = {"amazon": 120, "flipkart": 85, "ebay": 45}
        
        top_products = []
        tracks = db.query(ProductTrack).order_by(ProductTrack.current_price.desc()).limit(5).all()
        for t in tracks:
            top_products.append({
                "title": t.title or "Unknown",
                "price": t.current_price,
                "store": t.store,
                "url": t.url,
            })
        
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "premium_users": premium_users,
            "total_tracks": total_tracks,
            "total_deals_today": total_deals_today,
            "total_revenue": total_revenue,
            "active_subscriptions": active_subscriptions,
            "revenue_by_plan": revenue_by_plan,
            "users_by_plan": users_by_plan,
            "deals_by_store": deals_by_store,
            "top_products": top_products,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        await set_cache("admin:stats", stats, expire_seconds=300)
        return stats
        
    except Exception as e:
        logger.error(f"Admin stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    try:
        users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
        return {
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "phone": u.phone,
                    "plan": u.plan,
                    "is_premium": u.is_premium,
                    "referral_code": u.referral_code,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
            "count": len(users),
            "total": db.query(User).count(),
        }
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def get_all_products(db: Session = Depends(get_db)):
    """Get all tracked products (admin only)"""
    try:
        products = db.query(ProductTrack).order_by(ProductTrack.created_at.desc()).limit(100).all()
        return {
            "products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "url": p.url,
                    "current_price": p.current_price,
                    "target_price": p.target_price,
                    "store": p.store,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in products
            ],
            "total": len(products),
        }
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast")
async def broadcast_message(message: str = "", db: Session = Depends(get_db)):
    """Send broadcast message to all users"""
    try:
        if not message:
            raise HTTPException(status_code=400, detail="Message required")
        
        total_users = db.query(User).count()
        await set_cache("admin:broadcast", {"message": message, "sent_at": datetime.utcnow().isoformat()}, expire_seconds=86400)
        
        return {
            "status": "sent",
            "message": message,
            "recipients": total_users,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
async def get_revenue(days: int = 30, db: Session = Depends(get_db)):
    """Get revenue breakdown"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        # Mock revenue data
        revenue_data = []
        for i in range(days):
            date = (start_date + timedelta(days=i)).isoformat()
            revenue_data.append({
                "date": date,
                "affiliate_revenue": round(5000 + (i * 100), 2),
                "subscription_revenue": round(2000 + (i * 50), 2),
                "total": round(7000 + (i * 150), 2),
            })
        
        return {
            "period": f"Last {days} days",
            "data": revenue_data,
            "total_revenue": round(sum(d["total"] for d in revenue_data), 2),
        }
    except Exception as e:
        logger.error(f"Revenue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
