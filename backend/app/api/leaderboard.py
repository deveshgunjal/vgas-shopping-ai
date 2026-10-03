"""Deal Leaderboard API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import ProductTrack

router = APIRouter()

@router.get("/api/v1/leaderboard")
async def get_leaderboard(db: Session = Depends(get_db)):
    """Get top 10 deals"""
    products = db.query(ProductTrack).filter(
        ProductTrack.current_price > 0,
        ProductTrack.target_price > 0,
    ).all()
    
    deals = []
    for p in products:
        if p.target_price > 0:
            discount = ((p.target_price - p.current_price) / p.target_price) * 100
            deals.append({
                "id": p.id,
                "title": p.title or "Unknown",
                "current_price": p.current_price,
                "original_price": p.target_price,
                "discount_percent": round(discount, 1),
                "store": p.store,
                "url": p.url,
            })
    
    deals.sort(key=lambda x: x["discount_percent"], reverse=True)
    return {"deals": deals[:10]}

@router.get("/api/v1/deals/today")
async def get_todays_deals(db: Session = Depends(get_db)):
    """Get today's best deals"""
    from datetime import datetime, timedelta
    today = datetime.utcnow() - timedelta(hours=24)
    
    products = db.query(ProductTrack).filter(
        ProductTrack.created_at >= today,
        ProductTrack.current_price > 0,
    ).all()
    
    return {"count": len(products), "deals": [{"title": p.title, "price": p.current_price, "store": p.store} for p in products[:20]]}
