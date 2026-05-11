#!/usr/bin/env bash
set -e

# ensure environment variables are loaded
set -a
source .env
set +a

# create directories
mkdir -p "$DATABASE_STORAGE_PATH"
mkdir -p "$DATA_DIRECTORY"

exec ./start.sh
