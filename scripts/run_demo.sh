#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"
exec uvicorn ior_mvp.app:app --host "${IOR_HOST:-127.0.0.1}" --port "${IOR_PORT:-8000}" --reload
