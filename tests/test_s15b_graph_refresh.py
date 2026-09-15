from __future__ import annotations

import pytest

from ior_mvp.config import DATA_DIR
from ior_mvp.data_repository import get_public_case, get_synthetic_scenario
from ior_mvp.graph.artifact import load_projection
from ior_mvp.graph.projection import _simulated_analysis


@pytest.mark.parametrize(
    ("opportunity_id", "state", "route"),
    [
        ("SAU-H6-294110", "ADVANCE", 1),
        ("SAU-H6-294120", "REJECT", 0),
        ("SAU-H6-310430", "ADVANCE", 2),
        ("SAU-H6-310510", "REJECT", 0),
    ],
)
def test_s15b_graph_wrapper_accepts_absent_evsi_without_inventing_estimates(
    opportunity_id: str,
    state: str,
    route: int,
) -> None:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None

    result = _simulated_analysis(get_public_case(opportunity_id), scenario)

    assert result["decision"]["state"] == state
    assert result["decision"]["route_code"] == route
    assert result["scenario_id"] == scenario["scenario_id"]
    assert result["evidence_needs"]
    assert all(
        row["numeric_evsi"] == "NOT_CALCULABLE"
        for row in result["evidence_needs"]
    )


def test_s15b_final_graph_covers_all_public_cases_and_scenarios() -> None:
    projection = load_projection(DATA_DIR / "graph")
    input_paths = {row["path"] for row in projection.inputs}
    public_inputs = {
        path
        for path in input_paths
        if path.startswith("data/snapshots/public/")
        and path.count("/") == 3
    }
    scenario_inputs = {
        path
        for path in input_paths
        if path.startswith("data/synthetic/") and path.count("/") == 2
    }
    scenarios = {
        node.id for node in projection.nodes if node.label == "Scenario"
    }
    public_decisions = [
        node
        for node in projection.nodes
        if node.label == "Decision"
        and node.properties["scenario_id"] == "PUBLIC"
    ]

    assert len(public_inputs) == 11
    assert len(scenario_inputs) == 11
    assert len(scenarios) == 11
    assert len(public_decisions) == 11
    assert {
        "SYN-MINISTRY-PENICILLIN-API-001",
        "SYN-MINISTRY-STREPTOMYCIN-API-001",
        "SYN-MINISTRY-SOP-001",
        "SYN-MINISTRY-FERT-RETAIL-PACKS-001",
    } <= scenarios
