#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${TELEGRAM_BOT_TOKEN:=}"
: "${TELEGRAM_BOT_API_BASE_URL:=https://api.telegram.org}"
: "${WEBHOOK_URL:=}"
: "${TELEGRAM_WEBHOOK_PATH:=telegram-report-bot}"
: "${TELEGRAM_ALLOWED_UPDATES:=[\"message\"]}"
: "${TELEGRAM_DROP_PENDING_UPDATES:=true}"
: "${TELEGRAM_MAX_CONNECTIONS:=20}"
: "${TELEGRAM_WEBHOOK_SECRET_TOKEN:=}"

if [ -z "${TELEGRAM_BOT_TOKEN}" ]; then
  echo "TELEGRAM_BOT_TOKEN is required."
  exit 1
fi

if [ -z "${WEBHOOK_URL}" ]; then
  echo "WEBHOOK_URL is required."
  exit 1
fi

if [[ "${WEBHOOK_URL}" != https://* ]]; then
  echo "WEBHOOK_URL must be public HTTPS for Telegram."
  exit 1
fi

webhook_url="${WEBHOOK_URL%/}/webhook/${TELEGRAM_WEBHOOK_PATH}"

payload="$(
  cat <<EOF
{
  "url": "${webhook_url}",
  "allowed_updates": ${TELEGRAM_ALLOWED_UPDATES},
  "drop_pending_updates": ${TELEGRAM_DROP_PENDING_UPDATES},
  "max_connections": ${TELEGRAM_MAX_CONNECTIONS}
}
EOF
)"

if [ -n "${TELEGRAM_WEBHOOK_SECRET_TOKEN}" ]; then
  payload="$(
    python - "${payload}" "${TELEGRAM_WEBHOOK_SECRET_TOKEN}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
payload["secret_token"] = sys.argv[2]
print(json.dumps(payload))
PY
  )"
fi

curl -fsS "${TELEGRAM_BOT_API_BASE_URL}/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "${payload}"
echo
