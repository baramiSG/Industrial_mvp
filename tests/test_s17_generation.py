from __future__ import annotations

import hashlib
import json

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.decision_engine import analyze
from ior_mvp.graph.projection import build_repository_projection, discover_inputs


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_ui_history_is_exact_1_4_0_preimage() -> None:
    current = PROJECT_ROOT / "config/ui_strings.v1.yaml"
    history = PROJECT_ROOT / "config/history/ui_strings.v1-1.4.0.yaml"
    assert _sha256(history) == (
        "984290f6b6771d54d987a188987a6a50d404984a2c58ef3d32e0d4306de3d432"
    )
    assert history.stat().st_size == 63529
    assert _sha256(current) != _sha256(history)


def test_graph_inputs_include_s17_sources_without_generated_manifest_cycle() -> None:
    paths = {row["path"] for row in discover_inputs(PROJECT_ROOT)}
    assert {
        "config/ui_strings.v1.yaml",
        "docs/core/02_METHODOLOGY_IMPLEMENTATION_MAP.md",
        "docs/core/03_SYSTEM_ARCHITECTURE.md",
        "docs/core/09_TEST_ACCEPTANCE_AND_GOLDEN_CASES.md",
        "src/ior_mvp/config.py",
        "src/ior_mvp/genui.py",
    } <= paths
    assert "data/manifests/snapshot_manifest.json" not in paths
    assert "docs/authority/authority_hashes.json" not in paths


def test_in_memory_g17_is_deterministic_and_writes_nothing() -> None:
    current_path = PROJECT_ROOT / "data/graph/current.json"
    snapshot_manifest = PROJECT_ROOT / "data/manifests/snapshot_manifest.json"
    authority_manifest = PROJECT_ROOT / "docs/authority/authority_hashes.json"
    before = {
        path: path.read_bytes()
        for path in (current_path, snapshot_manifest, authority_manifest)
    }
    first = build_repository_projection(PROJECT_ROOT)
    second = build_repository_projection(PROJECT_ROOT)
    assert first == second
    assert first.projection_id == second.projection_id
    assert first.projection_id.startswith("GRAPH-SAU-2026-09-12-")
    assert first.projection_id == json.loads(
        current_path.read_text(encoding="utf-8")
    )["projection_id"]
    assert first.counts["nodes"] == 925
    assert first.counts["edges"] == 1045
    assert all(path.read_bytes() == content for path, content in before.items())
    assert len(json.loads(snapshot_manifest.read_text(encoding="utf-8"))["files"]) == 726
    assert len(json.loads(authority_manifest.read_text(encoding="utf-8"))["files"]) == 20
    print(
        "S17_IN_MEMORY_G17",
        first.projection_id,
        first.counts["nodes"],
        first.counts["edges"],
    )


def test_all_eleven_public_and_simulated_outcomes_remain_unchanged() -> None:
    expected = {
        "SAU-H0-721049": ("INVESTIGATE", "ADVANCE", 5),
        "SAU-H0-390210": ("REJECT", "REJECT", 0),
        "SAU-H6-721061": ("INVESTIGATE", "ADVANCE", 3),
        "SAU-H6-721012": ("INVESTIGATE", "ADVANCE", 7),
        "SAU-H6-760711": ("INVESTIGATE", "ADVANCE", 6),
        "SAU-H6-760429": ("INVESTIGATE", "ADVANCE", 4),
        "SAU-H6-392010": ("INVESTIGATE", "REJECT", 0),
        "SAU-H6-294110": ("INVESTIGATE", "ADVANCE", 1),
        "SAU-H6-294120": ("INVESTIGATE", "REJECT", 0),
        "SAU-H6-310430": ("INVESTIGATE", "ADVANCE", 2),
        "SAU-H6-310510": ("INVESTIGATE", "REJECT", 0),
    }
    for opportunity_id, (public_state, simulated_state, route) in expected.items():
        public = analyze(opportunity_id, "public")
        simulated = analyze(opportunity_id, "simulated")
        assert public["real_decision"]["state"] == public_state
        assert simulated["real_decision"] == public["real_decision"]
        assert simulated["simulation_decision"]["state"] == simulated_state
        assert simulated["simulation_decision"]["route_code"] == route
