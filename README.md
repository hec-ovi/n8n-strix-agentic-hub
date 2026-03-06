# n8n Strix Agentic Hub

Local-first learning repo for building `n8n` automations with a self-hosted `Ollama` model on AMD ROCm.

## What This Repo Is

This project is set up to learn the real shape of automation platforms:

- `Zapier`: managed SaaS automation with triggers, actions, filters, and paths.
- `n8n`: self-hosted automation/orchestration runtime with the same trigger/action model, plus stronger code, branching, AI, and self-host control.

The first milestone in this repo is a production-shaped local stack:

- `n8n` main instance
- `n8n` worker in queue mode
- `PostgreSQL`
- `Redis`
- `Ollama` on ROCm using `gpt-oss:20b`

## Why This Shape

This is the clean mental model:

`Trigger -> logic/transform -> action`

Examples:

- Telegram message arrives -> summarize with local LLM -> send email
- Webhook receives lead data -> enrich -> store -> notify Slack/Telegram
- Email arrives -> classify -> create task -> alert team

The important correction is that `n8n` is not only for messaging triggers. It is an automation runtime for webhooks, schedules, polling, branching, retries, approvals, sub-workflows, code, and AI/tool execution.

## Current Layout

```text
.
├── docker-compose.yml
├── ollama/
├── n8n/
│   ├── backups/
│   ├── local-files/
│   └── workflows/
└── scripts/
```

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

3. Create the local bind-mount folders:

   ```bash
   ./scripts/bootstrap-local-dirs.sh
   ```

4. Start the stack:

   ```bash
   docker compose --env-file .env up -d --build
   ```

5. Open:

   - `http://localhost:5678` for `n8n`
   - `http://localhost:11434` for `Ollama`

## Code-First Workflow Handling

Workflows live in JSON form under [`n8n/workflows`](./n8n/workflows).

Useful commands:

```bash
./scripts/n8n-import-workflows.sh
./scripts/n8n-export-workflows.sh
./scripts/test-n8n-health.sh
./scripts/test-ollama.sh
```

This is the key idea: you can absolutely treat `n8n` workflows as code artifacts, version them, import/export them with the CLI, and only use the UI when it helps you move faster.

## Production Notes

- `queue` mode is enabled because it is the official scalable mode for `n8n`.
- `Postgres` is used instead of SQLite.
- `Redis` backs the queue.
- `manual` executions are offloaded to workers too.
- `healthz` and readiness endpoints are enabled.
- Runtime data is bind-mounted on the host.

Important caveat:

`n8n` documents that queue mode is not a good fit for binary persistence on the local filesystem. If we later build PDF-heavy or file-heavy flows, we should move binary storage to S3-compatible storage instead of relying on local filesystem persistence.

## What We Build Next

The next milestone should be one real automation, not theory. The best first one is:

`Webhook -> local Ollama summary/classification -> Telegram or email action`

It is fast to demo, easy to reason about, and gives you the exact `trigger -> AI -> action` pattern that interviewers expect.
