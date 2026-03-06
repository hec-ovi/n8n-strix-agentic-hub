#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

: "${OLLAMA_PORT:=11434}"
: "${OLLAMA_MODEL:=gpt-oss:20b}"

curl -fsS "http://127.0.0.1:${OLLAMA_PORT}/api/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"${OLLAMA_MODEL}\",
    \"prompt\": \"Reply with exactly: n8n-ollama-ok\",
    \"stream\": false
  }"
echo
