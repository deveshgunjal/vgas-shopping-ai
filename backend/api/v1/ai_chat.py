#!/usr/bin/env python3
"""VGAS AI Chat - Real working endpoint using GROQ."""
import os
import time
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/chat", tags=["AI Chat"])

GROQ_KEY = os.getenv("GROQ_API_KEY_ALT", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are VGAS Shopping AI - India's best price comparison assistant.
Help users find cheapest products across Amazon, Flipkart, Meesho.
Be helpful, suggest deals, compare prices. Reply in the user's language."""


class ChatRequest(BaseModel):
    message: str
    system: Optional[str] = None
    max_tokens: int = 500


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    latency: float
    status: str


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """AI Shopping Chat - auto-routes to working provider."""
    if not GROQ_KEY:
        raise HTTPException(status_code=503, detail="No API key configured")

    messages = [
        {"role": "system", "content": req.system or SYSTEM_PROMPT},
        {"role": "user", "content": req.message},
    ]

    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "allam-2-7b",
                    "messages": messages,
                    "max_tokens": req.max_tokens,
                    "temperature": 0.7,
                },
            )
            latency = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return ChatResponse(
                    response=content,
                    provider="groq",
                    model="allam-2-7b",
                    latency=round(latency, 2),
                    status="success",
                )
            else:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Provider error: {resp.text[:200]}",
                )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Provider timeout")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:200])


@router.get("/health")
async def chat_health():
    return {
        "status": "healthy",
        "provider": "groq",
        "model": "allam-2-7b",
        "has_key": bool(GROQ_KEY),
    }
