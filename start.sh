#!/usr/bin/env bash

set -a
source .env
set +a

mkdir -p "$DATABASE_STORAGE_PATH"

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

# run huey consumer; workers count set via WORKERS_COUNT env var
default_workers=${WORKERS_COUNT:-2}
huey_consumer.py app.services.tasks.huey_manager.huey -w "$default_workers"

# when consumer exits stop uvicorn
kill "$UVICORN_PID" 2>/dev/null || true
wait "$UVICORN_PID"