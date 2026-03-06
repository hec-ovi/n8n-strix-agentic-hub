"""Health service."""

from src.models.report import HealthResponse


class HealthService:
    """Simple service for liveness checks."""

    async def check(self) -> HealthResponse:
        """Return a healthy response."""
        return HealthResponse(status="ok")
