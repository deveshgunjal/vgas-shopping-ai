"""
🔱 ZERO-DEPENDENCY AI ENGINE HUB - Universal King Mode 🔱

Master: Vikas Gunjal (VGAS - Vikas Gunjal Advance System)
Mode: UNIVERSAL KING - ALL POWER UNLOCKED

ZERO DEPENDENCIES - Pure Python Standard Library Only
No pip install needed. No heavy packages. Direct API calls only.
Fast, Simple, Forever Independent.

AI Engines Integrated (via direct HTTP APIs):
1. Hugging Face Inference API
2. vLLM Server API
3. TGI Server API
4. LLaMA.cpp Server API
5. OpenAI API
6. Any Generic REST API

No local model loading. No GPU needed. No bloat.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from urllib.request import urlopen, Request, URLError
from urllib.error import HTTPError

logger = logging.getLogger(__name__)

SAM_ROOT = Path(__file__).parent.parent.parent.parent.parent
MEMORY_VAULT = SAM_ROOT / "memory_vault"

# 🔒 SAM Brain Protection - Master Control Only
MASTER_ID = "vikas_gunjal"
MASTER_AUTH_TOKEN = "UNIVERSAL_KING_2026"
BRAIN_LOCK = True


@dataclass
class AIEngine:
    name: str
    engine_type: str
    api_endpoint: str
    status: str
    capabilities: List[str]
    model_types: List[str]
    description: str
    marathi_info: str
    setup_guide: str
    recommended_for: str
    is_zero_dep: bool


@dataclass
class SwarmNode:
    node_id: str
    name: str
    engine_type: str
    status: str
    api_endpoint: str
    models_available: List[str]
    tasks_active: int
    requests_per_minute: int
    last_heartbeat: str


@dataclass
class InferenceResult:
    engine: str
    model: str
    response: str
    tokens_used: int
    latency_ms: float
    timestamp: str


@dataclass
class HealthStatus:
    engine_type: str
    status: str  # healthy, degraded, down
    latency_ms: float
    last_check: str
    uptime_percent: float
    requests_total: int
    requests_failed: int
    avg_response_time_ms: float


@dataclass
class PerformanceStats:
    total_requests: int
    total_cache_hits: int
    total_cache_misses: int
    avg_latency_ms: float
    fastest_engine: str
    slowest_engine: str
    most_used_engine: str
    uptime: str


class UltimateAIEngineHub:
    """🔱 ZERO-DEPENDENCY AI ENGINE HUB - Universal King Mode 🔱"""

    def verify_master_auth(self, token: str) -> bool:
        """🔒 SAM Brain Protection - Only Master can modify"""
        return token == MASTER_AUTH_TOKEN
    
    def get_protection_status(self) -> Dict[str, Any]:
        """🔒 Get SAM Brain protection status"""
        return {"brain_locked": BRAIN_LOCK, "master_id": MASTER_ID, "protection_active": True, "only_master_can_modify": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ========== PHASE 1: ADVANCED FEATURES ==========
    
    def __init__(self):
        self.sam_root = SAM_ROOT
        self.memory_vault = MEMORY_VAULT
        self.engines: Dict[str, AIEngine] = {}
        self.swarm_nodes: Dict[str, SwarmNode] = {}
        # Advanced features data
        self._cache: Dict[str, Dict[str, Any]] = {}  # In-memory cache
        self._cache_max_size = 1000  # Max cache entries
        self._health_stats: Dict[str, Dict[str, Any]] = {}  # Health tracking
        self._perf_stats: Dict[str, Dict[str, Any]] = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "latencies": {},  # engine_type -> [latencies]
            "requests_per_engine": {},  # engine_type -> count
            "start_time": datetime.now(timezone.utc).isoformat()
        }
        self._register_all_engines()
        self._initialize_swarm_nodes()
        self._init_health_stats()
        logger.info("🔱 ZERO-DEPENDENCY AI ENGINE HUB initialized with ADVANCED FEATURES!")
    
    def _init_health_stats(self):
        """Initialize health stats for all engines"""
        for engine_type in self.engines:
            self._health_stats[engine_type] = {
                "status": "healthy",
                "latency_ms": 0.0,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "uptime_percent": 100.0,
                "requests_total": 0,
                "requests_failed": 0,
                "avg_response_time_ms": 0.0,
                "consecutive_failures": 0
            }

    def _register_all_engines(self):
        self.engines["transformers"] = AIEngine(
            name="Hugging Face Inference API",
            engine_type="transformers",
            api_endpoint="https://api-inference.huggingface.co/models/",
            status="available",
            capabilities=["text_generation", "text_classification", "question_answering", "summarization", "translation", "zero_shot"],
            model_types=["text", "vision", "audio"],
            description="Direct API access to 1000+ free AI models on Hugging Face. No install needed.",
            marathi_info="है AI विश्वातील सर्वात महतत्वachi आणि मोफत ओपन-सोर्स Python लायब्ररी आह.",
            setup_guide="1. Get free token from huggingface.co\n2. Set HF_TOKEN env var\n3. Call API directly!",
            recommended_for="General AI tasks, all model types",
            is_zero_dep=True
        )
        self.engines["vllm"] = AIEngine(
            name="vLLM API Server",
            engine_type="vllm",
            api_endpoint="http://localhost:8000/v1/",
            status="available",
            capabilities=["high_throughput", "paged_attention", "fast_generation", "openai_compatible"],
            model_types=["text", "code"],
            description="Connect to vLLM server via OpenAI-compatible API. Ultra-fast with PagedAttention.",
            marathi_info="हे अतिशय वेगाने AI मॉडेल्स चालवणारे टूल आह. PagedAttention तंत्रज्ञान वापरले जाते.",
            setup_guide="1. Run: vllm serve model_name\n2. Connect via API\n3. No client install needed!",
            recommended_for="Production chatbots, high-throughput serving",
            is_zero_dep=True
        )
        self.engines["tgi"] = AIEngine(
            name="TGI API Server",
            engine_type="tgi",
            api_endpoint="http://localhost:3000/",
            status="available",
            capabilities=["production_scaling", "token_streaming", "stable", "openai_compatible"],
            model_types=["text", "code"],
            description="Connect to TGI server for production-scale inference. Ultra-stable.",
            marathi_info="Hugging Face चे प्रोडक्शन स्केल इंजिन. अतिशय सुरक्षित आणि स्थिर.",
            setup_guide="1. Run TGI server\n2. Connect via REST API\n3. No client install needed!",
            recommended_for="Enterprise AI APIs, production deployment",
            is_zero_dep=True
        )
        self.engines["llama_cpp"] = AIEngine(
            name="LLaMA.cpp API Server",
            engine_type="llama_cpp",
            api_endpoint="http://localhost:8080/",
            status="available",
            capabilities=["cpu_inference", "quantization", "low_memory", "offline", "openai_compatible"],
            model_types=["text", "code"],
            description="Connect to LLaMA.cpp server for lightweight CPU inference. No GPU needed.",
            marathi_info="C/C++ मधली हलकी लायब्ररी, जी GPU शिवाय AI चालवू शकते.",
            setup_guide="1. Run: llama-server -m model.gguf\n2. Connect via API\n3. No client install needed!",
            recommended_for="Local PC/laptop AI, offline use, low-resource devices",
            is_zero_dep=True
        )
        self.engines["openai"] = AIEngine(
            name="OpenAI API",
            engine_type="openai",
            api_endpoint="https://api.openai.com/v1/",
            status="available",
            capabilities=["text_generation", "chat_completion", "embeddings", "image_generation", "audio", "function_calling"],
            model_types=["text", "vision", "audio", "multimodal"],
            description="Direct API access to GPT-4, GPT-3.5, DALL-E, Whisper. Simple REST API calls.",
            marathi_info="OpenAI चे GPT-4, GPT-3.5, DALL-E, Whisper मॉडेल्स. सोपे REST API कॉल्स.",
            setup_guide="1. Get API key from platform.openai.com\n2. Set OPENAI_API_KEY env var\n3. Call API directly!",
            recommended_for="Best quality responses, multimodal AI, production apps",
            is_zero_dep=True
        )
        self.engines["generic"] = AIEngine(
            name="Any REST AI Service",
            engine_type="generic",
            api_endpoint="",
            status="available",
            capabilities=["custom_api", "any_rest_service", "webhook_integration", "json_io"],
            model_types=["text", "code"],
            description="Connect to ANY AI service with a REST API. Universal compatibility.",
            marathi_info="कोणत्याही AI सर्व्हिसशी जोडले जाऊ शकते. युनिव्हर्सल कम्पॅटिबिलिटी.",
            setup_guide="1. Get API endpoint from any AI service\n2. Configure in settings\n3. Call API directly!",
            recommended_for="Custom AI services, third-party integrations, webhooks",
            is_zero_dep=True
        )
        logger.info(f"✅ Registered {len(self.engines)} AI engines - ZERO DEPENDENCY!")

    def _initialize_swarm_nodes(self):
        node_configs = [
            {"node_id": "node-hf-001", "name": "Hugging Face API Node", "engine_type": "transformers", "endpoint": "https://api-inference.huggingface.co", "models": ["meta-llama/Llama-2-7b", "mistralai/Mistral-7B", "bert-base-uncased"]},
            {"node_id": "node-vllm-001", "name": "vLLM Server Node", "engine_type": "vllm", "endpoint": "http://localhost:8000", "models": ["llama-2-13b", "mistral-7b"]},
            {"node_id": "node-tgi-001", "name": "TGI Server Node", "engine_type": "tgi", "endpoint": "http://localhost:3000", "models": ["llama-2-70b", "falcon-40b"]},
            {"node_id": "node-llama-001", "name": "LLaMA.cpp Server Node", "engine_type": "llama_cpp", "endpoint": "http://localhost:8080", "models": ["llama-2-7b-q4", "mistral-7b-q4"]},
            {"node_id": "node-openai-001", "name": "OpenAI API Node", "engine_type": "openai", "endpoint": "https://api.openai.com", "models": ["gpt-4", "gpt-3.5-turbo", "dall-e-3"]},
            {"node_id": "node-generic-001", "name": "Generic REST Node", "engine_type": "generic", "endpoint": "", "models": ["custom"]}
        ]
        for config in node_configs:
            self.swarm_nodes[config["node_id"]] = SwarmNode(
                node_id=config["node_id"], name=config["name"], engine_type=config["engine_type"],
                status="initialized", api_endpoint=config["endpoint"], models_available=config["models"],
                tasks_active=0, requests_per_minute=0, last_heartbeat=datetime.now(timezone.utc).isoformat()
            )
        logger.info(f"✅ Initialized {len(self.swarm_nodes)} swarm nodes - ZERO DEPENDENCY!")

    def _make_api_call(self, url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Dict[str, Any]:
        """Make direct HTTP API call - Pure Python urllib, NO external libraries!"""
        start_time = time.time()
        try:
            data = json.dumps(payload).encode('utf-8')
            req = Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            with urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                latency = (time.time() - start_time) * 1000
                return {"success": True, "data": result, "latency_ms": latency}
        except HTTPError as e:
            latency = (time.time() - start_time) * 1000
            return {"success": False, "error": f"HTTP {e.code}: {e.reason}", "latency_ms": latency}
        except URLError as e:
            latency = (time.time() - start_time) * 1000
            return {"success": False, "error": f"URL Error: {str(e)}", "latency_ms": latency}
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {"success": False, "error": str(e), "latency_ms": latency}

    def call_huggingface(self, model: str, prompt: str, hf_token: Optional[str] = None, max_tokens: int = 1024) -> InferenceResult:
        """Call Hugging Face Inference API directly - No pip install!"""
        url = f"https://api-inference.huggingface.co/models/{model}"
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "return_full_text": False, "temperature": 0.7}}
        headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
        result = self._make_api_call(url, payload, headers)
        response_text = ""
        tokens_used = 0
        if result["success"]:
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                response_text = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                response_text = data.get("generated_text", "")
            tokens_used = len(response_text.split())
        return InferenceResult(engine="transformers", model=model, response=response_text, tokens_used=tokens_used, latency_ms=result.get("latency_ms", 0), timestamp=datetime.now(timezone.utc).isoformat())

    def call_openai_compatible(self, base_url: str, model: str, prompt: str, api_key: Optional[str] = None, max_tokens: int = 1024) -> InferenceResult:
        """Call any OpenAI-compatible API (vLLM, TGI, LLaMA.cpp, OpenAI) - No pip install!"""
        url = f"{base_url}/chat/completions"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        result = self._make_api_call(url, payload, headers)
        response_text = ""
        tokens_used = 0
        if result["success"]:
            data = result["data"]
            if "choices" in data and len(data["choices"]) > 0:
                response_text = data["choices"][0].get("message", {}).get("content", "")
            if "usage" in data:
                tokens_used = data["usage"].get("total_tokens", 0)
        return InferenceResult(engine="openai_compatible", model=model, response=response_text, tokens_used=tokens_used, latency_ms=result.get("latency_ms", 0), timestamp=datetime.now(timezone.utc).isoformat())

    def call_any_rest_api(self, url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Call ANY REST API - Universal compatibility!"""
        return self._make_api_call(url, payload, headers)

    def get_all_engines(self) -> Dict[str, Any]:
        return {"engines": {k: asdict(v) for k, v in self.engines.items()}, "count": len(self.engines), "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}

    def get_engine(self, engine_type: str) -> Optional[Dict[str, Any]]:
        engine = self.engines.get(engine_type)
        return asdict(engine) if engine else None

    def get_swarm_nodes(self) -> Dict[str, Any]:
        return {"nodes": {k: asdict(v) for k, v in self.swarm_nodes.items()}, "count": len(self.swarm_nodes), "timestamp": datetime.now(timezone.utc).isoformat()}

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        node = self.swarm_nodes.get(node_id)
        return asdict(node) if node else None

    def recommend_engine(self, use_case: str) -> Dict[str, Any]:
        use_case_lower = use_case.lower()
        if any(word in use_case_lower for word in ["chatbot", "high", "throughput", "multi-user", "fast"]):
            recommended = self.engines["vllm"]
        elif any(word in use_case_lower for word in ["production", "enterprise", "stable", "scale"]):
            recommended = self.engines["tgi"]
        elif any(word in use_case_lower for word in ["local", "offline", "mobile", "edge", "cpu", "low"]):
            recommended = self.engines["llama_cpp"]
        elif any(word in use_case_lower for word in ["best", "quality", "gpt", "openai"]):
            recommended = self.engines["openai"]
        elif any(word in use_case_lower for word in ["json", "structured", "format", "data", "program"]):
            recommended = self.engines["openai"]
        else:
            recommended = self.engines["transformers"]
        return {"recommended_engine": asdict(recommended), "use_case": use_case, "reason": f"Best match for: {use_case}", "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}

    def get_marathi_info(self, engine_type: Optional[str] = None) -> Dict[str, Any]:
        if engine_type:
            engine = self.engines.get(engine_type)
            if engine:
                return {"engine": engine.name, "marathi_info": engine.marathi_info, "description": engine.description, "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}
        engines_info = []
        for engine_type, engine in self.engines.items():
            engines_info.append({"name": engine.name, "engine_type": engine.engine_type, "marathi_info": engine.marathi_info, "recommended_for": engine.recommended_for, "zero_dep": engine.is_zero_dep})
        return {"engines": engines_info, "count": len(engines_info), "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}

    def deliver_to_swarm(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        delivered_to = []
        failed = []
        for node_id, node in self.swarm_nodes.items():
            try:
                node.tasks_active += 1
                node.last_heartbeat = datetime.now(timezone.utc).isoformat()
                delivered_to.append(node_id)
                logger.info(f"✅ Delivered to {node_id}: {payload.get('action', 'unknown')}")
            except Exception as e:
                failed.append({"node_id": node_id, "error": str(e)})
                logger.error(f"❌ Failed to deliver to {node_id}: {e}")
        return {"delivered_to": delivered_to, "failed": failed, "total_nodes": len(self.swarm_nodes), "payload": payload, "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}

    def get_engine_comparison(self) -> Dict[str, Any]:
        comparison = {"engines": [], "use_cases": {"best_for_speed": "vLLM", "best_for_stability": "TGI", "best_for_local": "LLaMA.cpp", "best_for_quality": "OpenAI", "best_for_free": "Hugging Face", "best_for_flexibility": "Generic REST"}, "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}
        for engine_type, engine in self.engines.items():
            comparison["engines"].append({"name": engine.name, "engine_type": engine.engine_type, "speed_rating": self._get_speed_rating(engine.engine_type), "memory_efficiency": self._get_memory_efficiency(engine.engine_type), "ease_of_use": self._get_ease_of_use(engine.engine_type), "production_ready": self._get_production_ready(engine.engine_type), "capabilities_count": len(engine.capabilities), "zero_dep": engine.is_zero_dep})
        return comparison

    def _get_speed_rating(self, engine_type: str) -> int:
        ratings = {"vllm": 10, "openai": 9, "tgi": 9, "transformers": 7, "llama_cpp": 6, "generic": 8}
        return ratings.get(engine_type, 5)

    def _get_memory_efficiency(self, engine_type: str) -> int:
        ratings = {"llama_cpp": 10, "vllm": 9, "openai": 10, "tgi": 8, "transformers": 8, "generic": 9}
        return ratings.get(engine_type, 5)

    def _get_ease_of_use(self, engine_type: str) -> int:
        ratings = {"openai": 10, "transformers": 9, "generic": 8, "vllm": 7, "tgi": 7, "llama_cpp": 7}
        return ratings.get(engine_type, 5)

    def _get_production_ready(self, engine_type: str) -> bool:
        return engine_type in ["vllm", "tgi", "openai", "transformers", "llama_cpp", "generic"]
    
    # ========== PHASE 1: AUTO ENGINE SELECTION ==========
    
    def auto_select_engine(self, task: str, query: str = "", priority: str = "balanced") -> Dict[str, Any]:
        """🤖 Smart Auto Engine Selection based on task type and priority"""
        task_lower = task.lower()
        
        task_engine_map = {
            "code": ["vllm", "openai", "llama_cpp"],
            "coding": ["vllm", "openai", "llama_cpp"],
            "debug": ["vllm", "openai", "llama_cpp"],
            "python": ["vllm", "openai", "llama_cpp"],
            "creative": ["openai", "transformers", "tgi"],
            "write": ["openai", "transformers", "tgi"],
            "story": ["openai", "transformers", "tgi"],
            "translate": ["transformers", "openai", "tgi"],
            "summarize": ["transformers", "openai", "vllm"],
            "summar": ["transformers", "openai", "vllm"],
            "classify": ["transformers", "vllm", "tgi"],
            "classif": ["transformers", "vllm", "tgi"],
            "analyze": ["openai", "vllm", "transformers"],
            "chat": ["openai", "transformers", "vllm"],
            "question": ["openai", "transformers", "vllm"],
            "qa": ["openai", "transformers", "vllm"],
            "math": ["openai", "vllm", "llama_cpp"],
            "calculate": ["openai", "vllm", "llama_cpp"],
            "image": ["transformers", "generic"],
            "vision": ["transformers", "generic"],
            "local": ["llama_cpp", "transformers", "generic"],
            "private": ["llama_cpp", "transformers", "generic"],
            "free": ["transformers", "llama_cpp", "generic"],
            "fast": ["vllm", "openai", "tgi"],
            "speed": ["vllm", "openai", "tgi"],
            "quality": ["openai", "tgi", "vllm"],
            "best": ["openai", "vllm", "tgi"],
        }
        
        priority_order = {
            "speed": ["vllm", "openai", "tgi", "transformers", "llama_cpp", "generic"],
            "quality": ["openai", "tgi", "vllm", "transformers", "llama_cpp", "generic"],
            "cost": ["transformers", "llama_cpp", "generic", "vllm", "tgi", "openai"],
            "balanced": ["openai", "vllm", "transformers", "tgi", "llama_cpp", "generic"],
            "local": ["llama_cpp", "transformers", "generic", "vllm", "tgi", "openai"],
        }
        
        recommended = list(self.engines.keys())
        for keyword, engines in task_engine_map.items():
            if keyword in task_lower:
                recommended = engines
                break
        
        priority_list = priority_order.get(priority, priority_order["balanced"])
        ordered_engines = [e for e in priority_list if e in recommended]
        if not ordered_engines:
            ordered_engines = [e for e in priority_list if e in self.engines]
        
        best_engine = None
        for engine_type in ordered_engines:
            if engine_type in self.engines:
                health = self._health_stats.get(engine_type, {})
                if health.get("status", "healthy") != "down":
                    best_engine = engine_type
                    break
        
        if not best_engine:
            best_engine = list(self.engines.keys())[0]
        
        selected = self.engines[best_engine]
        self._perf_stats["requests_per_engine"][best_engine] = self._perf_stats["requests_per_engine"].get(best_engine, 0) + 1
        
        return {
            "selected_engine": best_engine,
            "engine_name": selected.name,
            "reason": f"Task: '{task}' matched with '{best_engine}' engine (priority: {priority})",
            "all_candidates": ordered_engines,
            "priority": priority,
            "task": task,
            "zero_dependency": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # ========== PHASE 1: HEALTH MONITOR ==========
    
    def _update_health_stats(self, engine_type: str, latency_ms: float, success: bool):
        """📊 Update health stats after a request"""
        if engine_type not in self._health_stats:
            return
        stats = self._health_stats[engine_type]
        stats["requests_total"] += 1
        stats["last_check"] = datetime.now(timezone.utc).isoformat()
        if engine_type not in self._perf_stats["latencies"]:
            self._perf_stats["latencies"][engine_type] = []
        self._perf_stats["latencies"][engine_type].append(latency_ms)
        if len(self._perf_stats["latencies"][engine_type]) > 100:
            self._perf_stats["latencies"][engine_type] = self._perf_stats["latencies"][engine_type][-100:]
        avg_latency = sum(self._perf_stats["latencies"][engine_type]) / len(self._perf_stats["latencies"][engine_type])
        stats["avg_response_time_ms"] = round(avg_latency, 2)
        stats["latency_ms"] = latency_ms
        if success:
            stats["consecutive_failures"] = 0
            stats["status"] = "healthy"
            stats["uptime_percent"] = round(((stats["requests_total"] - stats["requests_failed"]) / stats["requests_total"]) * 100, 2)
        else:
            stats["requests_failed"] += 1
            stats["consecutive_failures"] += 1
            if stats["consecutive_failures"] >= 5:
                stats["status"] = "down"
            elif stats["consecutive_failures"] >= 2:
                stats["status"] = "degraded"
            stats["uptime_percent"] = round(((stats["requests_total"] - stats["requests_failed"]) / stats["requests_total"]) * 100, 2)
        self._perf_stats["total_requests"] += 1
    
    def health_check(self, engine_type: str = None) -> Dict[str, Any]:
        """🏥 Real-time Health Monitor"""
        now = datetime.now(timezone.utc).isoformat()
        if engine_type:
            if engine_type not in self.engines:
                return {"error": f"Engine '{engine_type}' not found", "available_engines": list(self.engines.keys())}
            stats = self._health_stats.get(engine_type, {})
            return {
                "engine_type": engine_type,
                "health": {k: stats.get(k, 0) for k in ["status", "latency_ms", "uptime_percent", "requests_total", "requests_failed", "avg_response_time_ms"]},
                "last_check": stats.get("last_check", now),
                "zero_dependency": True,
                "timestamp": now
            }
        all_health = []
        healthy = degraded = down = 0
        for eng, stats in self._health_stats.items():
            st = stats.get("status", "healthy")
            if st == "down": down += 1
            elif st == "degraded": degraded += 1
            else: healthy += 1
            all_health.append({"engine_type": eng, "status": st, "latency_ms": stats.get("latency_ms", 0.0), "uptime_percent": stats.get("uptime_percent", 100.0), "requests_total": stats.get("requests_total", 0), "requests_failed": stats.get("requests_failed", 0)})
        overall = "healthy"
        if down > 0 or degraded > 0: overall = "degraded"
        return {"overall_status": overall, "engines_health": all_health, "total_engines": len(all_health), "healthy_count": healthy, "degraded_count": degraded, "down_count": down, "zero_dependency": True, "timestamp": now}
    
    # ========== PHASE 1: PARALLEL CALLS ==========
    
    def parallel_call(self, prompt: str, engines: List[str] = None, max_wait_ms: float = 30000.0) -> Dict[str, Any]:
        """⚡ Multi-Engine Parallel Call - Pick the best response"""
        start_time = time.time()
        if engines is None:
            engines = list(self.engines.keys())
        valid_engines = [e for e in engines if e in self.engines]
        if not valid_engines:
            return {"error": "No valid engines", "available": list(self.engines.keys())}
        import threading
        results = []
        errors = []
        lock = threading.Lock()
        def call_engine(eng: str):
            try:
                res = self.call_engine(eng, {"prompt": prompt})
                with lock:
                    if res.get("success"): results.append(res)
                    else: errors.append({"engine": eng, "error": res.get("error", "Unknown")})
            except Exception as e:
                with lock: errors.append({"engine": eng, "error": str(e)})
        threads = [threading.Thread(target=call_engine, args=(e,)) for e in valid_engines]
        for t in threads: t.start()
        for t in threads: t.join(timeout=max_wait_ms / 1000.0)
        total_time = (time.time() - start_time) * 1000
        best = min(results, key=lambda r: r.get("latency_ms", float('inf'))) if results else None
        for r in results: self._update_health_stats(r.get("engine", "unknown"), r.get("latency_ms", 0), True)
        for e in errors: self._update_health_stats(e.get("engine", "unknown"), 0, False)
        return {"best_response": best, "all_results": results, "errors": errors, "total_engines_called": len(valid_engines), "successful": len(results), "failed": len(errors), "total_time_ms": round(total_time, 2), "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ========== PHASE 1: RESPONSE CACHING ==========
    
    def _get_cache_key(self, engine_type: str, prompt: str) -> str:
        import hashlib
        return hashlib.md5(f"{engine_type}:{prompt}".encode()).hexdigest()
    
    def get_cached_response(self, engine_type: str, prompt: str) -> Optional[Dict[str, Any]]:
        """📦 Get cached response if available"""
        cache_key = self._get_cache_key(engine_type, prompt)
        cached = self._cache.get(cache_key)
        if cached:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached["cached_at"])).total_seconds()
            if age < 300:
                self._perf_stats["cache_hits"] += 1
                return {"cached": True, "age_seconds": round(age, 2), **cached["result"]}
            else: del self._cache[cache_key]
        self._perf_stats["cache_misses"] += 1
        return None
    
    def set_cached_response(self, engine_type: str, prompt: str, result: Dict[str, Any]):
        """📦 Store response in cache"""
        cache_key = self._get_cache_key(engine_type, prompt)
        if len(self._cache) >= self._cache_max_size:
            del self._cache[next(iter(self._cache))]
        self._cache[cache_key] = {"result": result, "cached_at": datetime.now(timezone.utc).isoformat()}
    
    def clear_cache(self) -> Dict[str, Any]:
        cleared = len(self._cache)
        self._cache.clear()
        return {"cleared": cleared, "cache_size": 0, "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        total = self._perf_stats["cache_hits"] + self._perf_stats["cache_misses"]
        return {"cache_size": len(self._cache), "max_size": self._cache_max_size, "total_hits": self._perf_stats["cache_hits"], "total_misses": self._perf_stats["cache_misses"], "hit_rate": round(self._perf_stats["cache_hits"] / max(1, total) * 100, 2), "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}
    
    # ========== PHASE 1: PERFORMANCE STATS ==========
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Get comprehensive performance statistics"""
        fastest = slowest = "N/A"
        fastest_time = float('inf')
        slowest_time = 0
        for eng, lats in self._perf_stats["latencies"].items():
            if lats:
                avg = sum(lats) / len(lats)
                if avg < fastest_time: fastest_time, fastest = avg, eng
                if avg > slowest_time: slowest_time, slowest = avg, eng
        most_used = max(self._perf_stats["requests_per_engine"].items(), key=lambda x: x[1])[0] if self._perf_stats["requests_per_engine"] else "N/A"
        all_lats = []
        for l in self._perf_stats["latencies"].values(): all_lats.extend(l)
        avg_lat = round(sum(all_lats) / len(all_lats), 2) if all_lats else 0
        total = self._perf_stats["cache_hits"] + self._perf_stats["cache_misses"]
        return {"total_requests": self._perf_stats["total_requests"], "cache_hits": self._perf_stats["cache_hits"], "cache_misses": self._perf_stats["cache_misses"], "cache_hit_rate": round(self._perf_stats["cache_hits"] / max(1, total) * 100, 2), "avg_latency_ms": avg_lat, "fastest_engine": fastest, "slowest_engine": slowest, "most_used_engine": most_used, "requests_per_engine": self._perf_stats["requests_per_engine"], "uptime_since": self._perf_stats["start_time"], "zero_dependency": True, "timestamp": datetime.now(timezone.utc).isoformat()}


# Singleton instance
ai_engine_hub = UltimateAIEngineHub()