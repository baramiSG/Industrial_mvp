from __future__ import annotations

import pytest

from ior_mvp.graph.loader import verify
from ior_mvp.graph.model import LABELS


pytestmark = pytest.mark.graph


def _driver(spec):
    from neo4j import GraphDatabase

    return GraphDatabase.driver(
        spec.uri,
        auth=(spec.username, spec.password),
    )


def _rows(spec, query: str) -> list[dict]:
    driver = _driver(spec)
    try:
        result = driver.execute_query(query, database_=spec.database)
        return [record.data() for record in result.records]
    finally:
        driver.close()


def test_show_constraints_has_one_uniqueness_constraint_per_label(
    connection_spec,
    loaded_graph,
) -> None:
    del loaded_graph
    rows = _rows(
        connection_spec,
        "SHOW CONSTRAINTS YIELD name, type "
        "WHERE name STARTS WITH 'graph_' "
        "RETURN name, type ORDER BY name",
    )
    assert len(rows) == len(LABELS)
    assert {row["type"] for row in rows} == {"UNIQUENESS"}


def test_counts_by_label_and_type_equal_artifact(
    connection_spec,
    projection,
    loaded_graph,
) -> None:
    del loaded_graph
    report = verify(connection_spec, projection)
    assert report.node_count == projection.counts["nodes"]
    assert report.edge_count == projection.counts["edges"]
    assert report.counts_by_label == {
        label: projection.counts["nodes_by_label"].get(label, 0)
        for label in LABELS
    }
    assert report.counts_by_type == projection.counts["edges_by_type"]


def test_provenance_null_count_is_zero_for_nodes_and_relationships(
    connection_spec,
    loaded_graph,
) -> None:
    del loaded_graph
    node_rows = _rows(
        connection_spec,
        "MATCH (n) WHERE n.evidence_id IS NULL OR n.as_of IS NULL "
        "OR n.evidence_class IS NULL OR n.synthetic_flag IS NULL "
        "OR n.scenario_id IS NULL RETURN count(n) AS count",
    )
    edge_rows = _rows(
        connection_spec,
        "MATCH ()-[r]->() WHERE r.evidence_id IS NULL OR r.as_of IS NULL "
        "OR r.evidence_class IS NULL OR r.synthetic_flag IS NULL "
        "OR r.scenario_id IS NULL RETURN count(r) AS count",
    )
    assert node_rows == [{"count": 0}]
    assert edge_rows == [{"count": 0}]


def test_no_public_edge_to_synthetic_node_live(
    connection_spec,
    loaded_graph,
) -> None:
    del loaded_graph
    rows = _rows(
        connection_spec,
        "MATCH (a)-[r]->(b) WHERE r.synthetic_flag = false "
        "AND (a.synthetic_flag = true OR b.synthetic_flag = true) "
        "RETURN count(r) AS count",
    )
    assert rows == [{"count": 0}]
