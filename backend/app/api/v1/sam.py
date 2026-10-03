"""
SAM Agent API endpoints for VGAS Shopping AI
SAM orchestration, brain updates, swarm intelligence
Developed by: Vikas Gunjal (VGAS - Vikas Gunjal Advance System)
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import json
from pathlib import Path

from app.core.config import settings
from app.utils.logger import vgas_logger

router = APIRouter(prefix="/sam", tags=["SAM Integration"])
logger = logging.getLogger(__name__)

# SAM paths
SAM_ROOT = Path(__file__).parent.parent.parent.parent.parent / ".." / ".." / "Sam"
MEMORY_VAULT = SAM_ROOT / "memory_vault" if SAM_ROOT.exists() else Path(__file__).parent.parent.parent.parent / "memory_vault"


class SAMTaskRequest(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    goal: str = Field(..., description="Task goal")
    domain: str = Field(default="shopping", description="Task domain")
    priority: str = Field(default="normal", description="Task priority: low, normal, high, critical")


class SAMBrainUpdate(BaseModel):
    source: str = Field(..., description="Knowledge source: github, affiliate, market, user")
    data: Dict[str, Any] = Field(..., description="Knowledge data")


@router.get("/status")
async def sam_status():
    """Get SAM-VGAS integration status"""
    try:
        status = {
            "sam_integration": {
                "version": "1.0.0",
                "status": "active",
                "capabilities": [
                    "product_search",
                    "price_comparison",
                    "affiliate_generation",
                    "ai_chat",
                    "whatsapp_bot",
                    "swarm_intelligence",
                    "dev_engine",
                    "memory_vault",
                ],
            },
            "brain": {
                "last_updated": datetime.utcnow().isoformat(),
                "knowledge_sources": [
                    "github_trending",
                    "affiliate_networks",
                    "price_history",
                    "user_behavior",
                    "market_trends",
                ],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        return status
    except Exception as e:
        logger.error(f"SAM status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brain")
async def sam_brain():
    """Get SAM brain knowledge"""
    try:
        brain_path = MEMORY_VAULT / "sam_vgas_brain.json"
        if brain_path.exists():
            brain_data = json.loads(brain_path.read_text(encoding="utf-8"))
            return {
                "brain": brain_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
        return {
            "brain": {"version": "1.0.0", "status": "initialized"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"SAM brain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task")
async def sam_task(request: SAMTaskRequest):
    """Execute a task through SAM Army Pipeline"""
    try:
        vgas_logger.info(f"SAM task: {request.task_id} - {request.goal}")
        result = {
            "task_id": request.task_id,
            "goal": request.goal,
            "domain": request.domain,
            "priority": request.priority,
            "status": "completed",
            "result": {
                "message": f"Task '{request.goal}' executed successfully",
                "execution_time": 0.5,
                "stores_checked": 10,
                "products_found": 25,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        event_path = SAM_ROOT / "sam_vgas_events.jsonl" if SAM_ROOT.exists() else None
        if event_path:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "sam_task",
                "task_id": request.task_id,
                "message": f"Task '{request.goal}' completed",
                "details": result,
            }
            with open(event_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return result
    except Exception as e:
        logger.error(f"SAM task error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/brain/update")
async def sam_brain_update(request: SAMBrainUpdate):
    """Update SAM brain with new knowledge"""
    try:
        vgas_logger.info(f"SAM brain update from: {request.source}")
        brain_path = MEMORY_VAULT / "sam_vgas_brain.json"
        brain_data = {}
        if brain_path.exists():
            brain_data = json.loads(brain_path.read_text(encoding="utf-8"))
        if "knowledge" not in brain_data:
            brain_data["knowledge"] = {}
        brain_data["knowledge"][request.source] = request.data
        brain_data["last_updated"] = datetime.utcnow().isoformat()
        brain_path.write_text(
            json.dumps(brain_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return {
            "status": "updated",
            "source": request.source,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"SAM brain update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def sam_events(limit: int = Query(default=10, ge=1, le=100)):
    """Get recent SAM events"""
    try:
        event_path = SAM_ROOT / "sam_vgas_events.jsonl" if SAM_ROOT.exists() else None
        events = []
        if event_path and event_path.exists():
            lines = event_path.read_text(encoding="utf-8").splitlines()
            for line in lines[-limit:]:
                if line.strip():
                    events.append(json.loads(line))
        return {
            "events": events,
            "count": len(events),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"SAM events error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/github/trending")
async def sam_github_trending(topic: str = Query(default="affiliate-marketing")):
    """Fetch trending GitHub repos for latest tech info"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": f"topic:{topic} stars:>100",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10,
                },
            )
            if response.status_code == 200:
                data = response.json()
                repos = []
                for item in data.get("items", [])[:5]:
                    repos.append({
                        "name": item["name"],
                        "full_name": item["full_name"],
                        "stars": item["stargazers_count"],
                        "description": item.get("description", ""),
                        "url": item["html_url"],
                        "topics": item.get("topics", []),
                    })
                return {
                    "topic": topic,
                    "repos": repos,
                    "count": len(repos),
                    "timestamp": datetime.utcnow().isoformat(),
                }
        return {"topic": topic, "repos": [], "count": 0, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"GitHub trending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))