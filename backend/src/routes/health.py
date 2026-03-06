"""Health check routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.models.report import HealthResponse
from src.services.health_service import HealthService

router = APIRouter(tags=["Health"])


def get_health_service() -> HealthService:
    """Build a health service instance."""
    return HealthService()


@router.get("/health")
async def health(service: Annotated[HealthService, Depends(get_health_service)]) -> HealthResponse:
    """Return a simple health status."""
    return await service.check()
