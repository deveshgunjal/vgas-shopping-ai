"""
Wallet API endpoints for VGAS Shopping AI
User wallet, balance, transactions, rewards
"""

from fastapi import APIRouter, Query, HTTPException, Body, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import secrets

from app.core.redis_cache import get_cache, set_cache
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/wallet", tags=["Wallet"])
logger = logging.getLogger(__name__)


class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = Field(..., description="credit or debit")
    description: str = Field(default="")


@router.get("/balance")
async def get_balance(user_id: str = Query(...)):
    """Get wallet balance"""
    try:
        wallet = await get_cache(f"wallet:{user_id}") or {
            "user_id": user_id,
            "balance": 0.0,
            "currency": "INR",
            "created_at": datetime.utcnow().isoformat(),
        }
        return {"wallet": wallet, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Balance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credit")
async def credit_wallet(
    user_id: str = Body(..., embed=True),
    request: TransactionRequest = Body(...),
):
    """Credit wallet"""
    try:
        if request.type != "credit":
            raise HTTPException(status_code=400, detail="Type must be 'credit'")

        wallet = await get_cache(f"wallet:{user_id}") or {
            "user_id": user_id,
            "balance": 0.0,
            "currency": "INR",
            "transactions": [],
        }
        wallet["balance"] = round(wallet.get("balance", 0) + request.amount, 2)

        txn = {
            "id": secrets.token_hex(8),
            "type": "credit",
            "amount": request.amount,
            "description": request.description or "Wallet credit",
            "timestamp": datetime.utcnow().isoformat(),
        }
        wallet.setdefault("transactions", []).append(txn)

        await set_cache(f"wallet:{user_id}", wallet, expire_seconds=86400 * 30)
        return {
            "success": True,
            "wallet": wallet,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debit")
async def debit_wallet(
    user_id: str = Body(..., embed=True),
    request: TransactionRequest = Body(...),
):
    """Debit wallet"""
    try:
        if request.type != "debit":
            raise HTTPException(status_code=400, detail="Type must be 'debit'")

        wallet = await get_cache(f"wallet:{user_id}")
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        if wallet.get("balance", 0) < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        wallet["balance"] = round(wallet["balance"] - request.amount, 2)

        txn = {
            "id": secrets.token_hex(8),
            "type": "debit",
            "amount": request.amount,
            "description": request.description or "Wallet debit",
            "timestamp": datetime.utcnow().isoformat(),
        }
        wallet.setdefault("transactions", []).append(txn)

        await set_cache(f"wallet:{user_id}", wallet, expire_seconds=86400 * 30)
        return {
            "success": True,
            "wallet": wallet,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Debit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions")
async def get_transactions(
    user_id: str = Query(...),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get transaction history"""
    try:
        wallet = await get_cache(f"wallet:{user_id}")
        if not wallet:
            return {
                "transactions": [],
                "total": 0,
                "timestamp": datetime.utcnow().isoformat(),
            }

        transactions = wallet.get("transactions", [])[-limit:]
        return {
            "transactions": transactions,
            "total": len(transactions),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Transactions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rewards")
async def get_rewards(user_id: str = Query(...)):
    """Get user rewards and cashback"""
    try:
        return {
            "user_id": user_id,
            "total_earned": 0.0,
            "total_redeemed": 0.0,
            "available": 0.0,
            "rewards": [],
            "note": "Rewards will accumulate as you use VGAS Shopping AI",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Rewards error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
