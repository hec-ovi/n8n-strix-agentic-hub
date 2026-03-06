#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${REPORT_SERVICE_PORT:=18100}"

curl -fsS "http://127.0.0.1:${REPORT_SERVICE_PORT}/api/v1/report-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "requester_name": "Local Smoke Test",
    "requester_channel": "script",
    "recipient_email": "reports@example.com",
    "topic": "n8n local report automation",
    "objective": "Explain the value of orchestrating report creation with n8n and a separate backend service",
    "tone": "executive",
    "briefing_notes": [
      "Use a concise executive tone.",
      "Explain why separating orchestration from compute is valuable."
    ]
  }'
echo
