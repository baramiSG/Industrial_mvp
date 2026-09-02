from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = ROOT / "src" / "ior_mvp" / "static"


def module_paths(static_root: Path = STATIC_ROOT) -> tuple[Path, ...]:
    """Return every production JavaScript module in stable order."""
    return tuple(sorted(static_root.rglob("*.js")))


def check_modules(
    node: str,
    paths: Sequence[Path],
    *,
    root: Path = ROOT,
) -> tuple[int, list[str]]:
    """Syntax-check module sources through Node's module parser."""
    findings: list[str] = []
    for path in paths:
        try:
            source = path.read_text(encoding="utf-8")
            result = subprocess.run(
                [node, "--input-type=module", "--check"],
                input=source,
                check=False,
                capture_output=True,
                text=True,
            )
        except (OSError, UnicodeError) as exc:
            return 2, [f"{path}: {type(exc).__name__}: {exc}"]
        if result.returncode != 0:
            display = (
                path.relative_to(root).as_posix()
                if path.is_relative_to(root)
                else path.as_posix()
            )
            detail = (result.stderr or result.stdout).strip()
            findings.append(f"{display}: {detail}")
    return (1 if findings else 0), findings


def main(argv: Sequence[str] | None = None) -> int:
    """Run the production ES-module syntax gate."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", required=True)
    args = parser.parse_args(argv)
    paths = module_paths()
    if not paths:
        print("ES MODULE CHECK ERROR: no production JavaScript files", file=sys.stderr)
        return 2
    status, findings = check_modules(args.node, paths)
    if status == 2:
        print("ES MODULE CHECK ERROR", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return status
    if findings:
        print("ES MODULE CHECK FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"ES MODULE CHECK PASS ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
