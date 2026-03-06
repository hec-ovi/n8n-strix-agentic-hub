#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  .local/n8n \
  .local/postgres \
  .local/redis \
  .local/report-artifacts \
  n8n/workflows \
  n8n/backups \
  n8n/local-files

chmod 700 .local/n8n

echo "Local directories are ready."
