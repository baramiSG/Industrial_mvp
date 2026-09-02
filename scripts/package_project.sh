#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/../Industrial_Opportunity_Resolution_MVP_POC.zip}"
if ! TOP="$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null)" \
  || [[ "$TOP" != "$ROOT" ]]; then
  echo "Packaging requires the project root to be a Git working tree." >&2
  exit 2
fi
OUT="$(realpath -m "$OUT")"
rm -f "$OUT"
git -C "$ROOT" ls-files -z | ROOT="$ROOT" OUT="$OUT" python3 -c '
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(os.environ["ROOT"])
output = Path(os.environ["OUT"])
tracked = [
    os.fsdecode(item)
    for item in sys.stdin.buffer.read().split(b"\0")
    if item
]
with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for relative in tracked:
        source = root / relative
        if source.is_file():
            archive.write(source, f"{root.name}/{relative}")
'
echo "$OUT"
