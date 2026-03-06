#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${N8N_PORT:=5678}"

curl -fsS "http://127.0.0.1:${N8N_PORT}/healthz/readiness"
echo
