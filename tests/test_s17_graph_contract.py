from __future__ import annotations

import json
from copy import deepcopy
from types import SimpleNamespace

import pytest
import yaml

from browser_tests.graph_fixtures import (
    adapt_no_candidate_expected,
    artifact_graph_payload,
    graph_catalogue_fixture,
    route_blocking_fixture,
)
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.decision_engine import analyze, list_opportunities
from ior_mvp.evidence import synthetic_display_labels
from ior_mvp.genui import build_ui_manifest
from ior_mvp.graph.model import GraphEdge, GraphNode
from ior_mvp.graph.projection import GraphProjection
from ior_mvp.graph.service import GraphService


def test_graph_descriptor_is_last_and_preserves_manifest_version() -> None:
    for mode in ("public", "simulated"):
        analysis = analyze("SAU-H0-721049", mode)
        manifest = build_ui_manifest(analysis)
        assert manifest["manifest_version"] == "1.0"
        assert [row["type"] for row in manifest["components"]][-2:] == [
            "decision_actions",
            "graph_view",
        ]
        assert manifest["components"][-1] == {
            "type": "graph_view",
            "id": "graph-view",
            "props": {
                "opportunity_id": "SAU-H0-721049",
                "mode": mode,
            },
        }


def test_graph_catalogue_and_fixture_payloads_cover_four_fixed_views() -> None:
    catalogue = graph_catalogue_fixture()
    assert catalogue["metadata"]["version"] == "1.0.0"
    assert [row["view_id"] for row in catalogue["views"]] == [
        "adjacency",
        "route_blocking",
        "shared_enabler",
        "evidence_to_change",
    ]
    for view_id in ("adjacency", "route_blocking", "evidence_to_change"):
        payload = artifact_graph_payload(view_id, "SAU-H0-721049", "public")
        assert payload["view_id"] == view_id
        assert payload["mode"] == "public"
        assert all(
            row["provenance"]["synthetic_flag"] is False
            for row in [*payload["nodes"], *payload["edges"]]
        )
    shared = artifact_graph_payload(
        "shared_enabler", "SAU-H6-760711", "simulated"
    )
    assert shared["graph_status"] == "AVAILABLE"
    assert shared["synthetic_flag"] is True


def test_route_blocking_fixture_is_only_test_class_d_nonempty_payload() -> None:
    payload = route_blocking_fixture("SAU-H0-721049")
    assert payload["mode"] == "simulated"
    assert payload["synthetic_flag"] is True
    assert payload["edges"]
    synthetic = [
        row for row in [*payload["nodes"], *payload["edges"]]
        if row["provenance"]["synthetic_flag"]
    ]
    assert synthetic
    assert all(row["provenance"]["evidence_class"] == "D" for row in synthetic)
    assert all(set(row["display_labels"]) == {"en", "ar"} for row in synthetic)


def test_no_candidate_adaptation_is_guarded_and_does_not_mutate_history() -> None:
    path = (
        PROJECT_ROOT
        / "tests/fixtures/public_decision/no-candidate-no-fired-signal.expected.json"
    )
    original = json.loads(path.read_text(encoding="utf-8"))
    before = deepcopy(original)
    adapted = adapt_no_candidate_expected(original)
    assert original == before
    assert adapted["ui_manifest"]["components"][-1]["type"] == "graph_view"
    broken = deepcopy(original)
    broken["ui_manifest"]["components"][-1]["type"] = "metric_grid"
    with pytest.raises(AssertionError):
        adapt_no_candidate_expected(broken)


def test_ui_catalogue_1_5_has_graph_parity_without_policy_label_duplication() -> None:
    payload = yaml.safe_load(
        (PROJECT_ROOT / "config/ui_strings.v1.yaml").read_text(encoding="utf-8")
    )
    assert payload["metadata"]["version"] == "1.5.0"
    assert payload["metadata"]["effective_date"] == "2026-09-16"
    english = payload["strings"]["en"]
    arabic = payload["strings"]["ar"]
    graph_keys = {key for key in english if key.startswith("graph.")}
    assert graph_keys == {key for key in arabic if key.startswith("graph.")}
    assert len({key for key in graph_keys if key.startswith("graph.node.")}) == 19
    assert len({key for key in graph_keys if key.startswith("graph.edge.")}) == 15
    policy = yaml.safe_load(
        (PROJECT_ROOT / "config/evidence_policy.v1.yaml").read_text(encoding="utf-8")
    )["synthetic_isolation"]
    assert policy["display_label"] not in english.values()
    assert policy["display_label_ar"] not in arabic.values()


def test_all_public_graph_views_are_public_for_all_opportunities() -> None:
    view_ids = [row["view_id"] for row in graph_catalogue_fixture()["views"]]
    for opportunity in list_opportunities("public"):
        for view_id in view_ids:
            payload = artifact_graph_payload(view_id, opportunity["id"], "public")
            elements = [*payload["nodes"], *payload["edges"]]
            assert payload["graph_status"] == "AVAILABLE"
            assert payload["synthetic_flag"] is False
            assert payload["display_labels"] is None
            assert all(
                row["provenance"]["synthetic_flag"] is False
                and row["provenance"]["scenario_id"] == "PUBLIC"
                for row in elements
            )


