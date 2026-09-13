from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    rule: str


class ScannerError(RuntimeError):
    """Raised when the repository cannot be scanned safely."""


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("secret:github-pat", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("secret:aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "secret:private-key-header",
        re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    ("secret:sk-token", re.compile(r"sk-[A-Za-z0-9]{20,}")),
)


def normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def prohibited_path_rules(path: str) -> tuple[str, ...]:
    normalized = normalize_path(path)
    parts = tuple(part for part in normalized.split("/") if part)
    basename = parts[-1] if parts else normalized
    lowercase_basename = basename.lower()
    rules: list[str] = []

    if "Zone.Identifier" in normalized:
        rules.append("path:Zone.Identifier")
    if ".env" in parts:
        rules.append("path:.env")
    if ".venv" in parts:
        rules.append("path:.venv/")
    if "__pycache__" in parts:
        rules.append("path:__pycache__")
    if lowercase_basename.endswith(".pyc"):
        rules.append("path:*.pyc")
    if ".DS_Store" in parts:
        rules.append("path:.DS_Store")
    if lowercase_basename.endswith(".pem"):
        rules.append("path:*.pem")
    if lowercase_basename.endswith(".key"):
        rules.append("path:*.key")
    if lowercase_basename.endswith(".p12"):
        rules.append("path:*.p12")
    if normalized == ".workflow/logs" or normalized.startswith(".workflow/logs/"):
        rules.append("path:.workflow/logs/")
    if (
        ".secrets" in parts
        and normalized != ".secrets/neo4j_auth.example.txt"
    ):
        rules.append("path:.secrets/")

    return tuple(rules)


def decode_tracked_text(content: bytes) -> str | None:
    if b"\x00" in content:
        return None
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan_tracked_files(files: Mapping[str, bytes]) -> tuple[Finding, ...]:
    findings: set[Finding] = set()
    for raw_path in sorted(files):
        path = normalize_path(raw_path)
        for rule in prohibited_path_rules(path):
            findings.add(Finding(path=path, rule=rule))

        text = decode_tracked_text(files[raw_path])
        if text is None:
            continue
        for rule, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.add(Finding(path=path, rule=rule))

    return tuple(sorted(findings))


def parse_git_ls_files(output: bytes) -> tuple[str, ...]:
    raw_paths = output.split(b"\0")
    if raw_paths and raw_paths[-1] == b"":
        raw_paths.pop()
    if any(raw_path == b"" for raw_path in raw_paths):
        raise ScannerError("git ls-files returned an empty tracked path")
    return tuple(sorted(os.fsdecode(raw_path) for raw_path in raw_paths))


def git_tracked_paths(root: Path) -> tuple[str, ...]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as error:
        raise ScannerError("git executable not found") from error
    if result.returncode != 0:
        raise ScannerError(f"git ls-files failed with exit code {result.returncode}")
    return parse_git_ls_files(result.stdout)


def git_deleted_paths(root: Path) -> tuple[str, ...]:
    """Return tracked paths Git identifies as deleted in the worktree."""
    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "-z",
                "--diff-filter=D",
            ],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as error:
        raise ScannerError("git executable not found") from error
    if result.returncode != 0:
        raise ScannerError(
            "git diff for deleted paths failed with "
            f"exit code {result.returncode}"
        )
    return parse_git_ls_files(result.stdout)


def load_tracked_files(root: Path, paths: Sequence[str]) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in paths:
        candidate = root / path
        try:
            if candidate.is_symlink():
                files[path] = os.fsencode(os.readlink(candidate))
            else:
                files[path] = candidate.read_bytes()
        except OSError as error:
            raise ScannerError(f"unable to read tracked file: {path}") from error
    return files


def scan_repository(root: Path) -> tuple[tuple[Finding, ...], int]:
    paths = git_tracked_paths(root)
    deleted = set(git_deleted_paths(root))
    readable_paths = tuple(path for path in paths if path not in deleted)
    files = load_tracked_files(root, readable_paths)
    return scan_tracked_files(files), len(readable_paths)


def main(root: Path = ROOT) -> int:
    try:
        findings, tracked_count = scan_repository(root)
    except ScannerError as error:
        print(f"PROHIBITED FILE SCAN ERROR: {error}", file=sys.stderr)
        return 2

    if findings:
        print("PROHIBITED FILE SCAN FAIL", file=sys.stderr)
        for finding in findings:
            print(f"- {finding.path}: {finding.rule}", file=sys.stderr)
        return 1

    print(f"PROHIBITED FILE SCAN PASS ({tracked_count} tracked files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
