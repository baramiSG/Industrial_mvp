#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
PYTHONPATH=src python3 scripts/verify_integrity.py
PYTHONPATH=src pytest -q
exec uvicorn ior_mvp.app:app --host 127.0.0.1 --port 8000 --reload
