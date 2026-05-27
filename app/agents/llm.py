"""Groq LLM factory."""

from __future__ import annotations

from langchain_groq import ChatGroq

from app.core.config import get_settings


def get_llm(temperature: float | None = None) -> ChatGroq:
    """Create a Groq chat model client."""

    settings = get_settings()
    if not settings.groq_api_key:
        msg = "GROQ_API_KEY is not configured. Add it to .env before calling LLM endpoints."
        raise RuntimeError(msg)
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=settings.llm_temperature if temperature is None else temperature,
    )

