"""Offline CaseBrief loader and PublicSnapshot builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ior_mvp.config import PROJECT_ROOT

from .brief import UNAVAILABLE, load_case_brief
from .projection import build_public_snapshot, canonical_bytes


def _load_by_id(root: Path, directory: Path, identity: str) -> dict[str, Any]:
    for path in sorted(directory.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("snapshot_id") == identity:
            return record
    raise ValueError(f"snapshot not found: {identity}")


def _documents(
    root: Path, document_ids: set[str]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "data" / "documents").glob("*/records/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        document_id = record.get("document_id")
        if document_id in document_ids:
            result[str(document_id)] = record
    if set(result) != document_ids:
        raise ValueError("CaseBrief document input missing")
    return result


def build_from_brief(
    brief_path: Path,
    *,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Build one snapshot in memory from a validated CaseBrief."""
    brief = load_case_brief(brief_path, root=root)
    universe = _load_by_id(
        root,
        root / "data" / "snapshots" / "universe",
        brief["universe_snapshot_id"],
    )
    partners = (
        None
        if brief["partner_snapshot_id"] == UNAVAILABLE
        else _load_by_id(
            root,
            root / "data" / "snapshots" / "partners",
            brief["partner_snapshot_id"],
        )
    )
    documents = _documents(
        root,
        {
            row["document_id"]
            for row in brief["document_evidence"]
        },
    )
    return build_public_snapshot(
        brief,
        universe,
        partners=partners,
        documents=documents,
        root=root,
    )


def write_built_snapshot(record: dict[str, Any], out_dir: Path) -> Path:
    """Write a canonical derived snapshot without overwriting a conflict."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{record['snapshot_id']}.json"
    content = canonical_bytes(record)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("built snapshot write conflict")
        return path
    path.write_bytes(content)
    return path


def build_brief_to_directory(
    brief_path: Path,
    out_dir: Path,
    *,
    root: Path = PROJECT_ROOT,
) -> Path:
    """Build, validate, and write one temporary PublicSnapshot."""
    return write_built_snapshot(
        build_from_brief(brief_path, root=root),
        out_dir,
    )


def reconstruct_briefs(
    *,
    root: Path = PROJECT_ROOT,
) -> tuple[int, int]:
    """Validate all briefs and compare any committed derived snapshots."""
    paths = sorted(
        (root / "data" / "cases" / "briefs").glob("CASE-BRIEF-*.json")
    )
    committed = 0
    for path in paths:
        snapshot = build_from_brief(path, root=root)
        candidates = (
            root
            / "data"
            / "snapshots"
            / "public"
            / f"{snapshot['opportunity']['id']}.json",
            root
            / "data"
            / "snapshots"
            / "public"
            / f"{snapshot['snapshot_id']}.json",
        )
        committed_path = next(
            (candidate for candidate in candidates if candidate.exists()),
            None,
        )
        if committed_path is None:
            continue
        committed += 1
        if committed_path.read_bytes() != canonical_bytes(snapshot):
            raise ValueError(
                f"case snapshot byte mismatch: {snapshot['snapshot_id']}"
            )
    return committed, len(paths)
