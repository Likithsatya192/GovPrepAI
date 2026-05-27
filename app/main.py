"""FastAPI application factory for GovPrepAI."""

from __future__ import annotations

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import GovPrepApi


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""

    fastapi_app = FastAPI(
        title="GovPrepAI",
        description="Smart Government Exam Preparation Multi-Agent System",
        version="1.0.0",
    )
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fastapi_app.include_router(GovPrepApi().router)
    return fastapi_app


app = create_app()


if __name__ == "__main__":
    reload_enabled = os.getenv("APP_RELOAD", "").lower() in {"1", "true", "yes"}
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload_enabled,
        reload_dirs=["app"] if reload_enabled else None,
    )
