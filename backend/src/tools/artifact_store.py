"""Artifact storage tool."""

from pathlib import Path

from src.core.settings import Settings


class ArtifactStoreTool:
    """Persist generated artifacts in the configured storage directory."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the storage tool."""
        self._root = Path(settings.artifacts_dir)

    def prepare_job_directory(self, job_id: str) -> Path:
        """Create and return the directory used for a report job."""
        job_dir = self._root / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def write_text(self, path: Path, content: str) -> None:
        """Write a UTF-8 text artifact to disk."""
        path.write_text(content, encoding="utf-8")
