from __future__ import annotations

from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.engine_feed import (
    adjacency_explanation,
    evidence_linkage,
    route_blocking_capability,
    shared_enabler_queue_rows,
)
from ior_mvp.graph.loader import execute_view


pytestmark = pytest.mark.graph


def _branches(projection):
    scenarios = {
        node.properties["opportunity_id"]: node.id
        for node in projection.nodes
        if node.label == "Scenario"
    }
    for node in projection.nodes:
        if node.label != "Product":
            continue
        yield node.id, "public", "PUBLIC", "public"
        if node.id in scenarios:
            scenario_id = scenarios[node.id]
            yield (
                node.id,
                "simulated",
                scenario_id,
                ("simulated", scenario_id),
            )


def test_view_v1_v4_cypher_equal_artifact_for_every_opportunity_and_mode(
    connection_spec,
    projection,
    loaded_graph,
) -> None:
    del loaded_graph
    for opportunity_id, mode, scenario_id, branch in _branches(projection):
        live = execute_view(
            connection_spec,
            "adjacency",
            opportunity_id=opportunity_id,
            mode=mode,
            scenario_id=scenario_id,
        )
        artifact = adjacency_explanation(
            projection,
            opportunity_id,
            branch=branch,
        )
        assert [row["producer_id"] for row in live] == artifact["producer_ids"]
        if live:
            for key in (
                "fired",
                "execution",
                "same_process_family",
                "qualifying_signal_count",
                "result_code",
            ):
                assert live[0][key] == artifact[key]

        live = execute_view(
            connection_spec,
            "route_blocking",
            opportunity_id=opportunity_id,
            mode=mode,
            scenario_id=scenario_id,
        )
        assert live == route_blocking_capability(
            projection,
            opportunity_id,
            branch=branch,
        )

        live = execute_view(
            connection_spec,
            "evidence_to_change",
            opportunity_id=opportunity_id,
            mode=mode,
            scenario_id=scenario_id,
        )
        assert live == evidence_linkage(
            projection,
            opportunity_id,
            branch=branch,
        )

        live = execute_view(
            connection_spec,
            "shared_enabler",
            opportunity_id=opportunity_id,
            mode=mode,
            scenario_id=scenario_id,
        )
        assert live == shared_enabler_queue_rows(
            projection,
            branch=branch,
        )


def test_public_queries_filter_synthetic_flag() -> None:
    source = (
        PROJECT_ROOT / "src/ior_mvp/graph/cypher.py"
    ).read_text(encoding="utf-8")
    for view_id in (
        "adjacency",
        "route_blocking",
        "shared_enabler",
        "evidence_to_change",
    ):
        section = source.split(f'"{view_id}": """', maxsplit=1)[1].split(
            '""",',
            maxsplit=1,
        )[0]
        assert "synthetic_flag = false" in section
        assert "ORDER BY" in section
