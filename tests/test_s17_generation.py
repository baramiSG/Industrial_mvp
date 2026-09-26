from __future__ import annotations

import hashlib
import json

import pytest

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
    assert len(json.loads(snapshot_manifest.read_text(encoding="utf-8"))["files"]) == 734
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
        assert public["active_decision"] == public["real_decision"]
        assert simulated["active_decision"] == simulated["simulation_decision"]
        assert simulated["real_decision"]["state"] == public_state


_PROFILE_GATES = {
    "S": [
        "substrate_range",
        "width_thickness_envelope",
        "coating_route_and_mass",
        "surface_treatment",
        "mandatory_or_customer_standard",
    ],
    "P": [
        "polymer_additive_compatibility",
        "conversion_route",
        "tooling",
        "performance_requirement",
        "application_qualification",
    ],
    "F": [
        "feedstock_route",
        "formulation_granulation",
        "nutrient_basis",
        "agronomic_performance",
        "emissions_and_safe_handling",
    ],
    "A": [
        "alloy",
        "forming_fabrication",
        "heat_treatment",
        "joining_finishing",
        "engineering_certification",
        "customer_liability",
    ],
    "H": [
        "named_molecule_and_synthesis_route",
        "gmp",
        "containment",
        "impurity_control",
        "analytical_validation",
        "effluent",
        "ip_fto",
    ],
}
_S0 = [
    *_PROFILE_GATES["S"],
    "exact imported specification",
    "customer/application qualification",
    "effective spare capacity and allocation",
]
_P0 = [
    *_PROFILE_GATES["P"],
    "named imported grade",
    "buyer application and qualification",
    "local grade availability in required volume and timing",
]
_PUBLIC_UNRESOLVED = {
    "SAU-H0-721049": _S0,
    "SAU-H0-390210": _P0,
    "SAU-H6-294110": _PROFILE_GATES["H"],
    "SAU-H6-294120": _PROFILE_GATES["H"],
    "SAU-H6-310430": _PROFILE_GATES["F"],
    "SAU-H6-310510": _PROFILE_GATES["F"],
    "SAU-H6-392010": _PROFILE_GATES["P"],
    "SAU-H6-721012": _PROFILE_GATES["S"],
    "SAU-H6-721061": _PROFILE_GATES["S"],
    "SAU-H6-760429": _PROFILE_GATES["A"],
    "SAU-H6-760711": _PROFILE_GATES["A"],
}


def test_ordered_22_branch_gate_lists_and_decision_equality() -> None:
    assert len(_PUBLIC_UNRESOLVED) == 11
    for opportunity_id, public_names in _PUBLIC_UNRESOLVED.items():
        public = analyze(opportunity_id, "public")
        simulated = analyze(opportunity_id, "simulated")
        assert public["capability"]["unresolved_hard_gates"] == public_names
        assert simulated["capability"]["unresolved_hard_gates"] == []
        assert public["capability"]["known_hard_gate_failures"] == []
        if opportunity_id == "SAU-H6-294120":
            assert simulated["capability"]["known_hard_gate_failures"] == [
                "effluent"
            ]
        else:
            assert simulated["capability"]["known_hard_gate_failures"] == []
        assert simulated["real_decision"] == public["real_decision"]
        assert public["active_decision"] == public["real_decision"]
        assert simulated["active_decision"] == simulated["simulation_decision"]
        assert public["economics"] is None
        if opportunity_id == "SAU-H0-721049":
            assert simulated["economics"]["minimum_effective_support_m"] == (
                pytest.approx(18.0)
            )
        if opportunity_id == "SAU-H0-390210":
            assert simulated["simulation_decision"]["state"] == "REJECT"
            assert simulated["simulation_decision"]["route_code"] == 0
