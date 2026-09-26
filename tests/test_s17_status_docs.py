from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_s17_status_distinguishes_completed_generation_from_f01_visual_refresh() -> (
    None
):
    architecture = (PROJECT_ROOT / "docs" / "ARCHITECTURE_DECISIONS.md").read_text(
        encoding="utf-8"
    )
    adr_027 = architecture.split("## ADR-027", maxsplit=1)[1]
    progress = (PROJECT_ROOT / "docs" / "BUILD_PROGRESS.md").read_text(encoding="utf-8")
    s17_row = next(
        line
        for line in progress.splitlines()
        if line.startswith("| S17 Interactive graph view |")
    )
    snapshot = json.loads(
        (PROJECT_ROOT / "data" / "manifests" / "snapshot_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    visual = json.loads(
        (
            PROJECT_ROOT / "browser_tests" / "baselines" / "v0.3.0" / "manifest.json"
        ).read_text(encoding="utf-8")
    )

    assert len(snapshot["files"]) == 734
    assert len(visual["entries"]) == 128
    assert visual["change_ref"] == "MINISTRY-F-GATE-PROVENANCE-2"
    for text in (adr_027, s17_row):
        assert "GRAPH-SAU-2026-09-12-b63159c7bdc1" in text
        assert "722" in text
        assert "112" in text
        assert "must not replay" in text
        assert "did not replay" in text
        assert "F01" in text
        assert "visual source provenance" in text
        assert "S17-FINAL-REVIEW-R1" in text
        assert "byte-identical" in text
        assert "zero WebP changes" in text
        assert "separate owner authorization" not in text
    assert "generated artifacts, independent implementation review" not in adr_027
    assert "Until those allocations run" not in adr_027
    assert "generated inputs intentionally stale" not in s17_row
