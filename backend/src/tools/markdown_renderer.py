"""Markdown renderer for generated reports."""

from src.models.report import ReportDraft, ReportRequest, SourceDocument


class MarkdownRendererTool:
    """Render structured report content into Markdown."""

    def render(
        self,
        data: ReportRequest,
        draft: ReportDraft,
        sources: list[SourceDocument],
    ) -> str:
        """Render a report draft as Markdown."""
        source_lines = [
            f"- [{source.title}]({source.url})"
            for source in sources
        ] or ["- No external reference URLs were provided."]

        section_lines = []
        for section in draft.sections:
            bullets = "\n".join([f"- {bullet}" for bullet in section.bullets])
            section_lines.append(f"## {section.heading}\n{bullets}")

        recommendation_lines = "\n".join([f"- {item}" for item in draft.recommendations])
        source_block = "\n".join(source_lines)
        section_block = "\n\n".join(section_lines)

        return (
            f"# {draft.title}\n\n"
            f"**Requester:** {data.requester_name}\n\n"
            f"**Channel:** {data.requester_channel}\n\n"
            f"**Topic:** {data.topic}\n\n"
            f"## Executive Summary\n{draft.executive_summary}\n\n"
            f"{section_block}\n\n"
            f"## Recommendations\n{recommendation_lines}\n\n"
            f"## Reference Sources\n{source_block}\n"
        )
