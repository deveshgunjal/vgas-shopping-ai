"""Payment Integration API Endpoints for VGAS Shopping AI"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging

router = APIRouter(prefix="/payment", tags=["Payment"])
logger = logging.getLogger(__name__)


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "INR"
    method: str = "stripe"  # stripe, upi, razorpay
    user_id: int
    plan: Optional[str] = None
    upi_id: Optional[str] = None
    description: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    currency: str
    redirect_url: Optional[str] = None
    message: Optional[str] = None


@router.post("/stripe/checkout")
async def stripe_checkout(request: PaymentRequest):
    """Create Stripe checkout session"""
    try:
        from app.services.stripe_pay import create_checkout_session, PLANS
        
        if not request.plan or request.plan == "free":
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        if request.plan not in PLANS:
            raise HTTPException(status_code=400, detail="Plan not found")
        
        result = create_checkout_session(request.user_id, request.plan)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return PaymentResponse(
            payment_id=result["session_id"],
            status="pending",
            amount=PLANS[request.plan]["price"],
            currency="INR",
            redirect_url=result.get("url"),
            message="Checkout session created"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upi")
async def upi_payment(request: PaymentRequest):
    """Build a UPI payment intent (deep link only).

    This endpoint does NOT take money and does NOT confirm anything. It only
    builds a standard `upi://pay` intent for the user's own UPI app. Because
    there is no payment gateway in front of it, the returned status is always
    "unverified" — the app must not treat this as a successful payment.
    """
    try:
        if not request.upi_id:
            raise HTTPException(status_code=400, detail="UPI ID required")

        from urllib.parse import quote

        upi_url = (
            f"upi://pay?pa={quote(request.upi_id)}"
            f"&pn={quote('VGAS Shopping AI')}"
            f"&am={request.amount}&cu={request.currency}"
        )

        return PaymentResponse(
            payment_id=None,
            status="unverified",
            amount=request.amount,
            currency=request.currency,
            redirect_url=upi_url,
            message=(
                "UPI intent link generated. No payment gateway is connected, so this "
                "payment cannot be confirmed server-side and must not be treated as paid."
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPI payment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/stripe")
async def stripe_webhook():
    """Handle Stripe webhook"""
    try:
        from app.api.webhook import stripe_webhook as handle_stripe_webhook
        return await handle_stripe_webhook()
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify")
async def verify_payment(payment_id: str = "", method: str = "stripe"):
    """Verify payment status against the REAL payment provider.

    For Stripe this calls Stripe's API and reports what Stripe actually says.
    Anything that cannot be verified is reported as unverified — this endpoint
    never returns success for an ID it did not confirm with the provider.
    """
    try:
        if method == "stripe":
            from app.services.stripe_pay import retrieve_checkout_session

            result = retrieve_checkout_session(payment_id)
            if "error" in result:
                return {
                    "payment_id": payment_id,
                    "status": "unverified",
                    "verified": False,
                    "error": result["error"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Payment could not be confirmed with Stripe.",
                }

            paid = result.get("payment_status") == "paid"
            return {
                "payment_id": result.get("session_id"),
                "status": "paid" if paid else result.get("payment_status") or "unknown",
                "verified": paid,
                "user_id": result.get("user_id"),
                "plan": result.get("plan"),
                "amount_total": result.get("amount_total"),
                "currency": result.get("currency"),
                "source": "stripe_api",
                "timestamp": datetime.utcnow().isoformat(),
                "message": (
                    "Confirmed by the Stripe API."
                    if paid
                    else "Stripe has not reported this session as paid yet."
                ),
            }

        # No gateway exists for any other method, so nothing can be verified.
        return {
            "payment_id": payment_id,
            "status": "unverified",
            "verified": False,
            "source": None,
            "timestamp": datetime.utcnow().isoformat(),
            "message": (
                f"No payment gateway is connected for method '{method}'. "
                "This payment cannot be verified server-side."
            ),
        }
    except Exception as e:
        logger.error(f"Payment verify error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans")
async def get_payment_plans():
    """Get available subscription plans"""
    from app.services.stripe_pay import PLANS
    plans = []
    for name, config in PLANS.items():
        if name == "free":
            continue
        plans.append({
            "name": config["name"],
            "price": config["price"],
            "tracks": config["tracks"],
            "scan_interval": config["scan_interval"],
            "stripe_price_id": config.get("stripe_price_id", ""),
        })
    return {"plans": plans}


@router.get("/success")
async def payment_success():
    """Payment success page"""
    return {"status": "success", "message": "Payment completed successfully!"}


@router.get("/cancel")
async def payment_cancel():
    """Payment cancelled page"""
    return {"status": "cancelled", "message": "Payment was cancelled"}
