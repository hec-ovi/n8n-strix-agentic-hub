"""Unit tests for the Markdown renderer."""

from src.models.report import ReportDraft, ReportRequest, ReportSection, SourceDocument
from src.tools.markdown_renderer import MarkdownRendererTool


def test_markdown_renderer_includes_key_sections() -> None:
    """Rendered Markdown should include the main report sections."""
    tool = MarkdownRendererTool()
    request = ReportRequest(
        requester_name="Test User",
        requester_channel="webhook",
        recipient_email="reports@example.com",
        topic="Automation orchestration",
        objective="Explain why n8n should orchestrate rather than compute",
        briefing_notes=["Keep it direct."],
    )
    draft = ReportDraft(
        title="Automation Report",
        executive_summary="n8n should orchestrate external services.",
        sections=[
            ReportSection(
                heading="Findings",
                bullets=[
                    "n8n is effective as an orchestration runtime.",
                    "Heavy work belongs in separate services.",
                ],
            )
        ],
        recommendations=["Keep AI inference outside n8n."],
        email_subject="Report ready",
        email_body="Attached is your report.",
    )
    sources = [
        SourceDocument(
            url="https://example.com/article",
            title="Example Article",
            content="Source content",
        )
    ]

    result = tool.render(data=request, draft=draft, sources=sources)

    assert "# Automation Report" in result
    assert "## Executive Summary" in result
    assert "## Findings" in result
    assert "## Recommendations" in result
    assert "Example Article" in result


def test_report_draft_defaults_email_fields() -> None:
    """Report draft should tolerate missing email fields from the model."""
    draft = ReportDraft.model_validate(
        {
            "title": "Automation Report",
            "executive_summary": "Summary",
            "sections": [{"heading": "Findings", "bullets": ["One", "Two"]}],
            "recommendations": ["Keep orchestration separate from compute."],
        }
    )

    assert draft.email_subject == "Your report is ready"
    assert draft.email_body == "Your report is attached."
