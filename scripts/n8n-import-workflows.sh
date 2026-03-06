#!/usr/bin/env bash
set -euo pipefail

if ! find n8n/workflows -maxdepth 1 -type f -name '*.json' | read -r _; then
  echo "No workflow JSON files found in n8n/workflows"
  exit 1
fi

docker compose exec -T -u node n8n \
  n8n import:workflow --separate --input=/workspace/workflows

echo "Workflow import finished."
