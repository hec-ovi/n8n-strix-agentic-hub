"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.settings import Settings
from src.routes.health import router as health_router
from src.routes.reports import router as reports_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    app.include_router(health_router)
    app.include_router(reports_router, prefix=settings.api_prefix)

    artifacts_path = Path(settings.artifacts_dir)
    artifacts_path.mkdir(parents=True, exist_ok=True)
    app.mount("/artifacts", StaticFiles(directory=artifacts_path), name="artifacts")
    return app


app = create_app()
