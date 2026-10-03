"""Cart API Endpoints for VGAS Shopping AI"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ProductTrack
from app.services.cart import cart_service
from app.api.v1.auth import oauth2_scheme, get_current_user
import logging

router = APIRouter(prefix="/cart", tags=["Cart"])
logger = logging.getLogger(__name__)


class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdateRequest(BaseModel):
    product_id: int
    action: str  # "add", "remove", "update"
    quantity: Optional[int] = 1


@router.post("/")
async def add_to_cart(req: AddToCartRequest, db: Session = Depends(get_db)):
    """Add a product to cart"""
    try:
        result = cart_service.add_to_cart(req.product_id, req.product_id, db)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Add to cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_cart(db: Session = Depends(get_db)):
    """Get user's cart"""
    try:
        user = await get_current_user(token=Depends(oauth2_scheme).__wrapped__(db))
        # Get user id from db
        user_id = None
        for u in db.query(User).all():
            if hasattr(u, 'id'):
                user_id = u.id
                break
        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")
        cart = cart_service.get_cart(user_id, db)
        return cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/total")
async def get_cart_total(db: Session = Depends(get_db)):
    """Get cart total with tax and shipping"""
    try:
        user = await get_current_user(token=Depends(oauth2_scheme).__wrapped__(db))
        user_id = None
        for u in db.query(User).all():
            user_id = u.id
            break
        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")
        total = cart_service.get_cart_total(user_id, db)
        return total
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cart total error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}")
async def remove_from_cart(product_id: int, db: Session = Depends(get_db)):
    """Remove product from cart"""
    try:
        user_id = None
        for u in db.query(User).all():
            user_id = u.id
            break
        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")
        success = cart_service.remove_from_cart(user_id, product_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Product not in cart")
        return {"status": "removed", "product_id": product_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove from cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/")
async def clear_cart(db: Session = Depends(get_db)):
    """Clear entire cart"""
    try:
        user_id = None
        for u in db.query(User).all():
            user_id = u.id
            break
        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")
        cart_service.clear_cart(user_id, db)
        return {"status": "cleared"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear cart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
