#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_DIR="n8n/workflows/active"

if [ "${1:-}" = "--all" ]; then
  WORKFLOW_DIR="n8n/workflows"
fi

if ! find "${WORKFLOW_DIR}" -type f -name '*.json' | read -r _; then
  echo "No workflow JSON files found in ${WORKFLOW_DIR}"
  exit 1
fi

workflow_files=()
while IFS= read -r workflow_file; do
  workflow_files+=("${workflow_file}")
done < <(find "${WORKFLOW_DIR}" -type f -name '*.json' | sort)

workflow_list="$(docker compose exec -T -u node n8n n8n list:workflow || true)"
imported_count=0
skipped_count=0
staging_dir=""
staged_any=0

for workflow_file in "${workflow_files[@]}"; do
  workflow_name="$(sed -n 's/  "name": "\(.*\)",/\1/p' "${workflow_file}" | head -n 1)"

  if [ -z "${workflow_name}" ]; then
    echo "Could not determine workflow name from ${workflow_file}"
    exit 1
  fi

  existing_id="$(
    printf '%s\n' "${workflow_list}" |
      awk -F'|' -v workflow_name="${workflow_name}" '$2 == workflow_name { id = $1 } END { print id }'
  )"

  if [ -n "${existing_id}" ]; then
    echo "Skipping import for ${workflow_name} (${existing_id})"
    skipped_count=$((skipped_count + 1))
    continue
  fi

  if [ -z "${staging_dir}" ]; then
    staging_dir="$(mktemp -d n8n/workflows/.import-XXXXXX)"
    trap 'if [ -n "${staging_dir}" ] && [ -d "${staging_dir}" ]; then rm -rf "${staging_dir}"; fi' EXIT
  fi

  cp "${workflow_file}" "${staging_dir}/"
  imported_count=$((imported_count + 1))
  staged_any=1
done

if [ "${staged_any}" -eq 1 ]; then
  docker compose exec -T -u node n8n \
    n8n import:workflow --separate --input="/workspace/workflows/${staging_dir##n8n/workflows/}"
fi

echo "Workflow import finished. Imported ${imported_count}, skipped ${skipped_count}."
