# n8n Strix Agentic Hub

Local-first automation stack for orchestrating `n8n` workflows with a self-hosted `Ollama` model on AMD ROCm.

![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-111111?style=for-the-badge&logo=ollama&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![ROCm](https://img.shields.io/badge/AMD_ROCm-C8102E?style=for-the-badge&logo=amd&logoColor=white)

## Overview

This repository packages a production-shaped local stack for automation, artifact generation, and AI-assisted workflow execution. The current implementation is centered on webhook-driven report pipelines:

`Webhook -> n8n -> report-service -> Ollama -> Markdown/PDF artifact -> email`

## Tech Used

- `n8n` for workflow orchestration and webhook handling
- `FastAPI` for the report-generation service
- `Ollama` for local OpenAI-compatible chat inference
- `gpt-oss:20b` as the default local model
- `PostgreSQL` for n8n persistence
- `Redis` for n8n queue mode
- `Mailpit` for local SMTP testing and inbox inspection
- `ReportLab` for PDF generation
- `uv` for Python dependency and environment management
- `Docker Compose` for local deployment
- `AMD ROCm` for GPU-backed local inference
- `JSON workflow artifacts` for code-first n8n versioning

## Architecture

`n8n` is the orchestrator, not the heavy compute runtime. Workflow nodes handle triggers, control flow, retries, and downstream calls. The backend service performs the AI request, report assembly, PDF rendering, and SMTP delivery.

Current workflow artifacts:

- [`n8n/workflows/active/report-request-webhook.json`](./n8n/workflows/active/report-request-webhook.json)
- Published webhook path: `/webhook/report-request-v2`
- [`n8n/workflows/active/telegram-report-webhook.json`](./n8n/workflows/active/telegram-report-webhook.json)
- Published webhook path: `/webhook/telegram-report-bot`

## Current Layout

```text
.
├── backend/
├── docker-compose.yml
├── llm.txt
├── README.md
├── .env.template
├── frontend/
├── n8n/
│   ├── backups/
│   ├── local-files/
│   └── workflows/
├── ollama/
└── scripts/
```

The `frontend/` scaffold is currently inactive and not required by the running stack.

## Prerequisites

- Docker Engine with Compose
- AMD ROCm-capable host if you want GPU-backed local inference
- The `gpt-oss:20b` model already present on the host under `OLLAMA_MODELS_DIR`

## Quick Start

1. Copy the environment template:

   ```bash
   cp .env.template .env
   ```

2. Review `.env` and adjust:

   - secrets
   - local ports
   - `OLLAMA_MODELS_DIR`
   - absolute host paths
   - `REPORT_REQUEST_WEBHOOK_PATH` if you rename the workflow path

3. Create the local bind-mount folders:

   ```bash
   ./scripts/bootstrap-local-dirs.sh
   ```

4. Start the stack:

   ```bash
   ./scripts/start-stack.sh
   ```

5. Open:

   - `http://localhost:5678` for `n8n`
   - `http://localhost:11434` for `Ollama`
   - `http://localhost:18100/docs` for `report-service`
   - `http://localhost:8025` for `Mailpit`

No external API keys are required for the current generic webhook-to-email flow. The only required values in `.env` are local secrets, passwords, ports, and host paths.

Telegram is different:

- for the local simulated Telegram smoke test, no Telegram credential is required
- for a real Telegram bot, you need a bot token issued by Telegram via `@BotFather`
- Telegram must be able to reach your `WEBHOOK_URL`, which means a public HTTPS URL is required for real inbound bot traffic
- long-running report generation can exceed what is comfortable for a direct Telegram webhook round-trip, so production setups often introduce a queue, bridge, or lighter acknowledgement path for Telegram ingress

SMTP is also different in production:

- local Mailpit uses unauthenticated SMTP on `mailpit:1025`
- real providers usually require credentials plus `STARTTLS` or `SSL`
- Gmail SMTP requires an account-specific app password rather than the normal account password
- Google Workspace SMTP relay is often a cleaner production fit than a personal Gmail inbox

## Workflow Management

Workflows live in JSON form under [`n8n/workflows`](./n8n/workflows).

Useful commands:

```bash
./scripts/start-stack.sh
./scripts/n8n-import-workflows.sh
./scripts/n8n-activate-workflows.sh
./scripts/n8n-export-workflows.sh
./scripts/test-n8n-health.sh
./scripts/test-ollama.sh
./scripts/test-report-service.sh
./scripts/test-report-webhook.sh
./scripts/test-telegram-report-webhook.sh
./scripts/test-mailpit.sh
```

Workflows are treated as deployable artifacts: versioned in Git, imported/exported with the CLI, and edited through the UI only when it improves delivery speed.

## Verification

Backend quality checks:

```bash
cd backend
uv sync --frozen
uv run ruff check
uv run pytest
```

Stack smoke checks:

```bash
./scripts/test-n8n-health.sh
./scripts/test-ollama.sh
./scripts/test-report-service.sh
./scripts/test-report-webhook.sh
./scripts/test-telegram-report-webhook.sh
./scripts/test-mailpit.sh
```

Telegram helper:

```bash
./scripts/register-telegram-webhook.sh
```

This helper configures Telegram to deliver bot updates to the `telegram-report-bot` n8n webhook. It requires both `TELEGRAM_BOT_TOKEN` and a public HTTPS `WEBHOOK_URL`.

## Production Env

Real Gmail / Google Workspace SMTP:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER=your.name@example.com
SMTP_USERNAME=your.name@example.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_SECURITY=starttls
```

Google Workspace relay variant:

```env
SMTP_HOST=smtp-relay.gmail.com
SMTP_PORT=587
SMTP_SENDER=reports@example.com
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_SECURITY=starttls
```

Real Telegram bot:

```env
WEBHOOK_URL=https://your-public-domain.example/
TELEGRAM_BOT_TOKEN=123456789:telegram-bot-token
TELEGRAM_WEBHOOK_PATH=telegram-report-bot
TELEGRAM_ALLOWED_UPDATES=["message"]
TELEGRAM_DROP_PENDING_UPDATES=true
TELEGRAM_MAX_CONNECTIONS=20
TELEGRAM_WEBHOOK_SECRET_TOKEN=replace-with-a-random-secret
TELEGRAM_REPORT_RECIPIENT_EMAIL=reports@example.com
```

Then register Telegram:

```bash
./scripts/register-telegram-webhook.sh
```

## Production Notes

- `queue` mode is enabled because it is the official scalable mode for `n8n`.
- `Postgres` is used instead of SQLite.
- `Redis` backs the queue.
- `report-service` isolates AI and PDF work from the workflow engine.
- `manual` executions are offloaded to workers too.
- `healthz` and readiness endpoints are enabled.
- Runtime data is bind-mounted on the host.

Important Telegram caveat:

`setWebhook` secret tokens are supported by the helper script, but this repository does not yet enforce Telegram header verification inside `n8n` itself. For hardened internet-facing production ingress, place a validating reverse proxy or custom ingress in front of the Telegram webhook before forwarding into `n8n`.

Important caveat:

`n8n` documents that queue mode is not a good fit for binary persistence on the local filesystem. If we later build PDF-heavy or file-heavy flows, we should move binary storage to S3-compatible storage instead of relying on local filesystem persistence.

## Scaling Direction

The local Compose stack mirrors the production shape that `n8n` recommends:

- scale `n8n-worker` replicas for execution throughput
- keep `Postgres` and `Redis` externalized
- optionally split webhook processing into dedicated instances
- move artifact storage from local bind mounts to object storage for multi-node deployments

The Docker images in this repository are suitable building blocks for a future Kubernetes deployment. Kubernetes runs containers, not specifically Docker as a runtime, but Docker-built OCI images are standard inputs for Kubernetes clusters.
