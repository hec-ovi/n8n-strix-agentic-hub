"""Prompt loader tool."""

from pathlib import Path


class PromptLoaderTool:
    """Load prompt files from the prompts directory."""

    def __init__(self) -> None:
        """Initialize the prompt loader."""
        self._prompts_dir = Path(__file__).resolve().parents[1] / "prompts"

    def load(self, filename: str) -> str:
        """Load a prompt file by name."""
        return (self._prompts_dir / filename).read_text(encoding="utf-8")
