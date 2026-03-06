#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="n8n/backups/${STAMP}"

mkdir -p "${OUTPUT_DIR}"

docker compose exec -T -u node n8n \
  n8n export:workflow --backup --output="/workspace/backups/${STAMP}"

echo "Workflows exported to ${OUTPUT_DIR}"
