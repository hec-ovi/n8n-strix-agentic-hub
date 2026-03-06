Workflow JSON files live here.

Structure:

- `active/`: workflows imported and activated by the helper scripts
- `optional/`: workflows or scaffolds that require extra credentials or manual wiring

Current active workflow artifact:

- `active/report-request-webhook.json`
  - published webhook path: `/webhook/report-request-v2`
  - orchestration path: `Webhook -> HTTP Request -> report-service`
- `active/telegram-report-webhook.json`
  - published webhook path: `/webhook/telegram-report-bot`
  - orchestration path: `Webhook -> HTTP Request -> report-service`

Treat this folder as the versioned source of truth for code-first `n8n` workflows.
