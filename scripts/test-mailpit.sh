#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${MAILPIT_UI_PORT:=8025}"

curl -fsS "http://127.0.0.1:${MAILPIT_UI_PORT}/api/v1/messages"
echo
