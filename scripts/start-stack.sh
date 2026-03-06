#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  echo ".env not found. Copy .env.template to .env and review it first."
  exit 1
fi

./scripts/bootstrap-local-dirs.sh
docker compose --env-file .env up -d --build
./scripts/n8n-import-workflows.sh
./scripts/n8n-activate-workflows.sh

echo "Stack started and workflows imported."
