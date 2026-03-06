# Report Service

FastAPI service for turning automation requests into deliverable report artifacts.

## Responsibilities

- Fetch optional reference URLs
- Generate a structured brief with a local OpenAI-compatible chat endpoint
- Render Markdown and PDF artifacts
- Deliver the report through SMTP
- Normalize Telegram webhook payloads into report jobs
- Expose artifact files over HTTP for downstream automation steps

## SMTP Configuration

- local development: `mailpit:1025` with `SMTP_SECURITY=none`
- authenticated providers: set `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_SECURITY`
- Gmail typically uses `smtp.gmail.com:587` with `SMTP_SECURITY=starttls`
- the password for Gmail SMTP should be an app password, not the normal account password

## Endpoints

- `POST /api/v1/report-jobs`
- `POST /api/v1/telegram/report-jobs`
- `GET /health`

## Local Commands

```bash
uv sync --frozen
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir src
uv run pytest
```
