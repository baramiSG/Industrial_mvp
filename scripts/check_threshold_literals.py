from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS_PATH = ROOT / "config" / "thresholds.v1.yaml"
SOURCE_DIR = ROOT / "src" / "ior_mvp"
EXEMPT_NUMERIC_VALUES = {0.0, 1.0, 2.0, 3.0}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    value: float

    def render(self) -> str:
        return f"{self.path}:{self.line}:{self.value:g}"


def collect_numeric_values(value: Any) -> set[float]:
    if isinstance(value, bool):
        return set()
    if isinstance(value, (int, float)):
        return {float(value)}
    if isinstance(value, dict):
        values: set[float] = set()
        for nested in value.values():
            values.update(collect_numeric_values(nested))
        return values
    if isinstance(value, list):
        values = set()
        for nested in value:
            values.update(collect_numeric_values(nested))
        return values
    return set()


def scan_source(
    source: str,
    *,
    path: str,
    threshold_values: set[float],
) -> list[Finding]:
    tree = ast.parse(source, filename=path)
    findings: set[Finding] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for operand in (node.left, *node.comparators):
            if not isinstance(operand, ast.Constant):
                continue
            value = operand.value
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            numeric_value = float(value)
            if (
                numeric_value in threshold_values
                and numeric_value not in EXEMPT_NUMERIC_VALUES
            ):
                findings.add(
                    Finding(path=path, line=operand.lineno, value=numeric_value)
                )
    return sorted(findings)


def load_threshold_values(path: Path) -> set[float]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Threshold configuration must be a mapping: {path}")
    values = collect_numeric_values(payload)
    if not values:
        raise ValueError(f"Threshold configuration has no numeric values: {path}")
    return values


def scan_repository(
    source_dir: Path,
    threshold_path: Path,
    *,
    root: Path,
) -> tuple[list[Finding], int, int]:
    threshold_values = load_threshold_values(threshold_path)
    source_paths = sorted(source_dir.glob("*.py"))
    findings: list[Finding] = []
    for source_path in source_paths:
        display_path = (
            source_path.relative_to(root).as_posix()
            if source_path.is_relative_to(root)
            else source_path.as_posix()
        )
        source = source_path.read_text(encoding="utf-8")
        findings.extend(
            scan_source(
                source,
                path=display_path,
                threshold_values=threshold_values,
            )
        )
    return sorted(findings), len(source_paths), len(threshold_values)


def main(
    source_dir: Path = SOURCE_DIR,
    threshold_path: Path = THRESHOLDS_PATH,
    root: Path = ROOT,
) -> int:
    try:
        findings, source_count, threshold_count = scan_repository(
            source_dir,
            threshold_path,
            root=root,
        )
    except (
        OSError,
        UnicodeError,
        SyntaxError,
        TypeError,
        ValueError,
        yaml.YAMLError,
    ) as exc:
        print(
            f"THRESHOLD LITERAL SCAN ERROR: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    if findings:
        print("THRESHOLD LITERAL SCAN FAIL")
        for finding in findings:
            print(f"- {finding.render()}")
        return 1

    print(
        "THRESHOLD LITERAL SCAN PASS "
        f"({source_count} Python files; {threshold_count} configured numeric values)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
