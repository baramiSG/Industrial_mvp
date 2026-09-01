#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/../Industrial_Opportunity_Resolution_MVP_POC.zip}"
cd "$(dirname "$ROOT")"
rm -f "$OUT"
zip -qr "$OUT" "$(basename "$ROOT")" \
  -x "*/.venv/*" "*/__pycache__/*" "*/.pytest_cache/*" "*.pyc"
echo "$OUT"
