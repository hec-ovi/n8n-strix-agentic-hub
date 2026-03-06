# Report Service

FastAPI service for turning automation requests into deliverable report artifacts.

## Responsibilities

- Fetch optional reference URLs
- Generate a structured brief with a local OpenAI-compatible chat endpoint
- Render Markdown and PDF artifacts
- Deliver the report through SMTP
- Expose artifact files over HTTP for downstream automation steps

## Local Commands

```bash
uv sync --frozen
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src
uv run pytest
```
