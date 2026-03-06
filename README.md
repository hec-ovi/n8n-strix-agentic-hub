# n8n Strix Agentic Hub

Self-hosted automation stack built around `n8n`, a local `Ollama` model on AMD ROCm, and a small `FastAPI` service that turns incoming requests into report artifacts and emails.

![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-111111?style=for-the-badge&logo=ollama&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![ROCm](https://img.shields.io/badge/AMD_ROCm-C8102E?style=for-the-badge&logo=amd&logoColor=white)

## Overview

This repo is meant to keep `n8n` focused on orchestration and let the heavier work happen somewhere else. Right now it ships with two working flows:

- `Webhook -> n8n -> report-service -> Ollama -> Markdown/PDF -> email`
- `Telegram-style webhook -> n8n -> report-service -> Markdown/PDF -> email`

The main idea is simple: `n8n` receives the event, routes it, retries it, and keeps the workflow visible. The backend service does the AI call, builds the report, renders the PDF, and sends the email.

## Tech Used

- `n8n` for workflow orchestration and webhook handling
- `FastAPI` for the report-generation service
- `Ollama` for local OpenAI-compatible chat inference
- `gpt-oss:20b` as the default local model
- `PostgreSQL` for n8n persistence
- `Redis` for queue mode
- `Mailpit` for local SMTP testing and inbox inspection
- `ReportLab` for PDF generation
- `uv` for Python dependency management
- `Docker Compose` for local deployment
- `AMD ROCm` for GPU-backed local inference
- `JSON workflow artifacts` for code-first n8n versioning

## How It Works

The runtime split is intentional:

- `n8n` handles triggers, branching, retries, and delivery flow
- `report-service` handles prompt building, PDF rendering, and SMTP delivery
- `Ollama` stays behind an OpenAI-compatible chat endpoint so the model layer is easy to swap later

Active workflow artifacts live here:

- [`n8n/workflows/active/report-request-webhook.json`](./n8n/workflows/active/report-request-webhook.json)
- [`n8n/workflows/active/telegram-report-webhook.json`](./n8n/workflows/active/telegram-report-webhook.json)

Current published paths:

- `/webhook/report-request-v2`
- `/webhook/telegram-report-bot`

## Layout

```text
.
├── backend/
├── docker-compose.yml
├── llm.txt
├── README.md
├── .env.template
├── n8n/
│   ├── backups/
│   ├── local-files/
│   └── workflows/
├── ollama/
└── scripts/
```

## Quick Start

1. Copy the environment template.

```bash
cp .env.template .env
```

2. Review `.env` and adjust the basics:

- secrets and passwords
- local ports
- `OLLAMA_MODELS_DIR`
- bind-mounted host paths

3. Create the local directories.

```bash
./scripts/bootstrap-local-dirs.sh
```

4. Start the stack.

```bash
./scripts/start-stack.sh
```

5. Open the services:

- `http://localhost:5678` for `n8n`
- `http://localhost:11434` for `Ollama`
- `http://localhost:18100/docs` for `report-service`
- `http://localhost:8025` for `Mailpit`

## What Works Today

- direct backend report generation
- generic n8n webhook flow
- Telegram-shaped webhook flow
- local SMTP delivery through Mailpit
- workflow import/export through JSON artifacts and CLI helpers

Useful commands:

```bash
./scripts/test-n8n-health.sh
./scripts/test-ollama.sh
./scripts/test-report-service.sh
./scripts/test-report-webhook.sh
./scripts/test-telegram-report-webhook.sh
./scripts/test-mailpit.sh
```

Backend checks:

```bash
cd backend
uv sync --frozen
uv run ruff check
uv run pytest
```

## Email and Telegram

Local email works out of the box because the stack includes `Mailpit`. Messages are sent over SMTP, but they stay inside your local Compose network and show up in the Mailpit UI.

If you want real email delivery, switch the SMTP settings in `.env` to a real provider. Two common options are:

Gmail SMTP:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER=your.name@example.com
SMTP_USERNAME=your.name@example.com
SMTP_PASSWORD=your-16-digit-app-password
SMTP_SECURITY=starttls
```

Google Workspace relay:

```env
SMTP_HOST=smtp-relay.gmail.com
SMTP_PORT=587
SMTP_SENDER=reports@example.com
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_SECURITY=starttls
```

Telegram is split into two modes:

- local testing: no Telegram credential needed
- real bot: requires a real bot token and a public HTTPS webhook URL

Example production Telegram settings:

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

Then register the bot webhook:

```bash
./scripts/register-telegram-webhook.sh
```

## Notes for Production

If you want to push this past local development, the shape is already good:

- `n8n` is running in queue mode
- `Postgres` and `Redis` are already separated out
- heavy work already lives outside the workflow engine

The next things to harden are the practical ones:

- move artifacts to object storage if you expect many PDFs or more than one node
- put proper HTTPS ingress in front of `n8n`
- validate Telegram traffic at the edge if you expose that webhook publicly
- use real SMTP credentials instead of Mailpit
- scale `n8n-worker` before touching the rest of the stack

The model side is also flexible. Today it points at local `Ollama`, but the backend is already speaking to an OpenAI-compatible chat endpoint, so swapping the inference target later is straightforward.
