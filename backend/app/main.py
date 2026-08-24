"""FastAPI application factory and entrypoint.

Phase 2 — FastAPI foundation: app factory, middleware, CORS, request tracing,
error handlers, health endpoints, and router mounting.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.core.middleware import RequestIdMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown events."""
    yield


def create_app() -> FastAPI:
    """Application factory for the VBC Command Center backend API."""

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # ---------------------------------------------------------
    # Request ID / tracing middleware
    # ---------------------------------------------------------
    app.add_middleware(RequestIdMiddleware)

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ---------------------------------------------------------
    # Centralized exception handlers
    # ---------------------------------------------------------
    register_exception_handlers(app)

    # ---------------------------------------------------------
    # API v1
    # ---------------------------------------------------------
    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    return app


app = create_app()