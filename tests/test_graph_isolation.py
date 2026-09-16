from __future__ import annotations

from copy import deepcopy

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.decision_engine import analyze, analyze_public
from ior_mvp.graph.artifact import load_projection
from ior_mvp.graph.engine_feed import (
    adjacency_explanation,
    evidence_linkage,
    route_blocking_capability,
    shared_enabler_inputs,
)


def _projection():
    return load_projection(PROJECT_ROOT / "data/graph")


def _fingerprint(decision: dict) -> dict:
    return {
        key: deepcopy(decision.get(key))
        for key in ("state", "route_code", "headline", "missing_facts")
    }


def test_public_graph_payloads_have_no_synthetic_marker_and_scenario_id_public_only() -> None:
    projection = _projection()
    public_nodes = [
        node for node in projection.nodes if not node.properties["synthetic_flag"]
    ]
    public_edges = [
        edge for edge in projection.edges if not edge.properties["synthetic_flag"]
    ]
    assert public_nodes and public_edges
    assert all(node.properties["scenario_id"] == "PUBLIC" for node in public_nodes)
    assert all(edge.properties["scenario_id"] == "PUBLIC" for edge in public_edges)
    serialized = str(
        [
            node.properties
            for node in public_nodes
        ]
        + [edge.properties for edge in public_edges]
    )
    assert "SIMULATED — NOT MINISTRY EVIDENCE" not in serialized
    assert "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة" not in serialized


def test_projection_public_edges_never_end_at_synthetic_nodes() -> None:
    projection = _projection()
    nodes = {node.id: node for node in projection.nodes}
    for edge in projection.edges:
        if edge.properties["synthetic_flag"] is False:
            assert nodes[edge.source].properties["synthetic_flag"] is False
            assert nodes[edge.target].properties["synthetic_flag"] is False


def test_public_engine_feeds_ignore_class_d_edges() -> None:
    projection = _projection()
    products = sorted(
        node.id for node in projection.nodes if node.label == "Product"
    )
    for opportunity_id in products:
        assert (
            shared_enabler_inputs(
                projection,
                opportunity_id,
                branch="public",
            )
            is None
        )
        for result in (
            adjacency_explanation(
                projection,
                opportunity_id,
                branch="public",
            ),
            route_blocking_capability(
                projection,
                opportunity_id,
                branch="public",
            ),
            evidence_linkage(
                projection,
                opportunity_id,
                branch="public",
            ),
        ):
            assert "SIMULATED — NOT MINISTRY EVIDENCE" not in str(result)


def test_real_decision_fingerprint_unchanged_for_all_cases_after_simulation_with_graph(
    s16b_graph_cache,
) -> None:
    projection = s16b_graph_cache
    scenario_opportunities = sorted(
        node.properties["opportunity_id"]
        for node in projection.nodes
        if node.label == "Scenario"
    )
    for opportunity_id in scenario_opportunities:
        before = _fingerprint(analyze_public(opportunity_id)["real_decision"])
        simulated = analyze(opportunity_id, "simulated")
        after = _fingerprint(simulated["real_decision"])
        assert after == before
