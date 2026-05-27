"""Runtime settings for GovPrepAI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Environment-backed application settings."""

    groq_api_key: str
    groq_model: str
    app_env: str
    chroma_persist_dir: str
    embedding_model: str
    llm_temperature: float
    search_region: str
    search_max_results: int


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so clients are reused consistently."""

    load_dotenv()
    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        app_env=os.getenv("APP_ENV", "development"),
        chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        ),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        search_region=os.getenv("SEARCH_REGION", "in-en"),
        search_max_results=int(os.getenv("SEARCH_MAX_RESULTS", "5")),
    )
