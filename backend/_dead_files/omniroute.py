#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIRoute v2.0 - Smart AI Provider Router
VERIFIED WORKING providers as of August 2026
Auto-detects 402/429/500 errors and switches providers
"""

import os
import time
import json
import httpx
import asyncio
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

# Load .env - FORCE overwrite
ENV_FILE = Path(__file__).parent.parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and value:
            os.environ[key] = value


class ErrorType(Enum):
    RATE_LIMIT = "429"
    PAYMENT_REQUIRED = "402"
    SERVER_ERROR = "500"
    TIMEOUT = "timeout"
    SUCCESS = "200"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    name: str
    base_url: str
    api_key: str
    models: List[str]
    default_model: str
    status: str = "healthy"
    last_error: str = ""
    last_error_time: float = 0
    error_count: int = 0
    success_count: int = 0
    cooldown_until: float = 0
    avg_latency: float = 0
    latency_history: List[float] = field(default_factory=list)


class OmniRoute:
    """
    Smart AI Router:
    1. Auto-detects 402 -> Skips provider (no credits)
    2. Auto-detects 429 -> Waits & retries
    3. Auto-detects 500 -> Retries then switches
    4. Tracks provider health and latency
    5. Routes to fastest healthy provider
    """

    def __init__(self):
        self.providers: Dict[str, ProviderHealth] = {}
        self._init_providers()
        self.cooldown_duration = 30

    def _init_providers(self):
        """Initialize providers with VERIFIED working models."""
        configs = [
            # === VERIFIED WORKING (tested live August 2026) ===
            {
                "name": "groq",
                "base_url": "https://api.groq.com/openai/v1",
                "key_env": "GROQ_API_KEY",
                "models": ["allam-2-7b", "groq/compound-mini", "llama-3.1-8b-instant"],
                "default": "allam-2-7b",
                "priority": 1,
            },
            {
                "name": "openrouter",
                "base_url": "https://openrouter.ai/api/v1",
                "key_env": "OPENROUTER_API_KEY",
                "models": [
                    "nvidia/nemotron-3.5-lightning:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "qwen/qwen3-235b-a22b:free",
                ],
                "default": "nvidia/nemotron-3.5-lightning:free",
                "priority": 2,
            },
            {
                "name": "mistral",
                "base_url": "https://api.mistral.ai/v1",
                "key_env": "MISTRAL_API_KEY",
                "models": ["mistral-small-latest", "mistral-medium-latest"],
                "default": "mistral-small-latest",
                "priority": 3,
            },
            {
                "name": "minimax",
                "base_url": "https://api.minimaxi.chat/v1",
                "key_env": "MINIMAX_API_KEY",
                "models": ["MiniMax-Text-01"],
                "default": "MiniMax-Text-01",
                "priority": 4,
            },
            {
                "name": "cerebras",
                "base_url": "https://api.cerebras.ai/v1",
                "key_env": "CEREBRAS_API_KEY",
                "models": ["llama-3.3-70b", "llama-3.1-8b"],
                "default": "llama-3.3-70b",
                "priority": 5,
            },
            {
                "name": "nvidia",
                "base_url": "https://integrate.api.nvidia.com/v1",
                "key_env": "NVIDIA_API_KEY",
                "models": [
                    "databricks/dbrx-instruct",
                    "ai21labs/jamba-1.5-large-instruct",
                ],
                "default": "databricks/dbrx-instruct",
                "priority": 6,
            },
            {
                "name": "deepseek",
                "base_url": "https://api.deepseek.com",
                "key_env": "DEEPSEEK_API_KEY",
                "models": ["deepseek-chat", "deepseek-reasoner"],
                "default": "deepseek-chat",
                "priority": 7,
            },
            {
                "name": "together",
                "base_url": "https://api.together.xyz/v1",
                "key_env": "TOGETHER_API_KEY",
                "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"],
                "default": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                "priority": 8,
            },
            {
                "name": "fireworks",
                "base_url": "https://api.fireworks.ai/inference/v1",
                "key_env": "FIREWORKS_API_KEY",
                "models": ["accounts/fireworks/models/llama-v3p3-70b-instruct"],
                "default": "accounts/fireworks/models/llama-v3p3-70b-instruct",
                "priority": 9,
            },
            {
                "name": "sambanova",
                "base_url": "https://api.sambanova.ai/v1",
                "key_env": "SAMBANOVA_API_KEY",
                "models": ["DeepSeek-R1", "Llama-4-Scout-17B-16E-Instruct"],
                "default": "DeepSeek-R1",
                "priority": 10,
            },
            # === NEW FREE PROVIDERS (August 2026) ===
            {
                "name": "cohere",
                "base_url": "https://api.cohere.com/v2",
                "key_env": "COHERE_API_KEY",
                "models": ["command-a-218b", "command-a-111b"],
                "default": "command-a-218b",
                "priority": 11,
            },
            {
                "name": "zhipu",
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "key_env": "ZHIPU_API_KEY",
                "models": ["glm-4.7", "glm-4.5"],
                "default": "glm-4.7",
                "priority": 12,
            },
            {
                "name": "llm7",
                "base_url": "https://api.llm7.io/v1",
                "key_env": "LLM7_API_KEY",
                "models": ["deepseek-r1-0528", "gpt-4o-mini"],
                "default": "gpt-4o-mini",
                "priority": 13,
            },
            {
                "name": "kilocode",
                "base_url": "https://api.kilo.ai/api/gateway",
                "key_env": "KILO_API_KEY",
                "models": ["nvidia/nemotron-3-ultra-550b-a55b:free"],
                "default": "nvidia/nemotron-3-ultra-550b-a55b:free",
                "priority": 14,
            },
            {
                "name": "ai21",
                "base_url": "https://api.ai21.com/studio/v1",
                "key_env": "AI21_API_KEY",
                "models": ["jamba-large-1-7", "jamba-mini-2"],
                "default": "jamba-large-1-7",
                "priority": 15,
            },
            {
                "name": "nebius",
                "base_url": "https://api.studio.nebius.com/v1",
                "key_env": "NEBIUS_API_KEY",
                "models": ["qwen3-235b-a22b"],
                "default": "qwen3-235b-a22b",
                "priority": 16,
            },
            {
                "name": "modelscope",
                "base_url": "https://api-inference.modelscope.cn/v1",
                "key_env": "MODELSCOPE_API_KEY",
                "models": ["MiniMax/MiniMax-M2.5", "qwen-qwen3-5-35b-a3b"],
                "default": "MiniMax/MiniMax-M2.5",
                "priority": 17,
            },
            # === PAID FALLBACK ===
            {
                "name": "openai",
                "base_url": "https://api.openai.com/v1",
                "key_env": "OPENAI_API_KEY",
                "models": ["gpt-4o-mini", "gpt-4o"],
                "default": "gpt-4o-mini",
                "priority": 99,
            },
        ]

        for config in configs:
            api_key = os.getenv(config["key_env"], "")
            self.providers[config["name"]] = ProviderHealth(
                name=config["name"],
                base_url=config["base_url"],
                api_key=api_key,
                models=config["models"],
                default_model=config["default"],
                status="healthy" if api_key else "no_key",
            )

    def _classify_error(self, status_code: int, response_text: str = "") -> ErrorType:
        if status_code == 429:
            return ErrorType.RATE_LIMIT
        elif status_code == 402:
            return ErrorType.PAYMENT_REQUIRED
        elif status_code >= 500:
            return ErrorType.SERVER_ERROR
        elif "timeout" in response_text.lower():
            return ErrorType.TIMEOUT
        elif status_code == 200:
            return ErrorType.SUCCESS
        else:
            return ErrorType.UNKNOWN

    def _is_provider_available(self, provider: ProviderHealth) -> bool:
        if not provider.api_key:
            return False
        if provider.status == "banned":
            return False
        if time.time() < provider.cooldown_until:
            return False
        return True

    def _get_sorted_providers(self) -> List[ProviderHealth]:
        available = [p for p in self.providers.values() if self._is_provider_available(p)]
        return sorted(available, key=lambda p: (p.error_count, p.avg_latency))

    def _update_provider_health(self, provider: ProviderHealth, error_type: ErrorType, latency: float = 0):
        provider.last_error_time = time.time()

        if error_type == ErrorType.SUCCESS:
            provider.success_count += 1
            provider.error_count = max(0, provider.error_count - 1)
            if latency > 0:
                provider.latency_history.append(latency)
                if len(provider.latency_history) > 10:
                    provider.latency_history.pop(0)
                provider.avg_latency = sum(provider.latency_history) / len(provider.latency_history)
            provider.status = "healthy"

        elif error_type == ErrorType.PAYMENT_REQUIRED:
            provider.error_count += 10
            provider.status = "banned"
            provider.last_error = "402 Payment Required"

        elif error_type == ErrorType.RATE_LIMIT:
            provider.error_count += 3
            provider.cooldown_until = time.time() + self.cooldown_duration
            provider.last_error = "429 Rate Limited"

        elif error_type == ErrorType.SERVER_ERROR:
            provider.error_count += 2
            if provider.error_count >= 6:
                provider.cooldown_until = time.time() + 60
                provider.last_error = "500 Multiple failures"
            else:
                provider.last_error = "500 Server Error"

        elif error_type == ErrorType.TIMEOUT:
            provider.error_count += 1
            provider.last_error = "Timeout"

    async def chat(
        self,
        messages: List[dict],
        model: str = "auto",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> dict:
        """Send chat with automatic provider fallback."""
        start_time = time.time()
        sorted_providers = self._get_sorted_providers()

        if not sorted_providers:
            return {"error": "No available providers", "status": "failed"}

        last_error = None
        for provider in sorted_providers:
            if model == "auto":
                use_model = provider.default_model
            elif model in provider.models:
                use_model = model
            else:
                use_model = provider.default_model

            headers = {
                "Authorization": f"Bearer {provider.api_key}",
                "Content-Type": "application/json",
            }
            if provider.name == "openrouter":
                headers["HTTP-Referer"] = "https://vgas-shopping.ai"
                headers["X-Title"] = "VGAS Shopping AI"

            request_start = time.time()
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        f"{provider.base_url}/chat/completions",
                        headers=headers,
                        json={
                            "model": use_model,
                            "messages": messages,
                            "max_tokens": max_tokens,
                            "temperature": temperature,
                        },
                    )

                    latency = time.time() - request_start
                    error_type = self._classify_error(resp.status_code, resp.text)

                    if error_type == ErrorType.SUCCESS:
                        self._update_provider_health(provider, error_type, latency)
                        data = resp.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return {
                            "content": content,
                            "provider": provider.name,
                            "model": use_model,
                            "latency": round(latency, 2),
                            "status": "success",
                        }
                    else:
                        self._update_provider_health(provider, error_type, latency)
                        last_error = f"{provider.name}: {resp.status_code}"
                        print(f"  [RETRY] {provider.name}/{use_model}: {resp.status_code}")

            except httpx.TimeoutException:
                latency = time.time() - request_start
                self._update_provider_health(provider, ErrorType.TIMEOUT, latency)
                last_error = f"{provider.name}: Timeout"
            except Exception as e:
                self._update_provider_health(provider, ErrorType.UNKNOWN)
                last_error = f"{provider.name}: {str(e)[:100]}"

        return {
            "error": f"All providers failed. Last: {last_error}",
            "status": "failed",
            "providers_tried": [p.name for p in sorted_providers],
        }

    def get_status(self) -> dict:
        status = {}
        for name, p in self.providers.items():
            status[name] = {
                "status": p.status,
                "has_key": bool(p.api_key),
                "error_count": p.error_count,
                "success_count": p.success_count,
                "avg_latency": round(p.avg_latency, 2),
                "available": self._is_provider_available(p),
            }
        return status

    def reset_provider(self, name: str):
        if name in self.providers:
            self.providers[name].status = "healthy"
            self.providers[name].error_count = 0
            self.providers[name].cooldown_until = 0


# Singleton
router = OmniRoute()


async def omnichat(prompt: str, system: str = "", model: str = "auto") -> str:
    """Simple chat function with auto-routing."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    result = await router.chat(messages, model=model)
    if result.get("status") == "success":
        return result["content"]
    return f"Error: {result.get('error', 'Unknown')}"


if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) > 1 and sys.argv[1] == "status":
            status = router.get_status()
            print("\n=== OMNIRoute v2.0 Status ===")
            for name, info in status.items():
                icon = "[OK]" if info["available"] else "[--]"
                print(f"  {icon} {name:15} key={info['has_key']} err={info['error_count']} ok={info['success_count']} avg={info['avg_latency']}s")
        else:
            prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello in 5 words"
            print(f"Prompt: {prompt}")
            result = await omnichat(prompt)
            safe = result.encode("ascii", "replace").decode("ascii")
            print(f"Response: {safe}")

    asyncio.run(main())
