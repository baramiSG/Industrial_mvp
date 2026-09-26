from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.artifact import load_projection
from ior_mvp.graph.cypher import VIEW_QUERIES
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
            "label_en": "Test enabler",
            "label_ar": "عامل تمكين اختباري",
        }
    )
    scenario_a = _props("SYN-A", synthetic=True, scenario_id="SYN-A")
    scenario_a["opportunity_id"] = "P-A"
    scenario_b = _props("SYN-B", synthetic=True, scenario_id="SYN-B")
    scenario_b["opportunity_id"] = "P-B"
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
        GraphNode("Scenario", "SYN-A", scenario_a),
        GraphNode("Scenario", "SYN-B", scenario_b),
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
                "valuation_route_code": 6 if scenario == "SYN-A" else 4,
                "valuation_input_reference": (
                    "synthetic_inputs.route_evidence"
                    f"[route_code={6 if scenario == 'SYN-A' else 4}].national_value"
                ),
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


def test_evidence_linkage_broad_needs_keep_sources_and_skip_sorted_capability() -> None:
    from tests.test_graph_projection import project_sorted_capability_needs

    projected = project_sorted_capability_needs()
    rows = evidence_linkage(projected, "SAU-TEST", branch="public")
    by_field = {row["blocked_field"]: row for row in rows}
    assert by_field["domestic_supply_or_capability"]["target_id"] == "SAU-TEST"
    assert by_field["hard_regulatory_or_process_gate"]["target_id"] == "SAU-TEST"
    assert by_field["idle_equivalent_domestic_capacity"]["target_id"] == "SAU-TEST"
    assert all(
        "capacity_time_window" not in row["target_id"] for row in rows
    )
    assert by_field["target_specification"]["target_id"] == "SPEC-SAU-TEST-TARGET"
    assert by_field["economics"]["target_id"] == "INT-SAU-TEST-route-5"
    assert by_field["domestic_supply_or_capability"]["evidence_ids"] == [
        "E-NEED-SUPPLY"
    ]


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


def test_s16b_shared_enabler_queue_excludes_zero_probability_and_share() -> None:
    zero_probability = _enabler_projection()
    edge_a = next(edge for edge in zero_probability.edges if edge.source == "P-A")
    edge_a.properties["unlock_probability"] = 0.0
    probability_rows = shared_enabler_queue_rows(
        zero_probability,
        branch=("simulated", "SYN-A"),
    )
    assert probability_rows[0]["dependent_opportunity_ids"] == ["P-B"]
    assert probability_rows[0]["counted_dependents"] == 1
    assert probability_rows[0]["unlock_value_m_sar"] == pytest.approx(10.0)

    zero_share = _enabler_projection()
    edge_b = next(edge for edge in zero_share.edges if edge.source == "P-B")
    edge_b.properties["dependency_share"] = 0.0
    share_rows = shared_enabler_queue_rows(
        zero_share,
        branch=("simulated", "SYN-A"),
    )
    assert share_rows[0]["dependent_opportunity_ids"] == ["P-A"]
    assert share_rows[0]["counted_dependents"] == 1
    assert share_rows[0]["unlock_value_m_sar"] == pytest.approx(15.0)


def test_s16b_shared_enabler_query_requires_declared_membership_and_nonderived_inputs() -> None:
    query = VIEW_QUERIES["shared_enabler"]
    assert "dependent.derived = false" in query
    assert "unlock.derived = false" in query
    assert "enabler.derived = false" in query
    assert "unlock.unlock_probability > 0" in query
    assert "unlock.dependency_share > 0" in query
    assert "unlock.dependent_incremental_national_value_m_sar > 0" in query
    assert "unlock.evidence_class = 'D'" in query
    assert "enabler.evidence_class = 'D'" in query
    assert "EXISTS {" in query
    assert "membership.opportunity_id = dependent.id" in query


def test_s16b_shared_enabler_feed_rejects_membership_and_derived_taint() -> None:
    membership = _enabler_projection()
    scenario = next(node for node in membership.nodes if node.id == "SYN-B")
    scenario.properties["opportunity_id"] = "P-A"
    with pytest.raises(ValueError, match="membership"):
        shared_enabler_inputs(
            membership,
            "P-A",
            branch=("simulated", "SYN-A"),
        )
    derived = _enabler_projection()
    enabler = next(
        node for node in derived.nodes if node.id == "ENABLER-SYN-TEST-001"
    )
    enabler.properties["derived"] = True
    with pytest.raises(ValueError, match="node is invalid"):
        shared_enabler_inputs(
            derived,
            "P-A",
            branch=("simulated", "SYN-A"),
        )
