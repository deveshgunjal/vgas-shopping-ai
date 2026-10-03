"""AI helper utilities for VGAS Shopping AI"""

from typing import Dict, Any
from app.api.v1.ai_client import AIClient
from app.core.config import settings


def build_ai_prompt(intent: str, message: str, context: Dict[str, Any], language: str) -> str:
    prompt = [
        f"You are VGAS Shopping AI Assistant.",
        f"Language: {language}",
        f"Intent: {intent}",
        f"User message: {message}",
        "Context data:",
        str(context),
        "Provide a concise and helpful shopping assistant response."
    ]
    return "\n".join(prompt)


async def get_ai_response(intent: str, message: str, context: Dict[str, Any], language: str) -> str:
    prompt = build_ai_prompt(intent, message, context, language)
    return await AIClient.generate_text(prompt, temperature=settings.AI_TEMPERATURE, max_tokens=settings.AI_MAX_TOKENS)
