"""Unit tests for the health service."""

import pytest

from src.services.health_service import HealthService


@pytest.mark.asyncio
async def test_health_service_returns_ok() -> None:
    """Health service should return a healthy status."""
    service = HealthService()

    result = await service.check()

    assert result.status == "ok"
