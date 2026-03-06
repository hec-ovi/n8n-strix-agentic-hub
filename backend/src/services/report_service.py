"""Business service for report generation."""

from pathlib import Path
from uuid import uuid4

from src.core.settings import Settings
from src.models.report import (
    ReportArtifacts,
    ReportRequest,
    ReportResponse,
    SourceDocument,
)
from src.tools.artifact_store import ArtifactStoreTool
from src.tools.email_sender import EmailSenderTool
from src.tools.llm_chat import LlmChatTool
from src.tools.markdown_renderer import MarkdownRendererTool
from src.tools.pdf_renderer import PdfRendererTool
from src.tools.prompt_loader import PromptLoaderTool
from src.tools.source_fetcher import SourceFetcherTool


class ReportService:
    """Generate structured reports and deliver them as artifacts."""

    def __init__(
        self,
        settings: Settings,
        prompt_loader: PromptLoaderTool,
        source_fetcher: SourceFetcherTool,
        llm_chat: LlmChatTool,
        markdown_renderer: MarkdownRendererTool,
        artifact_store: ArtifactStoreTool,
        pdf_renderer: PdfRendererTool,
        email_sender: EmailSenderTool,
    ) -> None:
        """Initialize a report service with injected dependencies."""
        self._settings = settings
        self._prompt_loader = prompt_loader
        self._source_fetcher = source_fetcher
        self._llm_chat = llm_chat
        self._markdown_renderer = markdown_renderer
        self._artifact_store = artifact_store
        self._pdf_renderer = pdf_renderer
        self._email_sender = email_sender

    @classmethod
    def build(cls) -> "ReportService":
        """Build a report service using environment-driven defaults."""
        settings = Settings()
        return cls(
            settings=settings,
            prompt_loader=PromptLoaderTool(),
            source_fetcher=SourceFetcherTool(),
            llm_chat=LlmChatTool(settings=settings),
            markdown_renderer=MarkdownRendererTool(),
            artifact_store=ArtifactStoreTool(settings=settings),
            pdf_renderer=PdfRendererTool(),
            email_sender=EmailSenderTool(settings=settings),
        )

    async def generate(self, data: ReportRequest) -> ReportResponse:
        """Generate report content, persist artifacts, and deliver the email."""
        job_id = uuid4().hex
        sources = await self._source_fetcher.fetch(data.reference_urls)
        prompt = self._build_prompt(data=data, sources=sources)
        draft = await self._llm_chat.generate_report(prompt=prompt)

        markdown_body = self._markdown_renderer.render(data=data, draft=draft, sources=sources)
        report_dir = self._artifact_store.prepare_job_directory(job_id)
        markdown_path = report_dir / "report.md"
        pdf_path = report_dir / "report.pdf"

        self._artifact_store.write_text(markdown_path, markdown_body)
        self._pdf_renderer.render(output_path=pdf_path, data=data, draft=draft, sources=sources)

        artifacts = self._build_artifacts(
            job_id=job_id,
            markdown_path=markdown_path,
            pdf_path=pdf_path,
        )

        await self._email_sender.send_report(
            recipient_email=str(data.recipient_email),
            subject=draft.email_subject,
            body=draft.email_body,
            attachment_path=pdf_path,
        )

        return ReportResponse(
            job_id=job_id,
            title=draft.title,
            executive_summary=draft.executive_summary,
            artifacts=artifacts,
            email_status="sent",
            delivered_to=data.recipient_email,
        )

    def _build_prompt(self, data: ReportRequest, sources: list[SourceDocument]) -> str:
        """Render the report-generation prompt using the request and fetched sources."""
        prompt_template = self._prompt_loader.load("report_brief.md")
        formatted_sources = "\n".join(
            [
                f"- title: {source.title}\n  url: {source.url}\n  content: {source.content[:2000]}"
                for source in sources
            ]
        )
        briefing_notes = "\n".join([f"- {note}" for note in data.briefing_notes]) or "- none"
        source_block = formatted_sources or "- none"

        return (
            f"{prompt_template}\n\n"
            f"REQUESTER NAME: {data.requester_name}\n"
            f"REQUESTER CHANNEL: {data.requester_channel}\n"
            f"TOPIC: {data.topic}\n"
            f"OBJECTIVE: {data.objective}\n"
            f"TONE: {data.tone}\n"
            f"BRIEFING NOTES:\n{briefing_notes}\n"
            f"REFERENCE SOURCES:\n{source_block}\n"
        )

    def _build_artifacts(
        self,
        job_id: str,
        markdown_path: Path,
        pdf_path: Path,
    ) -> ReportArtifacts:
        """Create artifact metadata for the API response."""
        base_url = self._settings.public_base_url.rstrip("/")
        return ReportArtifacts(
            markdown_path=str(markdown_path),
            markdown_url=f"{base_url}/artifacts/{job_id}/report.md",
            pdf_path=str(pdf_path),
            pdf_url=f"{base_url}/artifacts/{job_id}/report.pdf",
        )
