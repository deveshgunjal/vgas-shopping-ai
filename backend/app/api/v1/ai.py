"""
AI API endpoints for VGAS Shopping AI
AI chat, product recommendations, smart analysis
"""

from fastapi import APIRouter, Query, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.core.config import settings
from app.core.redis_cache import get_cache, set_cache, CacheKeys
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/ai", tags=["AI"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(default=None, description="Chat session ID")
    context: Optional[Dict] = Field(default=None, description="Additional context")


class RecommendRequest(BaseModel):
    query: str = Field(..., description="What the user is looking for")
    budget: Optional[float] = Field(default=None, description="Max budget")
    category: Optional[str] = Field(default=None, description="Product category")
    country: str = Field(default="India")
    count: int = Field(default=5, ge=1, le=20)


async def _handle_ai_chat(request: ChatRequest):
    """Internal AI chat handler - shared by /chat and /chat/send"""
    vgas_logger.info(f"AI chat: {request.message[:50]}...")

    # Get session history
    session_id = request.session_id or "default"
    cache_key = CacheKeys.AI_CHAT_SESSION.format(session_id)
    history = await get_cache(cache_key) or []

    # Add user message
    history.append({"role": "user", "content": request.message})

    # Generate AI response
    response = _generate_ai_response(request.message, history)

    # Update history
    history.append({"role": "assistant", "content": response["reply"]})
    if len(history) > 20:
        history = history[-20:]

    # Cache session
    await set_cache(cache_key, history, expire_seconds=3600)

    return {
        "reply": response["reply"],
        "session_id": session_id,
        "suggestions": response.get("suggestions", []),
        "products": response.get("products", []),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/chat")
async def ai_chat(request: ChatRequest = Body(...)):
    """AI shopping assistant chat"""
    try:
        return await _handle_ai_chat(request)
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/send")
async def ai_chat_send(
    request: ChatRequest = Body(...),
    language: str = Query(default="english", description="Response language"),
):
    """AI shopping assistant chat - web frontend compatible endpoint (/chat/send)"""
    try:
        result = await _handle_ai_chat(request)
        result["language"] = language
        return result
    except Exception as e:
        logger.error(f"AI chat send error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def get_recommendations(request: RecommendRequest = Body(...)):
    """Get AI-powered product recommendations"""
    try:
        vgas_logger.info(f"AI recommend: {request.query}")

        from app.scrapers.search_engine import ProductSearchEngine

        # Search for products
        search_result = await ProductSearchEngine.search(
            query=request.query,
            country=request.country,
            limit=request.count * 2,
            sort_by="price_asc",
            max_price=request.budget,
        )

        # Filter and rank
        recommendations = []
        for r in search_result.results[: request.count]:
            score = _calculate_recommendation_score(r, request)
            recommendations.append(
                {
                    "name": r.name,
                    "price": r.price,
                    "currency": r.currency,
                    "store": r.store,
                    "url": r.url,
                    "affiliate_url": r.affiliate_url,
                    "image": r.image,
                    "rating": r.rating,
                    "discount_percentage": r.discount_percentage,
                    "recommendation_score": score,
                    "why": _get_recommendation_reason(r, request),
                }
            )

        # Sort by score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

        return {
            "query": request.query,
            "recommendations": recommendations[: request.count],
            "total": len(recommendations),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"AI recommend error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_product(
    url: str = Body(..., embed=True, description="Product URL"),
):
    """AI analysis of a product - worth buying or not"""
    try:
        vgas_logger.info(f"AI analyze: {url}")

        # Get product data
        from app.scrapers import get_scraper
        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        scraper = get_scraper(domain)

        if not scraper:
            raise HTTPException(status_code=400, detail=f"No scraper for {domain}")

        product = await scraper.extract_product_from_url(url)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # AI Analysis
        analysis = {
            "product_name": product.get("name", "Unknown"),
            "price": product.get("current_price", 0),
            "original_price": product.get("original_price", 0),
            "discount": product.get("discount_percentage", 0),
            "rating": product.get("rating", 0),
            "rating_count": product.get("rating_count", 0),
            "verdict": _get_verdict(product),
            "pros": _get_pros(product),
            "cons": _get_cons(product),
            "should_buy": _should_buy(product),
            "confidence": _get_confidence(product),
            "price_advice": _get_price_advice(product),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/faq")
async def get_faq(query: str = Query(..., min_length=2, description="Question")):
    """Get AI answer to shopping FAQs"""
    try:
        cache_key = f"faq:{query.lower()}"
        cached = await get_cache(cache_key)
        if cached:
            return cached

        answer = _answer_faq(query)

        result = {
            "question": query,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await set_cache(cache_key, result, expire_seconds=3600)
        return result

    except Exception as e:
        logger.error(f"FAQ error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- AI Helper Functions ---


def _generate_ai_response(message: str, history: List[Dict]) -> Dict:
    """Generate AI response based on message"""
    msg = message.lower()

    # Greeting
    if any(g in msg for g in ["hi", "hello", "hey", "namaste", "नमस्ते"]):
        return {
            "reply": "👋 Hello! I'm VGAS AI Shopping Assistant. I can help you:\n\n"
            "🔍 Search products across all stores\n"
            "💰 Find best deals and discounts\n"
            "📊 Compare products side-by-side\n"
            "🤖 Analyze if a product is worth buying\n"
            "💡 Get personalized recommendations\n\n"
            "What are you looking for today?",
            "suggestions": [
                "Search for iPhone 15",
                "Best laptops under 50000",
                "Compare Samsung vs iPhone",
                "Show me loot deals",
            ],
        }

    # Search intent
    if any(
        w in msg for w in ["search", "find", "look for", "looking for", "want", "need"]
    ):
        query = (
            message.replace("search for", "")
            .replace("find", "")
            .replace("looking for", "")
            .strip()
        )
        return {
            "reply": f"🔍 Let me search for '{query}' across all stores...",
            "suggestions": [f"Search: {query}"],
        }

    # Deal intent
    if any(w in msg for w in ["deal", "offer", "discount", "sale", "loot"]):
        return {
            "reply": "🔥 Here are the best deals I found! Check the /search/loot-deals endpoint for 80-90% discounts.",
            "suggestions": [
                "Show loot deals",
                "Best discounts today",
                "Clearance sale items",
            ],
        }

    # Compare intent
    if any(w in msg for w in ["compare", "vs", "versus", "difference"]):
        return {
            "reply": "📊 I can compare products for you! Use the /compare endpoint with product URLs.",
            "suggestions": [
                "Compare iPhone vs Samsung",
                "Compare laptops",
                "Compare headphones",
            ],
        }

    # Default
    return {
        "reply": f"I understand you're asking about '{message}'. "
        "I can help with product search, comparison, deals, and recommendations. "
        "Try asking me to search for a specific product!",
        "suggestions": [
            "Search for a product",
            "Show best deals",
            "Compare products",
            "Get recommendations",
        ],
    }


def _calculate_recommendation_score(product, request) -> float:
    """Calculate recommendation score (0-100)"""
    score = 50  # Base score

    # Rating bonus
    if product.rating >= 4.5:
        score += 20
    elif product.rating >= 4.0:
        score += 10
    elif product.rating < 3.0:
        score -= 20

    # Discount bonus
    if product.discount_percentage >= 50:
        score += 15
    elif product.discount_percentage >= 30:
        score += 10

    # Price within budget
    if request.budget and product.price <= request.budget:
        score += 15
    elif request.budget and product.price > request.budget:
        score -= 30

    # Review count bonus
    if product.rating_count >= 1000:
        score += 10
    elif product.rating_count >= 100:
        score += 5

    return max(0, min(100, score))


def _get_recommendation_reason(product, request) -> str:
    """Get human-readable recommendation reason"""
    reasons = []

    if product.rating >= 4.5:
        reasons.append("⭐ Excellent rating")
    if product.discount_percentage >= 50:
        reasons.append(f"🔥 {product.discount_percentage}% off")
    if request.budget and product.price <= request.budget:
        reasons.append("💰 Within budget")
    if product.rating_count >= 1000:
        reasons.append(f"📝 {product.rating_count}+ reviews")

    return ", ".join(reasons) if reasons else "Good value for money"


def _get_verdict(product: Dict) -> str:
    """Get AI verdict on product"""
    price = product.get("current_price", 0)
    original = product.get("original_price", 0)
    rating = product.get("rating", 0)
    discount = product.get("discount_percentage", 0)

    if rating >= 4.5 and discount >= 30:
        return "🟢 EXCELLENT DEAL - Buy now!"
    elif rating >= 4.0 and discount >= 20:
        return "🟢 GOOD DEAL - Worth buying"
    elif rating >= 4.0:
        return "🟡 FAIR - Good product, wait for better discount"
    elif discount >= 50:
        return "🟡 CHECK - High discount but verify quality"
    else:
        return "🔴 NOT RECOMMENDED - Look for better options"


def _get_pros(product: Dict) -> List[str]:
    """Get product pros"""
    pros = []
    if product.get("discount_percentage", 0) >= 30:
        pros.append(f"Good discount: {product['discount_percentage']}% off")
    if product.get("rating", 0) >= 4.0:
        pros.append(f"High rating: {product['rating']} stars")
    if product.get("rating_count", 0) >= 500:
        pros.append(f"Many reviews: {product['rating_count']}+")
    if product.get("shipping_cost", 0) == 0:
        pros.append("Free shipping")
    if product.get("is_in_stock", True):
        pros.append("In stock")
    return pros if pros else ["Available on trusted platform"]


def _get_cons(product: Dict) -> List[str]:
    """Get product cons"""
    cons = []
    if product.get("rating", 0) < 3.5:
        cons.append(f"Low rating: {product['rating']} stars")
    if product.get("discount_percentage", 0) < 10:
        cons.append("Minimal discount")
    if product.get("shipping_cost", 0) > 0:
        cons.append(f"Shipping cost: ₹{product['shipping_cost']}")
    if not product.get("is_in_stock", True):
        cons.append("Out of stock")
    return cons if cons else ["No major concerns"]


def _should_buy(product: Dict) -> bool:
    """Should the user buy this product?"""
    return (
        product.get("rating", 0) >= 4.0
        and product.get("discount_percentage", 0) >= 20
        and product.get("is_in_stock", True)
    )


def _get_confidence(product: Dict) -> float:
    """Get confidence level (0-1)"""
    confidence = 0.5
    if product.get("rating_count", 0) >= 1000:
        confidence += 0.3
    elif product.get("rating_count", 0) >= 100:
        confidence += 0.2
    if product.get("rating", 0) >= 4.5:
        confidence += 0.2
    return min(1.0, confidence)


def _get_price_advice(product: Dict) -> str:
    """Get price advice"""
    discount = product.get("discount_percentage", 0)
    if discount >= 50:
        return "Great price! This is a good time to buy."
    elif discount >= 30:
        return "Good discount. Consider buying if you need it."
    elif discount >= 10:
        return "Small discount. You might want to wait for a better deal."
    else:
        return "No significant discount. Wait for sales or check other stores."


def _answer_faq(query: str) -> str:
    """Answer shopping FAQs"""
    q = query.lower()

    faqs = {
        "best time to buy": "The best times to buy are during festival sales (Diwali, Eid), end-of-season clearance, and major sale events like Amazon Great Indian Festival and Flipkart Big Billion Days.",
        "fake discount": "To detect fake discounts, check if the 'original price' was the actual selling price. VGAS AI checks price history to identify inflated MRP.",
        "return policy": "Most stores offer 7-30 day return policies. Amazon and Flipkart have easy returns. Always check the specific product return policy before buying.",
        "warranty": "Electronics typically come with 1-year manufacturer warranty. Extended warranties are available but often overpriced. Check if your credit card offers warranty coverage.",
        "emi": "No-cost EMI is available on most platforms for orders above ₹3,000. Compare the actual interest rate as 'no-cost' EMIs sometimes have hidden fees.",
    }

    for key, answer in faqs.items():
        if key in q:
            return answer

    return f"I can help with shopping questions about deals, discounts, return policies, warranties, and more. Try asking about 'best time to buy' or 'fake discounts'."
