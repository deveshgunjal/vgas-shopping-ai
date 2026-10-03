"""Cart Service for VGAS Shopping AI"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models import User, ProductTrack, PriceHistory
from app.core.redis_cache import get_cache, set_cache, delete_cache
import logging

logger = logging.getLogger(__name__)

CART_PREFIX = "cart:"


class CartService:
    """Manages user shopping carts"""

    def __init__(self):
        self.carts = {}

    def get_cart(self, user_id: int, db: Session) -> Dict:
        """Get user's cart"""
        cached = get_cache(f"{CART_PREFIX}{user_id}")
        if cached:
            return cached

        cart_items = db.query(ProductTrack).filter(
            ProductTrack.user_id == user_id,
            ProductTrack.status == "in_cart"
        ).all()

        cart = {
            "user_id": user_id,
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "price": item.current_price,
                    "store": item.store,
                    "url": item.url,
                    "image_url": item.image_url,
                    "quantity": 1,
                    "added_at": item.created_at.isoformat() if item.created_at else datetime.utcnow().isoformat(),
                }
                for item in cart_items
            ],
            "total_items": len(cart_items),
            "total_price": sum(item.current_price or 0 for item in cart_items),
        }

        set_cache(f"{CART_PREFIX}{user_id}", cart, expire_seconds=3600)
        return cart

    def add_to_cart(self, user_id: int, product_id: int, db: Session) -> Dict:
        """Add product to cart"""
        track = db.query(ProductTrack).filter(
            ProductTrack.id == product_id,
            ProductTrack.user_id == user_id
        ).first()

        if not track:
            raise ValueError(f"Product {product_id} not found or not owned by user")

        track.status = "in_cart"
        db.commit()
        db.refresh(track)

        # Invalidate cache
        delete_cache(f"{CART_PREFIX}{user_id}")

        logger.info(f"Product {product_id} added to cart for user {user_id}")
        return {"id": track.id, "status": "in_cart", "title": track.title}

    def remove_from_cart(self, user_id: int, product_id: int, db: Session) -> bool:
        """Remove product from cart"""
        track = db.query(ProductTrack).filter(
            ProductTrack.id == product_id,
            ProductTrack.user_id == user_id
        ).first()

        if not track:
            return False

        track.status = "watching"
        db.commit()
        db.refresh(track)

        delete_cache(f"{CART_PREFIX}{user_id}")
        return True

    def clear_cart(self, user_id: int, db: Session) -> bool:
        """Clear entire cart"""
        db.query(ProductTrack).filter(
            ProductTrack.user_id == user_id,
            ProductTrack.status == "in_cart"
        ).update({"status": "watching"})
        db.commit()

        delete_cache(f"{CART_PREFIX}{user_id}")
        return True

    def get_cart_total(self, user_id: int, db: Session) -> Dict:
        """Calculate cart total with tax and shipping"""
        cart = self.get_cart(user_id, db)
        subtotal = cart["total_price"]
        tax = subtotal * 0.18  # 18% GST for India
        shipping = 0 if subtotal > 500 else 50
        total = subtotal + tax + shipping

        return {
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "shipping": shipping,
            "total": round(total, 2),
            "currency": "INR",
            "item_count": cart["total_items"],
        }


cart_service = CartService()
