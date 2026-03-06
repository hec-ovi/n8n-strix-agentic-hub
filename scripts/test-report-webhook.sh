#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${N8N_PORT:=5678}"
: "${REPORT_REQUEST_WEBHOOK_PATH:=report-request-v2}"

curl -fsS "http://127.0.0.1:${N8N_PORT}/webhook/${REPORT_REQUEST_WEBHOOK_PATH}" \
  -H "Content-Type: application/json" \
  -d '{
    "requester_name": "Webhook Smoke Test",
    "requester_channel": "webhook",
    "recipient_email": "reports@example.com",
    "topic": "n8n artifact workflow",
    "objective": "Create a report artifact and deliver it by email using the local stack",
    "tone": "executive",
    "briefing_notes": [
      "Mention the role of n8n as the orchestrator.",
      "Mention that the PDF is the generated output artifact."
    ]
  }'
echo
