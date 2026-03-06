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

curl -fsS "${TELEGRAM_BOT_API_BASE_URL}/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${webhook_url}\"
  }"
echo
