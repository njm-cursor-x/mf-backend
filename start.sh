#!/bin/sh
set -e
port="${PORT:-8080}"
exec uvicorn app.main:app --host 0.0.0.0 --port "$port"
