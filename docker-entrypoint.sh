#!/usr/bin/env bash
set -e

# ensure environment variables are loaded
set -a
source .env
set +a

# create directories and fix permissions, running as root
mkdir -p "$DATABASE_STORAGE_PATH"
chown -R pwuser:pwuser "$DATABASE_STORAGE_PATH" || true

# optionally fix data directory permissions too
mkdir -p "$DATA_DIRECTORY"
chown -R pwuser:pwuser "$DATA_DIRECTORY" || true

# now drop privileges and exec the real start script as pwuser
exec su pwuser -s /bin/bash -c "./start.sh"
