"""Models for report generation."""

from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ReportRequest(BaseModel):
    """Request payload for generating a report artifact."""

    requester_name: Annotated[str, Field(description="Display name of the requester")]
    requester_channel: Annotated[
        str, Field(description="Source channel of the request")
    ] = "webhook"
    recipient_email: Annotated[EmailStr, Field(description="Email address receiving the report")]
    topic: Annotated[str, Field(description="Main research or report topic")]
    objective: Annotated[str, Field(description="Specific goal of the report")]
    tone: Annotated[
        Literal["executive", "concise", "technical"],
        Field(description="Report tone used for the output"),
    ] = "executive"
    reference_urls: Annotated[
        list[HttpUrl],
        Field(
            default_factory=list,
            description="Optional URLs that should be incorporated into the brief",
        ),
    ]
    briefing_notes: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Additional notes that should influence the report",
        ),
    ]


class SourceDocument(BaseModel):
    """Normalized external source document."""

    url: Annotated[HttpUrl, Field(description="Source URL")]
    title: Annotated[str, Field(description="Human-readable source title")]
    content: Annotated[str, Field(description="Extracted plain text content")]


class ReportSection(BaseModel):
    """Logical section in a generated report."""

    heading: Annotated[str, Field(description="Section heading")]
    bullets: Annotated[list[str], Field(description="Bullet points for the section")]


class ReportDraft(BaseModel):
    """Structured report content returned by the LLM."""

    title: Annotated[str, Field(description="Report title")]
    executive_summary: Annotated[str, Field(description="Short executive summary")]
    sections: Annotated[list[ReportSection], Field(description="Detailed sections")]
    recommendations: Annotated[list[str], Field(description="Final action recommendations")]
    email_subject: Annotated[
        str, Field(description="Suggested email subject")
    ] = "Your report is ready"
    email_body: Annotated[
        str, Field(description="Suggested email body")
    ] = "Your report is attached."


class ReportArtifacts(BaseModel):
    """Generated artifact paths and URLs."""

    markdown_path: Annotated[str, Field(description="Absolute path to the Markdown artifact")]
    markdown_url: Annotated[str, Field(description="Public URL for the Markdown artifact")]
    pdf_path: Annotated[str, Field(description="Absolute path to the PDF artifact")]
    pdf_url: Annotated[str, Field(description="Public URL for the PDF artifact")]


class ReportResponse(BaseModel):
    """Response payload after report generation and delivery."""

    job_id: Annotated[str, Field(description="Unique job identifier")]
    title: Annotated[str, Field(description="Generated report title")]
    executive_summary: Annotated[str, Field(description="Generated executive summary")]
    artifacts: Annotated[ReportArtifacts, Field(description="Artifact metadata")]
    email_status: Annotated[str, Field(description="Email delivery status")]
    delivered_to: Annotated[EmailStr, Field(description="Recipient address used for delivery")]


class HealthResponse(BaseModel):
    """Health response payload."""

    status: Annotated[str, Field(description="Overall health state")]
