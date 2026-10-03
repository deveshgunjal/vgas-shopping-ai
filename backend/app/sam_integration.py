"""
SAM-VGAS Shopping AI Integration Module
Integrates SAM Core (Swarm Intelligence, Dev Engine, Memory Vault) with VGAS Shopping AI
Developed by: Vikas Gunjal (VGAS - Vikas Gunjal Advance System)
"""

from __future__ import annotations

import json
import asyncio
import logging
import httpx
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sam_core.events import EventLog
from sam_core.army_pipeline import ArmyPipeline
from sam_core.process_manager import ProcessManager
from sam_core.policy import ActionKind, ActionRequest, PermissionPolicy

logger = logging.getLogger(__name__)

# Paths
SAM_ROOT = Path(__file__).parent.parent.parent  # D:\Sam
VGAS_ROOT = SAM_ROOT / "Vgas Shooping Ai"
SAM_CORE_ROOT = SAM_ROOT / "sam_core"
MEMORY_VAULT = SAM_ROOT / "memory_vault"


class SAMVgasIntegrator:
    """Integrates SAM Core with VGAS Shopping AI"""

    def __init__(self):
        self.sam_root = SAM_ROOT
        self.vgas_root = VGAS_ROOT
        self.event_log = EventLog(SAM_ROOT / "sam_vgas_events.jsonl")
        self.army_pipeline = ArmyPipeline(SAM_CORE_ROOT)
        self.process_manager = ProcessManager(SAM_CORE_ROOT)
        self.policy = PermissionPolicy()

        # SAM-VGAS Brain - Knowledge Base
        self.brain = {
            "version": "1.0.0",
            "created": datetime.now(timezone.utc).isoformat(),
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
            "knowledge_sources": [
                "github_trending",
                "affiliate_networks",
                "price_history",
                "user_behavior",
            ],
        }

        self.event_log.write(
            "sam_vgas_init",
            "integration",
            "SAM-VGAS Integration initialized",
            **self.brain,
        )

    async def run_vgas_task(self, task_id: str, goal: str, domain: str = "shopping") -> Dict[str, Any]:
        """Run a VGAS task through SAM Army Pipeline"""
        payload = {
            "goal": goal,
            "domain": domain,
            "permit": "vgas-integration",
        }
        result = self.army_pipeline.run(task_id, payload)
        self.event_log.write(
            "vgas_task_complete",
            task_id,
            f"Task '{goal}' completed",
            **result,
        )
        return result

    async def fetch_github_trending(self, topic: str = "affiliate-marketing") -> List[Dict[str, Any]]:
        """Fetch trending GitHub repos for latest tech info"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"https://api.github.com/search/repositories",
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
                    self.event_log.write(
                        "github_fetch",
                        "knowledge",
                        f"Fetched {len(repos)} trending repos for {topic}",
                        repos_count=len(repos),
                    )
                    return repos
        except Exception as e:
            logger.warning(f"GitHub fetch failed: {e}")
        return []

    async def update_sam_brain(self) -> Dict[str, Any]:
        """Update SAM brain with latest knowledge from internet"""
        updates = {}

        # Fetch GitHub trending repos
        trending = await self.fetch_github_trending("affiliate-marketing")
        updates["github_trending"] = trending

        # Fetch latest shopping tech
        shopping_tech = await self.fetch_github_trending("price-comparison")
        updates["shopping_tech"] = shopping_tech

        # Save to memory vault
        vault_path = MEMORY_VAULT / "sam_vgas_knowledge.json"
        if MEMORY_VAULT.exists():
            vault_data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "knowledge": updates,
            }
            vault_path.write_text(
                json.dumps(vault_data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self.event_log.write(
                "brain_update",
                "knowledge",
                "SAM brain updated with latest knowledge",
                vault_path=str(vault_path),
            )

        return updates

    async def get_vgas_status(self) -> Dict[str, Any]:
        """Get complete VGAS system status"""
        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sam_vgas_integration": {
                "version": self.brain["version"],
                "capabilities": self.brain["capabilities"],
            },
            "processes": self.process_manager.get_process_status(),
            "recent_events": self.event_log.recent(10),
        }
        return status

    async def start_vgas_services(self) -> Dict[str, Any]:
        """Start all VGAS services"""
        results = {}

        # Check if backend is running
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8000/api/v1/system/info")
                if response.status_code == 200:
                    results["backend"] = "running"
                else:
                    results["backend"] = "error"
        except Exception:
            results["backend"] = "not_running"

        # Check frontend
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:3000")
                if response.status_code == 200:
                    results["frontend"] = "running"
                else:
                    results["frontend"] = "error"
        except Exception:
            results["frontend"] = "not_running"

        self.event_log.write(
            "vgas_status_check",
            "monitoring",
            "VGAS services status checked",
            **results,
        )
        return results


# Singleton instance
sam_vgas = SAMVgasIntegrator()


async def main():
    """Main entry point for SAM-VGAS integration"""
    print("🚀 SAM-VGAS Integration Starting...")

    # Update SAM brain
    print("🧠 Updating SAM brain with latest knowledge...")
    updates = await sam_vgas.update_sam_brain()
    print(f"✅ Brain updated: {len(updates)} knowledge sources")

    # Check VGAS status
    print("📊 Checking VGAS status...")
    status = await sam_vgas.get_vgas_status()
    print(f"✅ VGAS Status: {json.dumps(status, indent=2)}")

    # Run a test task
    print("🎯 Running test task...")
    result = await sam_vgas.run_vgas_task(
        task_id="test-001",
        goal="Search for iPhone 15 across all stores",
        domain="shopping",
    )
    print(f"✅ Task result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())