#!/bin/bash
set -euo pipefail

MODEL_NAME="${OLLAMA_MODEL:-gpt-oss:20b}"
OLLAMA_PID=""

log() {
  echo "[ollama] $1"
}

cleanup() {
  log "Shutting down"
  if [ -n "$OLLAMA_PID" ]; then
    kill "$OLLAMA_PID" 2>/dev/null || true
    wait "$OLLAMA_PID" 2>/dev/null || true
  fi
}
trap cleanup SIGTERM SIGINT

log "Model: $MODEL_NAME"
log "Starting Ollama server"
/bin/ollama serve &
OLLAMA_PID=$!

log "Waiting for port 11434"
for i in {1..60}; do
  if timeout 2 bash -c 'cat < /dev/null > /dev/tcp/localhost/11434' 2>/dev/null; then
    log "Ollama is accepting connections"
    break
  fi

  if [ "$i" -eq 60 ]; then
    log "Timed out waiting for Ollama"
    exit 1
  fi

  sleep 1
done

sleep 2

if /bin/ollama list 2>/dev/null | grep -q "$MODEL_NAME"; then
  log "Model already present"
else
  log "Downloading model $MODEL_NAME"
  /bin/ollama pull "$MODEL_NAME"
fi

if ! /bin/ollama list 2>/dev/null | grep -q "$MODEL_NAME"; then
  log "Model verification failed"
  exit 1
fi

log "Ollama ready"
wait "$OLLAMA_PID"
