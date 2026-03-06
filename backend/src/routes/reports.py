"""Report generation routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.exceptions import (
    ArtifactRenderError,
    EmailDeliveryError,
    LlmRequestError,
    ReportServiceError,
    SourceFetchError,
)
from src.models.report import ReportRequest, ReportResponse
from src.services.report_service import ReportService

router = APIRouter(tags=["Reports"])


def get_report_service() -> ReportService:
    """Build a report service instance with runtime dependencies."""
    return ReportService.build()


@router.post("/report-jobs")
async def create_report_job(
    data: ReportRequest,
    service: Annotated[ReportService, Depends(get_report_service)],
) -> ReportResponse:
    """Generate and deliver a report artifact.

    Args:
        data: Incoming request describing the report to build.
        service: Business service that orchestrates report generation.

    Returns:
        Metadata describing the generated report and delivery outcome.

    Raises:
        HTTPException: If any stage of report generation fails.
    """
    try:
        return await service.generate(data)
    except SourceFetchError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except (LlmRequestError, ArtifactRenderError, EmailDeliveryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except ReportServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