def test_evidence_support_edges_keep_current_branch_and_exclude_other_scenarios() -> None:
    public = artifact_graph_payload(
        "evidence_to_change", "SAU-H0-721049", "public"
    )
    public_support = [
        edge for edge in public["edges"]
        if edge["type"] == "SUPPORTED_BY_EVIDENCE"
    ]
    assert public_support
    assert all(
        edge["provenance"]["synthetic_flag"] is False
        and edge["provenance"]["scenario_id"] == "PUBLIC"
        for edge in public_support
    )
    simulated = artifact_graph_payload(
        "evidence_to_change", "SAU-H0-721049", "simulated"
    )
    allowed = {"PUBLIC", "SYN-MINISTRY-STEEL-001"}
    assert all(
        edge["provenance"]["scenario_id"] in allowed
        for edge in simulated["edges"]
        if edge["type"] == "SUPPORTED_BY_EVIDENCE"
    )


def _provenance(synthetic: bool, scenario_id: str, evidence_id: str) -> dict:
    return {
        "evidence_id": evidence_id,
        "as_of": "2026-09-12",
        "evidence_class": "D" if synthetic else "C",
        "synthetic_flag": synthetic,
        "scenario_id": scenario_id,
        **(
            {
                "display_label": synthetic_display_labels()["en"],
                "display_label_ar": synthetic_display_labels()["ar"],
            }
            if synthetic else {}
        ),
        "derived": False,
    }


def test_edge_only_synthetic_payload_sets_top_flag_and_bilingual_labels() -> None:
    public = _provenance(False, "PUBLIC", "PUBLIC-EVIDENCE")
    synthetic = _provenance(
        True, "SYN-MINISTRY-EDGE-ONLY-001", "SYNTHETIC-EVIDENCE"
    )
    nodes = [
        GraphNode("Product", "EDGE-ONLY-PRODUCT", dict(public)),
        GraphNode(
            "Scenario",
            "SYN-MINISTRY-EDGE-ONLY-001",
            {
                **synthetic,
                "opportunity_id": "EDGE-ONLY-PRODUCT",
            },
        ),
        GraphNode("Decision", "EDGE-ONLY-DECISION", dict(public)),
        GraphNode("Evidence", "EDGE-ONLY-NEED", dict(public)),
        GraphNode("Evidence", "EDGE-ONLY-PASSPORT", dict(public)),
    ]
    edges = [
        GraphEdge(
            "CONSTRAINED_BY",
            "EDGE-ONLY-DECISION",
            "EDGE-ONLY-NEED",
            "EDGE-ONLY-CONSTRAINT",
            {**public, "need_code": "TEST-NEED"},
        ),
        GraphEdge(
            "SUPPORTED_BY_EVIDENCE",
            "EDGE-ONLY-NEED",
            "EDGE-ONLY-PASSPORT",
            "EDGE-ONLY-SUPPORT",
            synthetic,
        ),
    ]
    projection = GraphProjection(
        projection_id="GRAPH-SAU-2026-09-12-edgeonly",
        as_of="2026-09-12",
        inputs=[],
        engine={},
        nodes=nodes,
        edges=edges,
    )
    service = GraphService(
        SimpleNamespace(target="fixture"),
        artifact_projection_id=projection.projection_id,
        projection=projection,
        status_reader=lambda _spec: {
            "projection_id": projection.projection_id,
            "counts": {},
            "synthetic_partition": {},
        },
        view_reader=lambda *_args: [
            {
                "decision_id": "EDGE-ONLY-DECISION",
                "target_id": "EDGE-ONLY-NEED",
                "need_code": "TEST-NEED",
                "evidence_ids": ["EDGE-ONLY-PASSPORT"],
            }
        ],
    )
    payload = service.view(
        "evidence_to_change", "EDGE-ONLY-PRODUCT", "simulated"
    )
    assert not any(node["provenance"]["synthetic_flag"] for node in payload["nodes"])
    assert any(edge["provenance"]["synthetic_flag"] for edge in payload["edges"])
    assert payload["synthetic_flag"] is True
    assert payload["display_labels"] == synthetic_display_labels()


def test_shared_enabler_preserves_both_aluminium_dependency_edges() -> None:
    for opportunity_id in ("SAU-H6-760711", "SAU-H6-760429"):
        payload = artifact_graph_payload(
            "shared_enabler", opportunity_id, "simulated"
        )
        unlocked = [
            edge for edge in payload["edges"] if edge["type"] == "UNLOCKED_BY"
        ]
        assert {edge["source"] for edge in unlocked} == {
            "SAU-H6-760711",
            "SAU-H6-760429",
        }


def test_route_blocking_fixture_product_matches_actual_public_serialization() -> None:
    actual = artifact_graph_payload(
        "adjacency", "SAU-H0-721049", "public"
    )
    expected_product = next(
        node for node in actual["nodes"] if node["id"] == "SAU-H0-721049"
    )
    fixture = route_blocking_fixture("SAU-H0-721049")
    fixture_product = next(
        node for node in fixture["nodes"] if node["id"] == "SAU-H0-721049"
    )
    assert fixture_product == expected_product
