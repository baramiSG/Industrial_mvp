from __future__ import annotations

import json
import stat

import pytest

from ior_mvp.graph.cypher import CONSTRAINT_QUERIES, INDEX_QUERIES
from ior_mvp.graph.loader import (
    GraphVerificationError,
    GraphSafetyError,
    ensure_credential,
    load,
    primitive_properties,
    resolve_target,
)
from ior_mvp.graph.model import LABELS
from ior_mvp.graph.projection import GraphProjection


def test_constraints_cover_all_labels_and_indexes_are_per_label() -> None:
    assert len(CONSTRAINT_QUERIES) == len(LABELS)
    for label in LABELS:
        assert sum(f"FOR (n:`{label}`)" in query for query in CONSTRAINT_QUERIES) == 1
        assert any(
            f"FOR (n:`{label}`)" in query
            and "ON (n.synthetic_flag)" in query
            for query in INDEX_QUERIES
        )


def test_primitive_property_codec_flattens_nested_values_and_retains_id() -> None:
    encoded = primitive_properties(
        {
            "id": "N-1",
            "flag": True,
            "score": 1.5,
            "names": ["a", "b"],
            "nested": {"b": 2, "a": 1},
            "maps": [{"x": 1}],
            "missing": None,
        }
    )
    assert encoded["id"] == "N-1"
    assert encoded["names"] == ["a", "b"]
    assert json.loads(encoded["nested"]) == {"a": 1, "b": 2}
    assert json.loads(encoded["maps"]) == [{"x": 1}]
    assert "missing" not in encoded
    assert all(
        isinstance(value, (str, bool, int, float, list))
        for value in encoded.values()
    )


def test_credential_created_once_with_restrictive_mode(tmp_path) -> None:
    path = tmp_path / ".secrets/neo4j_auth.txt"
    assert ensure_credential(path) == "CREDENTIAL_CREATED"
    first = path.read_bytes()
    assert first.startswith(b"neo4j/")
    assert len(first.strip().split(b"/", maxsplit=1)[1]) == 32
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert ensure_credential(path) == "CREDENTIAL_PRESENT"
    assert path.read_bytes() == first


def test_ci_target_requires_password_but_never_uses_inherited_uri() -> None:
    with pytest.raises(GraphSafetyError, match="NEO4J_PASSWORD_REQUIRED"):
        resolve_target("ci", {"NEO4J_URI": "neo4j+s://forbidden.example"})
    spec = resolve_target(
        "ci",
        {
            "NEO4J_PASSWORD": "test-double",
            "NEO4J_URI": "neo4j+s://forbidden.example",
        },
    )
    assert spec.uri == "bolt://localhost:7688"


def test_load_refuses_different_live_projection_before_any_write() -> None:
    class Result:
        def __init__(self, records) -> None:
            self.records = records

        class Summary:
            counters = object()

        summary = Summary()

    class Driver:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def execute_query(self, query, **_kwargs):
            self.queries.append(query)
            if "count(n)" in query:
                return Result([{"count": 1}])
            return Result([{"projection_ids": ["GRAPH-OLD"]}])

        def close(self) -> None:
            return None

    driver = Driver()
    spec = resolve_target(
        "ci",
        {"NEO4J_PASSWORD": "test-double"},
    )
    projection = GraphProjection(
        projection_id="GRAPH-SAU-2026-01-01-newnewnewnew",
        as_of="2026-01-01",
        inputs=[],
        engine={"engine_run_id": "ENGINE-TEST"},
    )
    projection.refresh_counts()
    with pytest.raises(GraphVerificationError, match="projection identity"):
        load(spec, projection, driver_factory=lambda _spec: driver)
    assert len(driver.queries) == 2
    assert all("CREATE " not in query for query in driver.queries)
    assert all("MERGE " not in query for query in driver.queries)


def test_load_empty_graph_counts_before_reading_projection_property() -> None:
    class Result:
        records = [{"count": 0}]

        class Summary:
            counters = object()

        summary = Summary()

    class Driver:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def execute_query(self, query, **_kwargs):
            self.queries.append(query)
            if "collect(DISTINCT n.projection_id)" in query:
                raise AssertionError("empty graph must not read absent property")
            return Result()

        def close(self) -> None:
            return None

    driver = Driver()
    spec = resolve_target("ci", {"NEO4J_PASSWORD": "test-double"})
    projection = GraphProjection(
        projection_id="GRAPH-SAU-2026-01-01-emptyempty12",
        as_of="2026-01-01",
        inputs=[],
        engine={"engine_run_id": "ENGINE-TEST"},
    )
    projection.refresh_counts()
    report = load(spec, projection, driver_factory=lambda _spec: driver)
    assert report.nodes_created == 0
    assert driver.queries[0] == "MATCH (n) RETURN count(n) AS count"
