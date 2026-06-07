import logging

import requests

from app.core.config import settings
from app.services.safety_service import (
    CRISIS_MESSAGE,
    DISCLAIMER,
    contains_crisis_language,
)

logger = logging.getLogger(__name__)


def _fallback_reflection(text: str, mood: str | None) -> str:
    mood_phrase = f" Feeling {mood} can carry a lot with it." if mood else ""
    return (
        "It sounds like you are taking time to notice what is happening inside "
        f"you, and that is a meaningful step.{mood_phrase} Consider naming one "
        "small thing you need right now and one person or practice that could "
        "support you today."
    )


def _openai_reflection(text: str, mood: str | None) -> str:
    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.OPENAI_MODEL,
            "instructions": (
                "Write a brief, warm, non-diagnostic mental wellness reflection. "
                "Do not give medical advice. Encourage one practical next step. "
                "Do not claim to be a therapist."
            ),
            "input": f"Mood: {mood or 'not provided'}\nEntry: {text}",
            "max_output_tokens": 180,
        },
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("output_text"):
        return payload["output_text"].strip()
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"].strip()
    raise ValueError("AI provider returned no reflection text")


def create_reflection(text: str, mood: str | None = None) -> dict:
    if contains_crisis_language(text):
        return {
            "reflection": CRISIS_MESSAGE,
            "crisis_detected": True,
            "source": "safety",
            "disclaimer": DISCLAIMER,
        }

    source = "fallback"
    reflection = _fallback_reflection(text, mood)
    if settings.OPENAI_API_KEY:
        try:
            reflection = _openai_reflection(text, mood)
            source = "openai"
        except (requests.RequestException, ValueError) as exc:
            logger.warning("AI reflection unavailable; using fallback: %s", exc)

    return {
        "reflection": reflection,
        "crisis_detected": False,
        "source": source,
        "disclaimer": DISCLAIMER,
    }
