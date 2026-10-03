"""Product Tracking API"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ProductTrack, PriceHistory, User
from ..scrapers.crawler import crawler

router = APIRouter()

class TrackRequest(BaseModel):
    url: str
    target_price: float = 0
    user_id: int

@router.post("/api/v1/track")
async def track_product(req: TrackRequest, db: Session = Depends(get_db)):
    """Start tracking a product"""
    # Enforce tracking limit (max 5 active tracked items) for Free users
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user or user.plan not in ["pro", "premium"]:
        count = db.query(ProductTrack).filter(ProductTrack.user_id == req.user_id, ProductTrack.status == "watching").count()
        if count >= 5:
            raise HTTPException(
                status_code=402,
                detail="Tracking quota (5 products) exceeded. Upgrade to Pro/Premium for unlimited tracking!"
            )
            
    result = await crawler.crawl(req.url)
    
    track = ProductTrack(
        user_id=req.user_id,
        url=req.url,
        title=result.get("title", "Unknown"),
        image_url=result.get("image_url", ""),
        current_price=result.get("price", 0),
        target_price=req.target_price,
        store=result.get("store", "unknown"),
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    
    if result.get("price"):
        history = PriceHistory(
            product_id=track.id,
            price=result["price"],
            store=result.get("store", "unknown"),
        )
        db.add(history)
        db.commit()
    
    return {"id": track.id, "status": "tracking", "price": result.get("price")}

@router.get("/api/v1/price-history/{product_id}")
async def get_price_history(product_id: int, db: Session = Depends(get_db)):
    """Get price history for a product"""
    history = db.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(PriceHistory.recorded_at).all()
    return [{"date": h.recorded_at.isoformat(), "price": h.price, "store": h.store} for h in history]
