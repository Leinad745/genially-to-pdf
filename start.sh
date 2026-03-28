#!/usr/bin/env bash
set -a
source .env
set +a

mkdir -p "$DATABASE_STORAGE_PATH"

uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

default_workers=${WORKERS_COUNT:-2}
uv run python -m huey.bin.huey_consumer app.services.tasks.huey_manager.huey -w "$default_workers"

kill "$UVICORN_PID" 2>/dev/null || true
wait "$UVICORN_PID"