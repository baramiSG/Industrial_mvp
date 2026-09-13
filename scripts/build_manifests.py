from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entry(path: Path) -> dict[str, str | int]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
    }


def update_human_authority_table(rows: list[dict[str, str | int]]) -> None:
    path = ROOT / "docs" / "authority" / "00_AUTHORITY_MANIFEST.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    start = "<!-- HASH_TABLE_START -->"
    end = "<!-- HASH_TABLE_END -->"
    table = [
        start,
        "",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | --- |",
        *[
            f"| `{row['path']}` | `{row['sha256']}` | {int(row['bytes']):,} |"
            for row in rows
        ],
        "",
        end,
    ]
    before, remainder = text.split(start, 1)
    _, after = remainder.split(end, 1)
    path.write_text(before + "\n".join(table) + after, encoding="utf-8")


def main() -> None:
    snapshot_paths = sorted((ROOT / "data" / "snapshots").rglob("*.json"))
    snapshot_paths += sorted((ROOT / "data" / "synthetic").rglob("*.json"))
    snapshot_paths += sorted((ROOT / "data" / "golden").glob("*.json"))
    raw_root = ROOT / "data" / "raw"
    if raw_root.exists():
        snapshot_paths += sorted(
            p
            for p in raw_root.rglob("*")
            if p.is_file()
        )
    documents_root = ROOT / "data" / "documents"
    if documents_root.exists():
        snapshot_paths += sorted(
            p for p in documents_root.rglob("*") if p.is_file()
        )
    entities_root = ROOT / "data" / "entities"
    if entities_root.exists():
        snapshot_paths += sorted(
            p for p in entities_root.rglob("*") if p.is_file()
        )
    screening_root = ROOT / "data" / "screening"
    if screening_root.exists():
        snapshot_paths += sorted(
            p for p in screening_root.rglob("*") if p.is_file()
        )
    cases_root = ROOT / "data" / "cases"
    if cases_root.exists():
        snapshot_paths += sorted(
            p for p in cases_root.rglob("*") if p.is_file()
        )
    history_root = ROOT / "config" / "history"
    if history_root.exists():
        snapshot_paths += sorted(
            p for p in history_root.rglob("*") if p.is_file()
        )
    snapshot_manifest = {
        "manifest_version": "1.0",
        "generated_on": str(date.today()),
        "policy": (
            "Golden cases and synthetic scenarios run only against pinned files "
            "in this manifest; case derivation inputs and retained superseded operating-configuration bytes "
            "are also hash-pinned."
        ),
        "files": [entry(path) for path in snapshot_paths],
    }
    (ROOT / "data" / "manifests" / "snapshot_manifest.json").write_text(
        json.dumps(snapshot_manifest, indent=2) + "\n", encoding="utf-8"
    )

    authority_paths = [
        ROOT / "docs" / "authority" / "Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx",
        ROOT / "config" / "thresholds.v1.yaml",
        ROOT / "config" / "sector_profiles.v1.yaml",
        ROOT / "config" / "evidence_policy.v1.yaml",
        ROOT / "config" / "ui_strings.v1.yaml",
        ROOT / "config" / "decision_narratives.v1.yaml",
        ROOT / "config" / "acquisition_sources.v1.yaml",
        ROOT / "config" / "entity_resolution.v1.yaml",
        ROOT / "config" / "screening.v1.yaml",
        ROOT / "config" / "product_families.v1.yaml",
    ]
    authority_paths += sorted((ROOT / "docs" / "core").glob("*.md"))
    authority_manifest = {
        "manifest_version": "1.0",
        "generated_on": str(date.today()),
        "files": [entry(path) for path in authority_paths if path.exists()],
    }
    (ROOT / "docs" / "authority" / "authority_hashes.json").write_text(
        json.dumps(authority_manifest, indent=2) + "\n", encoding="utf-8"
    )
    update_human_authority_table(authority_manifest["files"])


if __name__ == "__main__":
    main()
