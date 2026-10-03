from __future__ import annotations
import hashlib
import json
import os
import re
import time
from typing import Any, Optional

import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BRAIN_URL = "http://127.0.0.1:5000/v1/chat/completions"
MODEL = "el-claude-fable-5.1"
STORES = ["amazon", "flipkart", "ebay", "walmart", "myntra", "nykaa"]
COMMISSION = {"amazon": 0.08, "flipkart": 0.07, "ebay": 0.05, "walmart": 0.04, "myntra": 0.10, "nykaa": 0.09}

app = FastAPI(title="Vgas Shopping AI v3")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Serve React build
BUILD_DIR = r"D:\Projects\Vgas Shooping Ai\web\build"
STATIC_DIR = r"D:\Projects\Vgas Shooping Ai\web\build\static"
if os.path.isdir(BUILD_DIR):
    # Serve static files via custom routes (StaticFiles not working on this system)
    @app.get("/static/js/{filename}")
    async def serve_js(filename: str):
        file_path = os.path.join(STATIC_DIR, "js", filename)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404)
    
    @app.get("/static/css/{filename}")
    async def serve_css(filename: str):
        file_path = os.path.join(STATIC_DIR, "css", filename)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404)
    
    # Catch-all for SPA: serve index.html for all non-API, non-static routes
    @app.get("/{full_path:path}")
    async def spa_catch_all(full_path: str):
        # Skip API routes and static files
        if full_path.startswith("api/") or full_path.startswith("static/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            raise HTTPException(status_code=404)
        index_path = os.path.join(BUILD_DIR, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
        return HTMLResponse('<h1>Vgas Shopping AI v3</h1><p>Build not found</p>')

ALERTS: list[dict[str, Any]] = []
CART: list[dict[str, Any]] = []
AID = [0]
CID = [0]


class AlertIn(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    target_price: float = Field(gt=0)
    contact: Optional[str] = None


class CartIn(BaseModel):
    store: str = "amazon"
    title: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)
    qty: int = Field(default=1, ge=1, le=99)


def fallback_prices(q: str) -> list[dict[str, Any]]:
    out = []
    for s in STORES:
        h = int(hashlib.md5(f"{q}:{s}".encode()).hexdigest()[:8], 16)
        base = 500 + (h % 9500)
        disc = 5 + (h % 40)
        price = round(base * (1 - disc / 100), 2)
        out.append({"store": s, "title": q, "price": price, "mrp": float(base),
                    "discount_pct": disc, "url": f"https://{s}.com/s?q={q}"})
    return sorted(out, key=lambda r: r["price"])


def brain_search(q: str) -> tuple[list[dict[str, Any]], str]:
    prompt = f"Compare prices for '{q}' on {','.join(STORES)}. Reply ONLY JSON array of {{store,title,price,mrp,discount_pct,url}}."
    try:
        r = requests.post(BRAIN_URL, json={"model": MODEL, "messages": [
            {"role": "user", "content": prompt}], "max_tokens": 800, "temperature": 0.2}, timeout=25)
        if r.status_code != 200:
            return fallback_prices(q), "fallback"
        txt = r.json()["choices"][0]["message"]["content"]
        m = re.search(r"\[.*\]", txt, re.S)
        data = json.loads(m.group(0) if m else txt)
        rows = [d for d in data if isinstance(d, dict) and "store" in d and "price" in d]
        if not rows:
            return fallback_prices(q), "fallback"
        return rows, "live"
    except Exception:
        return fallback_prices(q), "fallback"





@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "vgas-v3", "ts": int(time.time())}


@app.get("/api/search")
def search(q: str = Query(min_length=1, max_length=200)) -> dict[str, Any]:
    results, source = brain_search(q)
    return {"query": q, "source": source, "model": MODEL, "results": results}


@app.post("/api/deals/alert")
def add_alert(a: AlertIn) -> dict[str, Any]:
    AID[0] += 1
    row = {"id": AID[0], "query": a.query, "target_price": a.target_price,
           "contact": a.contact, "ts": int(time.time())}
    ALERTS.append(row)
    return row


@app.get("/api/deals")
def deals() -> dict[str, Any]:
    return {"alerts": ALERTS, "count": len(ALERTS)}


@app.post("/api/cart")
def add_cart(c: CartIn) -> dict[str, Any]:
    CID[0] += 1
    row = {"id": CID[0], "store": c.store, "title": c.title, "price": c.price, "qty": c.qty}
    CART.append(row)
    return row


@app.get("/api/cart")
def cart() -> dict[str, Any]:
    total = round(sum(i["price"] * i["qty"] for i in CART), 2)
    return {"items": CART, "total": total, "count": len(CART)}


@app.get("/api/revenue/stats")
def revenue() -> dict[str, Any]:
    gmv = round(sum(i["price"] * i["qty"] for i in CART), 2)
    by_store: dict[str, float] = {}
    for i in CART:
        by_store[i["store"]] = round(by_store.get(i["store"], 0) + i["price"] * i["qty"], 2)
    proj = round(sum(v * COMMISSION.get(k, 0.05) for k, v in by_store.items()), 2)
    return {"gmv": gmv, "affiliate_projection": proj, "by_store": by_store,
            "alerts": len(ALERTS), "commission_rates": COMMISSION}
