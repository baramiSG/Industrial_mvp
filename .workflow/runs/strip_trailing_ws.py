"""Strip trailing whitespace from the given files (records only; content otherwise unchanged)."""
from __future__ import annotations

import sys
from pathlib import Path


def main(paths: list[str]) -> int:
    changed = 0
    for raw in paths:
        path = Path(raw)
        text = path.read_text(encoding="utf-8")
        fixed = "\n".join(line.rstrip() for line in text.splitlines()) + ("\n" if text.endswith("\n") else "")
        if fixed != text:
            path.write_text(fixed, encoding="utf-8")
            changed += 1
            print(f"stripped: {raw}")
    print(f"files_changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
