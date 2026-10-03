"""
🔱 AI Engine Hub API - Zero Dependency - Universal King Mode 🔱
API endpoints for all 6 AI Inference Engines and Swarm Nodes
No pip install needed. Pure Python + Direct HTTP APIs.

DESIGNED AND CREATED BY: Vikas Gunjal (THE ONLY MASTER)
SAM is DIFFERENT - Always 100x ahead from all existing AI systems FOREVER!
"""

from __future__ import annotations

from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any

from ...ai_engine_hub import ai_engine_hub

router = APIRouter(prefix="/ai-engines", tags=["AI Engine Hub - Zero Dependency"])


@router.get("/", summary="Get all AI engines")
async def get_all_engines():
    """Get all registered AI inference engines with full details - ZERO DEPENDENCY"""
    return ai_engine_hub.get_all_engines()


@router.get("/recommend", summary="Recommend best engine for use case")
async def recommend_engine(use_case: str = Query("general", description="Describe your use case")):
    """Recommend the best AI engine for a specific use case"""
    return ai_engine_hub.recommend_engine(use_case)


@router.get("/marathi", summary="Get Marathi info about AI engines")
async def get_marathi_info(engine_type: Optional[str] = Query(None, description="Specific engine type")):
    """Get Marathi information about AI engines"""
    return ai_engine_hub.get_marathi_info(engine_type)


@router.get("/comparison", summary="Get engine comparison")
async def get_comparison():
    """Get detailed comparison of all AI engines"""
    return ai_engine_hub.get_engine_comparison()


@router.get("/swarm", summary="Get all swarm nodes")
async def get_swarm_nodes():
    """Get all swarm nodes status"""
    return ai_engine_hub.get_swarm_nodes()


@router.get("/swarm/{node_id}", summary="Get specific swarm node")
async def get_node(node_id: str):
    """Get specific swarm node status"""
    return ai_engine_hub.get_node(node_id)


@router.post("/swarm/deliver", summary="Deliver to swarm nodes")
async def deliver_to_swarm(payload: Dict[str, Any] = Body(default={}, description="Task payload to deliver")):
    """Deliver task/model/update to all swarm nodes"""
    return ai_engine_hub.deliver_to_swarm(payload)


@router.get("/protection", summary="Get SAM Brain protection status")
async def get_protection_status():
    """🔒 Get SAM Brain protection status - Only Master can modify"""
    return ai_engine_hub.get_protection_status()


@router.post("/protection/verify", summary="Verify Master authentication")
async def verify_master_auth(auth_data: Dict[str, str] = Body(default={}, description="Auth token data")):
    """🔒 Verify Master authentication"""
    token = auth_data.get("token", "")
    is_valid = ai_engine_hub.verify_master_auth(token)
    return {"authenticated": is_valid, "master_id": "vikas_gunjal" if is_valid else None, "timestamp": ai_engine_hub.get_protection_status()["timestamp"]}


@router.post("/call/huggingface", summary="Call Hugging Face API directly")
async def call_huggingface(
    model: str = Query("gpt2", description="Hugging Face model ID"),
    prompt: str = Query("Hello", description="Input prompt"),
    hf_token: Optional[str] = Query(None, description="Hugging Face API token"),
    max_tokens: int = Query(1024, description="Max tokens to generate")
):
    """Call Hugging Face Inference API directly - No pip install needed!"""
    result = ai_engine_hub.call_huggingface(model=model, prompt=prompt, hf_token=hf_token, max_tokens=max_tokens)
    return {"engine": result.engine, "model": result.model, "response": result.response, "tokens_used": result.tokens_used, "latency_ms": result.latency_ms, "timestamp": result.timestamp}


@router.post("/call/openai-compatible", summary="Call OpenAI-compatible API")
async def call_openai_compatible(
    base_url: str = Query("http://localhost:8000", description="API base URL (vLLM, TGI, LLaMA.cpp, OpenAI)"),
    model: str = Query("gpt2", description="Model name"),
    prompt: str = Query("Hello", description="Input prompt"),
    api_key: Optional[str] = Query(None, description="API key"),
    max_tokens: int = Query(1024, description="Max tokens to generate")
):
    """Call any OpenAI-compatible API - No pip install needed!"""
    result = ai_engine_hub.call_openai_compatible(base_url=base_url, model=model, prompt=prompt, api_key=api_key, max_tokens=max_tokens)
    return {"engine": result.engine, "model": result.model, "response": result.response, "tokens_used": result.tokens_used, "latency_ms": result.latency_ms, "timestamp": result.timestamp}


@router.post("/call/any-rest", summary="Call any REST API")
async def call_any_rest_api(
    url: str = Query("http://example.com", description="API endpoint URL"),
    payload: Dict[str, Any] = Body(default={}, description="Request payload"),
    headers: Optional[Dict[str, str]] = Body(None, description="Optional headers")
):
    """Call ANY REST API - Universal compatibility!"""
    return ai_engine_hub.call_any_rest_api(url=url, payload=payload, headers=headers)


@router.get("/{engine_type}", summary="Get specific AI engine details")
async def get_engine(engine_type: str):
    """Get details of a specific AI engine"""
    return ai_engine_hub.get_engine(engine_type)


# ========== PHASE 1: ADVANCED API ENDPOINTS ==========

@router.get("/auto-select", summary="Auto select best engine for task")
async def auto_select_engine(
    task: str = Query("general", description="Task type: code, creative, translate, summarize, classify, chat, math, image, local, fast, quality, best"),
    query: str = Query("", description="Additional query context"),
    priority: str = Query("balanced", description="Priority: speed, quality, cost, balanced, local")
):
    """🤖 Smart Auto Engine Selection based on task type and priority"""
    return ai_engine_hub.auto_select_engine(task=task, query=query, priority=priority)


@router.get("/health", summary="Get engine health status")
async def health_check(engine_type: Optional[str] = Query(None, description="Specific engine type or all")):
    """🏥 Real-time Health Monitor for all engines or specific engine"""
    return ai_engine_hub.health_check(engine_type=engine_type)


@router.post("/parallel", summary="Multi-engine parallel call")
async def parallel_call(
    prompt: str = Body(default="", embed=True, description="Input prompt"),
    engines: Optional[list] = Body(default=None, description="List of engine types to call"),
    max_wait_ms: float = Body(default=30000.0, description="Max wait time in milliseconds")
):
    """⚡ Multi-Engine Parallel Call - Pick the best response"""
    return ai_engine_hub.parallel_call(prompt=prompt, engines=engines, max_wait_ms=max_wait_ms)


@router.get("/cache/stats", summary="Get cache statistics")
async def get_cache_stats():
    """📊 Get cache statistics"""
    return ai_engine_hub.get_cache_stats()


@router.post("/cache/clear", summary="Clear response cache")
async def clear_cache():
    """🧹 Clear all cached responses"""
    return ai_engine_hub.clear_cache()


@router.get("/stats", summary="Get performance statistics")
async def get_performance_stats():
    """📈 Get comprehensive performance statistics"""
    return ai_engine_hub.get_performance_stats()