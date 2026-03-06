# n8n Strix Agentic Hub

Local-first automation stack for orchestrating `n8n` workflows with a self-hosted `Ollama` model on AMD ROCm.

## Overview

This repository packages a production-shaped local stack for automation, artifact generation, and AI-assisted workflow execution. The current implementation is centered on a webhook-driven report pipeline:

`Webhook -> n8n -> report-service -> Ollama -> Markdown/PDF artifact -> email`

Core services:

- `n8n` main instance for the editor, API, timers, and inbound webhooks
- `n8n-worker` for queued workflow execution
- `postgres` for durable workflow state
- `redis` for queue transport
- `ollama` on ROCm using the host-mounted `gpt-oss:20b` model
- `report-service` for synthesis, artifact rendering, and SMTP delivery
- `mailpit` for local SMTP capture and inbox inspection

## Architecture

`n8n` is the orchestrator, not the heavy compute runtime. Workflow nodes handle triggers, control flow, retries, and downstream calls. The backend service performs the AI request, report assembly, PDF rendering, and SMTP delivery.

Current workflow artifact:

- [`n8n/workflows/active/report-request-webhook.json`](./n8n/workflows/active/report-request-webhook.json)
- Published webhook path: `/webhook/report-request-v2`

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

No external API keys are required for the current webhook-to-email flow. The only required values in `.env` are local secrets, passwords, ports, and host paths. Telegram credentials are only needed if a Telegram trigger/action workflow is added later.

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
./scripts/test-mailpit.sh
```

## Production Notes

- `queue` mode is enabled because it is the official scalable mode for `n8n`.
- `Postgres` is used instead of SQLite.
- `Redis` backs the queue.
- `report-service` isolates AI and PDF work from the workflow engine.
- `manual` executions are offloaded to workers too.
- `healthz` and readiness endpoints are enabled.
- Runtime data is bind-mounted on the host.

Important caveat:

`n8n` documents that queue mode is not a good fit for binary persistence on the local filesystem. If we later build PDF-heavy or file-heavy flows, we should move binary storage to S3-compatible storage instead of relying on local filesystem persistence.

## Scaling Direction

The local Compose stack mirrors the production shape that `n8n` recommends:

- scale `n8n-worker` replicas for execution throughput
- keep `Postgres` and `Redis` externalized
- optionally split webhook processing into dedicated instances
- move artifact storage from local bind mounts to object storage for multi-node deployments

The Docker images in this repository are suitable building blocks for a future Kubernetes deployment. Kubernetes runs containers, not specifically Docker as a runtime, but Docker-built OCI images are standard inputs for Kubernetes clusters.
