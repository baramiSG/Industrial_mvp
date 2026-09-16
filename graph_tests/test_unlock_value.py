from __future__ import annotations

import pytest

from ior_mvp.graph.engine_feed import shared_enabler_queue_rows
from ior_mvp.graph.loader import execute_view


pytestmark = pytest.mark.graph


def test_shared_enabler_unlock_value_cypher_equals_engine(
    connection_spec,
    projection,
    loaded_graph,
) -> None:
    del loaded_graph
    scenarios = sorted(
        node.id
        for node in projection.nodes
        if node.label == "Scenario"
    )
    assert any(edge.type == "UNLOCKED_BY" for edge in projection.edges)
    assert scenarios
    for scenario_id in scenarios:
        live = execute_view(
            connection_spec,
            "shared_enabler",
            opportunity_id="",
            mode="simulated",
            scenario_id=scenario_id,
        )
        artifact = shared_enabler_queue_rows(
            projection,
            branch=("simulated", scenario_id),
        )
        assert live == artifact
