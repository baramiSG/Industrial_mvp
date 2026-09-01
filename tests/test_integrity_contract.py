from __future__ import annotations

import json
from pathlib import Path

from ior_mvp.config import PROJECT_ROOT


def test_manifests_exist_and_track_expected_files() -> None:
    snapshot_manifest = PROJECT_ROOT / "data" / "manifests" / "snapshot_manifest.json"
    authority_manifest = PROJECT_ROOT / "docs" / "authority" / "authority_hashes.json"
    assert snapshot_manifest.exists()
    assert authority_manifest.exists()

    snapshots = json.loads(snapshot_manifest.read_text(encoding="utf-8"))
    authorities = json.loads(authority_manifest.read_text(encoding="utf-8"))
    snapshot_paths = {item["path"] for item in snapshots["files"]}
    authority_paths = {item["path"] for item in authorities["files"]}

    assert "data/snapshots/public/SAU-H0-721049.json" in snapshot_paths
    assert "data/snapshots/public/SAU-H0-390210.json" in snapshot_paths
    assert "data/synthetic/SYN-MINISTRY-STEEL-001.json" in snapshot_paths
    assert "docs/authority/Industrial_Opportunity_Resolution_Methodology_Final_KSA.docx" in authority_paths
    assert "config/thresholds.v1.yaml" in authority_paths
