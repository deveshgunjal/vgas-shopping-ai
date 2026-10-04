"""Webhook Handlers"""
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..services.stripe_pay import handle_webhook
from ..database import get_db
from ..models import User
from ..core.redis_cache import get_cache, set_cache

router = APIRouter()

class UPIPaymentRequest(BaseModel):
    user_id: int
    utr_number: str
    amount: float
    plan: str

async def upgrade_user_plan(user_id: int, plan: str, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.plan = plan
        user.is_premium = (plan in ["pro", "premium"])
        db.commit()
        db.refresh(user)
        
        # Sync to Redis cache
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "name": user.username,
            "phone": user.phone,
            "plan": user.plan,
            "is_premium": user.is_premium,
            "referral_code": user.referral_code,
        }
        await set_cache(f"user_id:{user.id}", user_data, expire_seconds=86400 * 365)
        if user.email:
            await set_cache(f"user:{user.email}", user_data, expire_seconds=86400 * 365)
        if user.phone:
            await set_cache(f"user:{user.phone}", user_data, expire_seconds=86400 * 365)
        return True
    return False

@router.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    result = handle_webhook(payload, sig_header)
    
    if result.get("status") == "success":
        user_id = result.get("user_id")
        plan = result.get("plan")
        if user_id and plan:
            try:
                await upgrade_user_plan(int(user_id), plan, db)
            except Exception as e:
                return {"status": "error", "message": f"Failed to upgrade user: {e}"}
                
    return result

@router.post("/api/v1/payment/upi")
async def upi_payment_track(req: UPIPaymentRequest, db: Session = Depends(get_db)):
    """Manual UPI payment claim — REFUSED, because nothing here can verify it.

    This endpoint used to accept any self-reported UTR/reference number and
    immediately upgrade the caller's plan to Pro/Premium. That granted paid
    features for free to anyone who posted ten characters, so the "verification"
    was pure theatre.

    A UTR can only be trusted if something authoritative confirms the money
    arrived. That requires one of:
      * a payment gateway that supports UPI and exposes a server-side
        verify/payment API (Razorpay, Cashfree, PhonePe Business), or
      * a bank statement reconciliation feed.

    Neither is integrated, and there is no payment ledger table to record an
    unverified claim in. So the endpoint reports that honestly instead of
    upgrading anybody. Use POST /api/v1/payment/stripe/checkout for a real,
    signature-verified upgrade.
    """
    if req.plan not in ["pro", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid plan requested")

    raise HTTPException(
        status_code=501,
        detail={
            "error": "upi_verification_unavailable",
            "message": (
                "Manual UPI plan upgrades are disabled. A submitted UTR/reference "
                "number cannot be verified by this server, so no plan is granted."
            ),
            "why_not_just_trust_the_utr": (
                "The UTR is supplied by the caller. Accepting it unverified would "
                "let anyone self-upgrade to a paid plan for free."
            ),
            "use_instead": "POST /api/v1/payment/stripe/checkout",
            "required_to_re_enable": [
                "Integrate a UPI-capable payment gateway with a server-side verify API",
                "Add a payments ledger table to record each attempt and its outcome",
            ],
        },
    )

@router.get("/api/v1/whatsapp/webhook")
async def whatsapp_verify():
    """Twilio webhook verification"""
    return {"status": "ok"}
