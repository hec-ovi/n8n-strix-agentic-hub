"""PDF renderer for report artifacts."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from src.core.exceptions import ArtifactRenderError
from src.models.report import ReportDraft, ReportRequest, SourceDocument


class PdfRendererTool:
    """Render report drafts into PDF files."""

    def render(
        self,
        output_path: Path,
        data: ReportRequest,
        draft: ReportDraft,
        sources: list[SourceDocument],
    ) -> None:
        """Render a PDF artifact to disk."""
        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        heading_style = styles["Heading2"]
        body_style = styles["BodyText"]
        body_style.leading = 16
        meta_style = ParagraphStyle(
            "Meta",
            parent=body_style,
            textColor=colors.HexColor("#475569"),
        )

        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )
        story = [
            Paragraph(draft.title, title_style),
            Spacer(1, 8),
            Paragraph(f"Requester: {data.requester_name}", meta_style),
            Paragraph(f"Channel: {data.requester_channel}", meta_style),
            Paragraph(f"Topic: {data.topic}", meta_style),
            Spacer(1, 12),
            Paragraph("Executive Summary", heading_style),
            Paragraph(draft.executive_summary, body_style),
            Spacer(1, 10),
        ]

        for section in draft.sections:
            story.append(Paragraph(section.heading, heading_style))
            section_items = [
                ListItem(Paragraph(bullet, body_style), leftIndent=8)
                for bullet in section.bullets
            ]
            story.append(ListFlowable(section_items, bulletType="bullet"))
            story.append(Spacer(1, 8))

        story.append(Paragraph("Recommendations", heading_style))
        recommendation_items = [
            ListItem(Paragraph(bullet, body_style), leftIndent=8)
            for bullet in draft.recommendations
        ]
        story.append(ListFlowable(recommendation_items, bulletType="bullet"))
        story.append(Spacer(1, 8))

        story.append(Paragraph("Reference Sources", heading_style))
        if sources:
            source_items = [
                ListItem(
                    Paragraph(f"{source.title} - {source.url}", body_style),
                    leftIndent=8,
                )
                for source in sources
            ]
            story.append(ListFlowable(source_items, bulletType="bullet"))
        else:
            story.append(Paragraph("No external reference URLs were provided.", body_style))

        try:
            document.build(story)
        except Exception as exc:
            raise ArtifactRenderError(f"Failed to render PDF artifact: {exc}") from exc
