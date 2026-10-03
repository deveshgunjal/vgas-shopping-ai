"""
WhatsApp API endpoints for VGAS Shopping AI
WhatsApp bot integration, notifications, messaging
"""

from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])
logger = logging.getLogger(__name__)


class WhatsAppMessageRequest(BaseModel):
    phone: str = Field(..., description="Phone number with country code")
    message: str = Field(..., description="Message text")


class WhatsAppWebhook(BaseModel):
    webhook_id: str = Field(..., description="Webhook ID")
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(default={}, description="Event data")


@router.get("/status")
async def get_whatsapp_status():
    """Get WhatsApp bot status"""
    try:
        session = await get_cache(CacheKeys.WHATSAPP_SESSION)
        qr = await get_cache(CacheKeys.WHATSAPP_QR)

        return {
            "status": "connected" if session else "disconnected",
            "qr_available": bool(qr),
            "session_active": bool(session),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"WhatsApp status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_message(request: WhatsAppMessageRequest = Body(...)):
    """Send a WhatsApp message"""
    try:
        vgas_logger.info(f"WhatsApp message to {request.phone}")

        session = await get_cache(CacheKeys.WHATSAPP_SESSION)
        if not session:
            return {
                "success": False,
                "message": "WhatsApp bot not connected. Please connect first.",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Store pending message
        pending_key = f"whatsapp_pending:{request.phone}"
        await set_cache(
            pending_key,
            {
                "phone": request.phone,
                "message": request.message,
                "timestamp": datetime.utcnow().isoformat(),
            },
            expire_seconds=3600,
        )

        return {
            "success": True,
            "message": "Message queued for delivery",
            "phone": request.phone,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-bulk")
async def send_bulk_messages(messages: List[WhatsAppMessageRequest] = Body(...)):
    """Send bulk WhatsApp messages"""
    try:
        results = []
        for msg in messages:
            try:
                pending_key = f"whatsapp_pending:{msg.phone}"
                await set_cache(
                    pending_key,
                    {
                        "phone": msg.phone,
                        "message": msg.message,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    expire_seconds=3600,
                )
                results.append({"phone": msg.phone, "success": True})
            except Exception as e:
                results.append({"phone": msg.phone, "success": False, "error": str(e)})

        return {
            "total": len(messages),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"WhatsApp bulk send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alert/price-drop")
async def send_price_drop_alert(
    phone: str = Body(..., embed=True),
    product_name: str = Body(..., embed=True),
    old_price: float = Body(..., embed=True),
    new_price: float = Body(..., embed=True),
    product_url: str = Body(..., embed=True),
):
    """Send price drop alert via WhatsApp"""
    try:
        savings = old_price - new_price
        discount_pct = round((savings / old_price) * 100, 1) if old_price > 0 else 0

        message = (
            f"🔥 PRICE DROP ALERT!\n\n"
            f"Product: {product_name}\n"
            f"Old Price: ₹{old_price:,.2f}\n"
            f"New Price: ₹{new_price:,.2f}\n"
            f"You Save: ₹{savings:,.2f} ({discount_pct}%)\n\n"
            f"Buy now: {product_url}\n\n"
            f"- VGAS Shopping AI"
        )

        pending_key = f"whatsapp_pending:{phone}"
        await set_cache(
            pending_key,
            {
                "phone": phone,
                "message": message,
                "type": "price_drop_alert",
                "timestamp": datetime.utcnow().isoformat(),
            },
            expire_seconds=3600,
        )

        return {
            "success": True,
            "message": "Price drop alert sent",
            "savings": savings,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Price drop alert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def whatsapp_webhook(request: WhatsAppWebhook = Body(...)):
    """Handle WhatsApp webhooks"""
    try:
        vgas_logger.info(f"WhatsApp webhook: {request.event}")

        if request.event == "message":
            # Process incoming message
            phone = request.data.get("from", "")
            text = request.data.get("text", "")

            # Simple auto-reply
            reply = _process_whatsapp_message(text)

            if reply:
                await set_cache(
                    f"whatsapp_reply:{phone}",
                    {
                        "phone": phone,
                        "message": reply,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    expire_seconds=3600,
                )

        return {
            "received": True,
            "event": request.event,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr")
async def get_qr_code():
    """Get WhatsApp QR code for connection"""
    try:
        qr = await get_cache(CacheKeys.WHATSAPP_QR)
        if qr:
            return {"qr": qr, "timestamp": datetime.utcnow().isoformat()}

        return {
            "qr": None,
            "message": "No QR code available. Start the WhatsApp bot first.",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"WhatsApp QR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscribe")
async def subscribe_to_alerts(
    phone: str = Body(..., embed=True),
    product_name: str = Body(..., embed=True),
    target_price: float = Body(..., embed=True),
):
    """Subscribe to price alerts for a product"""
    try:
        cache_key = f"whatsapp_alert:{phone}:{product_name}"
        await set_cache(
            cache_key,
            {
                "phone": phone,
                "product": product_name,
                "target_price": target_price,
                "subscribed_at": datetime.utcnow().isoformat(),
                "active": True,
            },
            expire_seconds=86400 * 30,
        )

        return {
            "success": True,
            "message": f"You'll be notified when '{product_name}' drops to ₹{target_price}",
            "phone": phone,
            "product": product_name,
            "target_price": target_price,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _process_whatsapp_message(text: str) -> Optional[str]:
    """Process incoming WhatsApp message and generate reply"""
    text = text.lower().strip()

    if any(g in text for g in ["hi", "hello", "hey"]):
        return "👋 Hello! VGAS Shopping AI Bot. Send me a product name to search!"

    if any(w in text for w in ["deal", "offer", "discount"]):
        return "🔥 Check our website for the best deals! Visit: vgas-ai.com/deals"

    if any(w in text for w in ["help", "menu"]):
        return (
            "📱 VGAS Shopping AI Menu:\n\n"
            "1. Send a product name to search\n"
            "2. Send 'deals' for best offers\n"
            "3. Send 'subscribe [product] [price]' for alerts\n"
            "4. Send 'help' for this menu"
        )

    # Default: treat as product search
    return f"🔍 Searching for '{text}'... Check vgas-ai.com for results!"
