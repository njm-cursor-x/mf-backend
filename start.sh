#!/bin/sh
set -e
cd /app
port="${PORT:-8080}"
echo "mf-backend start.sh port=${port} (ignoring extra args: $*)" >&2
exec uvicorn app.main:app --host 0.0.0.0 --port "$port"
