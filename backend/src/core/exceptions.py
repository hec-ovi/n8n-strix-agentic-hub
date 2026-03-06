"""Domain exceptions for the report service."""


class ReportServiceError(Exception):
    """Base exception for report service failures."""


class LlmRequestError(ReportServiceError):
    """Raised when the LLM request fails or returns invalid data."""


class SourceFetchError(ReportServiceError):
    """Raised when a reference source cannot be fetched."""


class ArtifactRenderError(ReportServiceError):
    """Raised when an artifact cannot be generated."""


class EmailDeliveryError(ReportServiceError):
    """Raised when the report email cannot be delivered."""
