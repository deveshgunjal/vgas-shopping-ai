"""Stripe Payment Integration"""
import stripe
import os
from typing import Dict

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

PLANS = {
    "free": {"price": 0, "name": "Free", "tracks": 5, "scan_interval": 21600},
    "pro": {"price": 9900, "name": "Pro", "tracks": -1, "scan_interval": 300, "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID", "")},
    "premium": {"price": 29900, "name": "Premium", "tracks": -1, "scan_interval": 60, "stripe_price_id": os.getenv("STRIPE_PREMIUM_PRICE_ID", "")},
}

def create_checkout_session(user_id: int, plan: str) -> Dict:
    """Create Stripe checkout session"""
    if plan not in PLANS or plan == "free":
        return {"error": "Invalid plan"}
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "upi"],
            line_items=[{
                "price": PLANS[plan]["stripe_price_id"],
                "quantity": 1,
            }],
            mode="subscription",
            success_url="http://localhost:8000/payment/success",
            cancel_url="http://localhost:8000/payment/cancel",
            metadata={"user_id": str(user_id), "plan": plan},
        )
        return {"session_id": session.id, "url": session.url}
    except Exception as e:
        return {"error": str(e)}

def retrieve_checkout_session(session_id: str) -> Dict:
    """Retrieve a checkout session from the REAL Stripe API.

    Returns {"error": ...} if the session does not exist or Stripe is
    unreachable. It never guesses — verification must come from Stripe.
    """
    if not stripe.api_key:
        return {"error": "STRIPE_SECRET_KEY is not configured"}
    if not session_id or not str(session_id).startswith("cs_"):
        return {"error": f"Not a Stripe checkout session id: {session_id!r}"}
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "session_id": session.id,
            "payment_status": session.payment_status,   # paid | unpaid | no_payment_required
            "status": session.status,                   # open | complete | expired
            "user_id": (session.metadata or {}).get("user_id"),
            "plan": (session.metadata or {}).get("plan"),
            "amount_total": session.amount_total,
            "currency": session.currency,
        }
    except Exception as e:
        return {"error": str(e)}


def handle_webhook(payload: bytes, sig_header: str) -> Dict:
    """Handle Stripe webhook"""
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET", ""))
        
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            return {"status": "success", "user_id": session["metadata"]["user_id"], "plan": session["metadata"]["plan"]}
        
        elif event["type"] == "customer.subscription.deleted":
            return {"status": "cancelled", "subscription": event["data"]["object"]["id"]}
        
        return {"status": "ignored"}
    except Exception as e:
        return {"error": str(e)}
