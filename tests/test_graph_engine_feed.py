from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.artifact import load_projection
from ior_mvp.graph.engine_feed import (
    adjacency_explanation,
    evidence_linkage,
    route_blocking_capability,
    shared_enabler_inputs,
    shared_enabler_queue_rows,
)
from ior_mvp.graph.model import GraphEdge, GraphNode
from ior_mvp.graph.projection import GraphProjection


@pytest.fixture(scope="module")
def projection() -> GraphProjection:
    return load_projection(PROJECT_ROOT / "data/graph")


def _props(
    identity: str,
    *,
    synthetic: bool,
    scenario_id: str,
    derived: bool = False,
) -> dict:
    values = {
        "id": identity,
        "evidence_id": f"E-{identity}",
        "as_of": "2026-01-01",
        "evidence_class": "D" if synthetic else "B",
        "synthetic_flag": synthetic,
        "scenario_id": scenario_id,
        "origin_kind": "SCENARIO" if synthetic else "PUBLIC_SNAPSHOT",
        "origin_ref": scenario_id,
        "derived": derived,
        "projection_id": "GRAPH-TEST",
        "evidence_ids": [f"E-{identity}"],
    }
    if synthetic:
        values["display_label"] = "SIMULATED — NOT MINISTRY EVIDENCE"
        values["display_label_ar"] = (
            "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"
        )
    if derived:
        values["engine_run_id"] = "ENGINE-TEST"
    return values


def _enabler_projection(*, derived_edge: bool = False) -> GraphProjection:
    enabler = _props(
        "ENABLER-SYN-TEST-001",
        synthetic=True,
        scenario_id="SYN-A",
    )
    enabler.update(
        {
            "kind": "shared_enabler",
            "enabler_kind": "shared_laboratory",
            "enabler_cost_m_sar": 10.0,
            "components": {
                "technical_feasibility_confirmed": True,
            },
            "scenario_ids": ["SYN-A", "SYN-B"],
        }
    )
    nodes = [
        GraphNode(
            "Product",
            "P-A",
            _props("P-A", synthetic=False, scenario_id="PUBLIC"),
        ),
        GraphNode(
            "Product",
            "P-B",
            _props("P-B", synthetic=False, scenario_id="PUBLIC"),
        ),
        GraphNode("Intervention", "ENABLER-SYN-TEST-001", enabler),
    ]
    edges = []
    for product, scenario, probability, value, share in (
        ("P-A", "SYN-A", 0.5, 100.0, 0.5),
        ("P-B", "SYN-B", 0.8, 50.0, 0.5),
    ):
        props = _props(
            f"REL-{product}",
            synthetic=True,
            scenario_id=scenario,
            derived=derived_edge,
        )
        props["key"] = f"REL-{product}"
        props.update(
            {
                "unlock_probability": probability,
                "dependent_incremental_national_value_m_sar": value,
                "dependency_share": share,
                "constraint_classes_addressed": [
                    "capacity_or_availability"
                ],
                "removes_binding_constraint": True,
            }
        )
        edges.append(
            GraphEdge(
                "UNLOCKED_BY",
                product,
                "ENABLER-SYN-TEST-001",
                f"REL-{product}",
                props,
            )
        )
    graph = GraphProjection(
        projection_id="GRAPH-TEST",
        as_of="2026-01-01",
        inputs=[],
        engine={"engine_run_id": "ENGINE-TEST"},
        nodes=nodes,
        edges=edges,
    )
    graph.refresh_counts()
    return graph


def test_shared_enabler_inputs_none_without_edges(
    projection: GraphProjection,
) -> None:
    assert shared_enabler_inputs(projection, "SAU-H0-721049", branch="public") is None


def test_shared_enabler_inputs_public_branch_ignores_synthetic_edges() -> None:
    graph = _enabler_projection()
    assert shared_enabler_inputs(graph, "P-A", branch="public") is None


def test_shared_enabler_inputs_sorted_dependents_and_contract_fields() -> None:
    graph = _enabler_projection()
    result = shared_enabler_inputs(
        graph,
        "P-A",
        branch=("simulated", "SYN-A"),
    )
    assert result is not None
    assert result["enabler_id"] == "ENABLER-SYN-TEST-001"
    assert result["dependent_opportunity_ids"] == ["P-A", "P-B"]
    assert result["unlock_probabilities"] == [0.5, 0.8]
    assert result["dependent_incremental_national_values_m_sar"] == [
        100.0,
        50.0,
    ]
    assert result["dependency_shares"] == [0.5, 0.5]
    assert result["enabler_cost_m_sar"] == 10.0
    assert result["graph_projection_id"] == "GRAPH-TEST"


def test_feed_ignores_derived_elements() -> None:
    assert (
        shared_enabler_inputs(
            _enabler_projection(derived_edge=True),
            "P-A",
            branch=("simulated", "SYN-A"),
        )
        is None
    )


def test_adjacency_explanation_matches_r9s_ledger_for_all_cases_both_modes(
    projection: GraphProjection,
) -> None:
    products = sorted(
        node.id for node in projection.nodes if node.label == "Product"
    )
    for opportunity_id in products:
        result = adjacency_explanation(
            projection,
            opportunity_id,
            branch="public",
        )
        assert result["opportunity_id"] == opportunity_id
        assert isinstance(result["producer_ids"], list)
        if result["producer_ids"]:
            assert isinstance(result["fired"], (bool, type(None)))
            assert isinstance(result["qualifying_signal_count"], int)
    scenarios = {
        node.properties["opportunity_id"]: node.id
        for node in projection.nodes
        if node.label == "Scenario"
    }
    for opportunity_id, scenario_id in scenarios.items():
        result = adjacency_explanation(
            projection,
            opportunity_id,
            branch=("simulated", scenario_id),
        )
        assert result["mode"] == "simulated"
        assert result["scenario_id"] == scenario_id


def test_route_blocking_matches_route_reason_codes_and_capability_states(
    projection: GraphProjection,
) -> None:
    rows = route_blocking_capability(
        projection,
        "SAU-H0-721049",
        branch="public",
    )
    route_nodes = {
        node.properties["route_code"]: node
        for node in projection.nodes
        if node.label == "Intervention"
        and node.properties.get("opportunity_id") == "SAU-H0-721049"
        and node.properties.get("mode") == "public"
    }
    for row in rows:
        assert row["reason_code"] in route_nodes[row["route_code"]].properties[
            "reason_codes"
        ]
        assert row["capability_id"].startswith("CAP-")


def test_evidence_linkage_matches_evidence_needs(
    projection: GraphProjection,
) -> None:
    rows = evidence_linkage(
        projection,
        "SAU-H0-721049",
        branch="public",
    )
    assert rows
    assert all(row["need_code"] and row["blocked_field"] for row in rows)
    assert rows == sorted(
        rows,
        key=lambda row: (
            row["need_code"],
            row["variant"],
            row["target_id"],
        ),
    )


def test_shared_enabler_queue_rows_public_empty_and_simulated_aggregation(
    projection: GraphProjection,
) -> None:
    assert shared_enabler_queue_rows(projection, branch="public") == []
    graph = _enabler_projection()
    rows = shared_enabler_queue_rows(
        graph,
        branch=("simulated", "SYN-A"),
    )
    assert len(rows) == 1
    assert rows[0]["dependent_opportunity_ids"] == ["P-A", "P-B"]
    assert rows[0]["unlock_value_m_sar"] == pytest.approx(35.0)
