"""Vgas Shopping AI v3.0 - FastAPI Main App"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from .database import init_db
from .api import track, leaderboard, webhook
from .services import whatsapp
from .api.v1 import (
    search as search_v1,
    products as products_v1,
    compare as compare_v1,
    affiliate as affiliate_v1,
    ai as ai_v1,
    monetization as monetization_v1,
    auth as auth_v1,
    auto_checkout as auto_checkout_v1,
    wallet as wallet_v1,
    arbitrage as arbitrage_v1,
    voice_ai as voice_ai_v1,
    brand_dashboard as brand_dashboard_v1,
    system as system_v1,
    sam as sam_v1,
    whatsapp as whatsapp_api_v1,
    cart as cart_v1,
    payment as payment_v1,
    admin as admin_v1,
    health as health_v1,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    init_db()
    print("Vgas Shopping AI v3.0 - Server Started!")
    yield
    print("Server Shutdown")

app = FastAPI(
    title="Vgas Shopping AI v3.0",
    description="AI-Powered Deal Snatcher & Price Optimization Platform",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(track.router)
app.include_router(leaderboard.router)
app.include_router(webhook.router)
app.include_router(whatsapp.router)

# Include v1 routers
app.include_router(search_v1.router, prefix="/api/v1")
app.include_router(products_v1.router, prefix="/api/v1")
app.include_router(compare_v1.router, prefix="/api/v1")
app.include_router(affiliate_v1.router, prefix="/api/v1")
app.include_router(ai_v1.router, prefix="/api/v1")
app.include_router(monetization_v1.router, prefix="/api/v1")
app.include_router(auth_v1.router, prefix="/api/v1")
app.include_router(auto_checkout_v1.router, prefix="/api/v1")
app.include_router(wallet_v1.router, prefix="/api/v1")
app.include_router(arbitrage_v1.router, prefix="/api/v1")
app.include_router(voice_ai_v1.router, prefix="/api/v1")
app.include_router(brand_dashboard_v1.router, prefix="/api/v1")
app.include_router(system_v1.router, prefix="/api/v1")
app.include_router(sam_v1.router, prefix="/api/v1")
app.include_router(whatsapp_api_v1.router, prefix="/api/v1")
app.include_router(cart_v1.router, prefix="/api/v1")
app.include_router(payment_v1.router, prefix="/api/v1")
app.include_router(admin_v1.router, prefix="/api/v1")
app.include_router(health_v1.router)

@app.get("/")
async def root():
    return {"message": "Vgas Shopping AI v3.0 - Running!", "docs": "/docs"}

@app.get("/api/v1/plans")
async def get_plans():
    return {
        "plans": [
            {"name": "Free", "price": 0, "tracks": 5, "features": ["5 items", "6-hour scans", "Basic leaderboard"]},
            {"name": "Pro", "price": 99, "tracks": -1, "features": ["Unlimited items", "5-min scans", "Early alerts", "Ad-free"]},
            {"name": "Premium", "price": 299, "tracks": -1, "features": ["Everything in Pro", "API access", "White-label", "Priority support"]},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
