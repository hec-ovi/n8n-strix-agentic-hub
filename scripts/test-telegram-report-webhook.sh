#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${N8N_PORT:=5678}"
: "${MAILPIT_UI_PORT:=8025}"
: "${TELEGRAM_WEBHOOK_PATH:=telegram-report-bot}"

before_count="$(
  curl -fsS "http://127.0.0.1:${MAILPIT_UI_PORT}/api/v1/messages" |
    python -c "import json,sys; print(json.load(sys.stdin)['total'])"
)"

curl -fsS "http://127.0.0.1:${N8N_PORT}/webhook/${TELEGRAM_WEBHOOK_PATH}" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 10001,
    "message": {
      "message_id": 42,
      "date": 1739999999,
      "text": "/report Build me a concise briefing on why n8n should orchestrate report generation instead of owning all compute directly.",
      "from": {
        "id": 9001,
        "is_bot": false,
        "first_name": "Telegram",
        "last_name": "Tester",
        "username": "telegram_tester"
      },
      "chat": {
        "id": 9001,
        "type": "private",
        "first_name": "Telegram",
        "last_name": "Tester",
        "username": "telegram_tester"
      }
    }
  }' >/dev/null

for _ in $(seq 1 60); do
  current_count="$(
    curl -fsS "http://127.0.0.1:${MAILPIT_UI_PORT}/api/v1/messages" |
      python -c "import json,sys; print(json.load(sys.stdin)['total'])"
  )"

  if [ "${current_count}" -gt "${before_count}" ]; then
    curl -fsS "http://127.0.0.1:${MAILPIT_UI_PORT}/api/v1/messages" |
      python -c "import json,sys; messages=json.load(sys.stdin)['messages']; print(messages[0]['Subject']); print(messages[0]['Snippet'])"
    exit 0
  fi

  sleep 2
done

echo "Timed out waiting for the Telegram webhook flow to deliver an email."
exit 1
