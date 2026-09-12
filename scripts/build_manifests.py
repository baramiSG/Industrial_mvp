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
    snapshot_manifest = {
        "manifest_version": "1.0",
        "generated_on": str(date.today()),
        "policy": "Golden cases and synthetic scenarios run only against pinned files in this manifest.",
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


if __name__ == "__main__":
    main()
