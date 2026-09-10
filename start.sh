#!/bin/sh
set -e
cd /app
echo "mf-backend start.sh delegating to python -m app.run" >&2
exec python -m app.run
