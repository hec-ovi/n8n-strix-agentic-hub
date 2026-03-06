#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_DIR="n8n/workflows/active"

if ! find "${WORKFLOW_DIR}" -type f -name '*.json' | read -r _; then
  echo "No workflow JSON files found in ${WORKFLOW_DIR}"
  exit 1
fi

workflow_files=()
while IFS= read -r workflow_file; do
  workflow_files+=("${workflow_file}")
done < <(find "${WORKFLOW_DIR}" -type f -name '*.json' | sort)

workflow_list="$(docker compose exec -T -u node n8n n8n list:workflow)"
published_count=0

for workflow_file in "${workflow_files[@]}"; do
  workflow_name="$(sed -n 's/  "name": "\(.*\)",/\1/p' "${workflow_file}" | head -n 1)"

  if [ -z "${workflow_name}" ]; then
    echo "Could not determine workflow name from ${workflow_file}"
    exit 1
  fi

  workflow_id="$(
    printf '%s\n' "${workflow_list}" |
      awk -F'|' -v workflow_name="${workflow_name}" '$2 == workflow_name { id = $1 } END { print id }'
  )"

  if [ -z "${workflow_id}" ]; then
    echo "Workflow ${workflow_name} is not imported."
    exit 1
  fi

  docker compose exec -T -u node n8n \
    n8n publish:workflow --id="${workflow_id}"

  echo "Published ${workflow_name} (${workflow_id})"
  published_count=$((published_count + 1))
done

docker compose restart n8n n8n-worker

echo "Published ${published_count} workflow(s) and restarted n8n services."
