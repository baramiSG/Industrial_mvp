from __future__ import annotations

from pathlib import Path

import pytest

from ior_mvp.acquisition.contracts import OfflineGuardViolation
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.graph.artifact import load_projection
from ior_mvp.graph.loader import GraphSafetyError, resolve_target
from ior_mvp.graph.service import (
    GraphConnectionError,
    GraphDriverUnavailable,
    GraphService,
)


PROJECTION_ID = "GRAPH-SAU-2026-01-01-aaaaaaaaaaaa"


def test_not_configured_without_env() -> None:
    service = GraphService(None, artifact_projection_id=PROJECTION_ID)
    assert service.status() == {
        "graph_status": "GRAPH_UNAVAILABLE",
        "reason_code": "NOT_CONFIGURED",
        "target": None,
        "artifact_projection_id": PROJECTION_ID,
        "live_projection_id": None,
        "counts": None,
        "synthetic_partition": None,
    }


def test_driver_not_installed_maps_to_typed_state(tmp_path: Path) -> None:
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})

    def unavailable(_spec):
        raise GraphDriverUnavailable

    status = GraphService(
        spec,
        artifact_projection_id=PROJECTION_ID,
        status_reader=unavailable,
    ).status()
    assert status["reason_code"] == "DRIVER_NOT_INSTALLED"


def test_service_unavailable_maps_to_connection_failed(tmp_path: Path) -> None:
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})

    def unavailable(_spec):
        raise GraphConnectionError("service stopped")

    status = GraphService(
        spec,
        artifact_projection_id=PROJECTION_ID,
        status_reader=unavailable,
    ).status()
    assert status["reason_code"] == "CONNECTION_FAILED"


def test_auth_error_maps_to_connection_failed_without_credential_text(
    tmp_path: Path,
) -> None:
    auth = tmp_path / "auth"
    credential = "do-not-disclose"
    auth.write_text(f"neo4j/{credential}\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})

    def unavailable(_spec):
        raise GraphConnectionError(f"authentication failed: {credential}")

    status = GraphService(
        spec,
        artifact_projection_id=PROJECTION_ID,
        status_reader=unavailable,
    ).status()
    assert credential not in str(status)
    assert status["reason_code"] == "CONNECTION_FAILED"


def test_instance_mismatch_refused_before_connect() -> None:
    with pytest.raises(GraphSafetyError, match="INSTANCE_MISMATCH"):
        resolve_target(
            "aura",
            {
                "NEO4J_URI": "neo4j+s://wrong.databases.neo4j.io",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "not-printed",
                "NEO4J_DATABASE": "neo4j",
                "AURA_INSTANCEID": "expected",
            },
            confirm_instance="expected",
        )


def test_projection_mismatch_typed(tmp_path: Path) -> None:
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})
    service = GraphService(
        spec,
        artifact_projection_id=PROJECTION_ID,
        status_reader=lambda _spec: {
            "projection_id": "GRAPH-OTHER",
            "counts": {"nodes": 1, "edges": 0},
            "synthetic_partition": {
                "public_nodes": 1,
                "synthetic_nodes": 0,
            },
        },
    )
    assert service.status()["reason_code"] == "PROJECTION_MISMATCH"


def test_offline_guard_violation_propagates(tmp_path: Path) -> None:
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})

    def blocked(_spec):
        raise OfflineGuardViolation("socket refused by tests")

    with pytest.raises(OfflineGuardViolation):
        GraphService(
            spec,
            artifact_projection_id=PROJECTION_ID,
            status_reader=blocked,
        ).status()


def test_no_gds_or_apoc_tokens_in_required_paths() -> None:
    required = [
        PROJECT_ROOT / "src/ior_mvp/graph/engine_feed.py",
        PROJECT_ROOT / "src/ior_mvp/graph/cypher.py",
    ]
    prohibited = ("gds" + ".", "apoc" + ".")
    assert all(
        token not in path.read_text(encoding="utf-8")
        for path in required
        for token in prohibited
    )


def test_compose_target_is_loopback_and_ignores_inherited_uri(
    tmp_path: Path,
) -> None:
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target(
        "compose",
        {
            "NEO4J_AUTH_FILE": str(auth),
            "NEO4J_URI": "neo4j+s://forbidden.databases.neo4j.io",
        },
    )
    assert spec.uri == "bolt://localhost:7688"
    assert "password" not in repr(spec).casefold()


def test_available_view_returns_governed_nodes_and_relationships(
    tmp_path: Path,
) -> None:
    projection = load_projection(PROJECT_ROOT / "data/graph")
    adjacency = next(
        edge
        for edge in projection.edges
        if edge.type == "ADJACENT_TO"
        and edge.properties["scenario_id"] == "PUBLIC"
    )
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})
    service = GraphService(
        spec,
        artifact_projection_id=projection.projection_id,
        projection=projection,
        status_reader=lambda _spec: {
            "projection_id": projection.projection_id,
            "counts": projection.counts,
            "synthetic_partition": {
                "public_nodes": 1,
                "synthetic_nodes": 0,
            },
        },
        view_reader=lambda *_args: [
            {
                "producer_id": adjacency.source,
                "fired": adjacency.properties["fired"],
            }
        ],
    )
    payload = service.view(
        "adjacency",
        adjacency.target,
        "public",
    )
    assert {node["id"] for node in payload["nodes"]} == {
        adjacency.source,
        adjacency.target,
    }
    assert len(payload["edges"]) == 1
    assert payload["edges"][0]["id"] == adjacency.key
    assert payload["edges"][0]["type"] == "ADJACENT_TO"


def test_s16b_query_failure_after_available_status_fails_closed(
    tmp_path: Path,
) -> None:
    projection = load_projection(PROJECT_ROOT / "data/graph")
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})

    def unavailable(*_args):
        raise GraphConnectionError("query failed")

    service = GraphService(
        spec,
        artifact_projection_id=projection.projection_id,
        projection=projection,
        status_reader=lambda _spec: {
            "projection_id": projection.projection_id,
            "counts": projection.counts,
            "synthetic_partition": {},
        },
        view_reader=unavailable,
    )
    payload = service.view("adjacency", "SAU-H0-721049", "public")
    assert payload["graph_status"] == "GRAPH_UNAVAILABLE"
    assert payload["reason_code"] == "CONNECTION_FAILED"
    assert payload["nodes"] == []
    assert service.shared_enablers("public")["reason_code"] == (
        "CONNECTION_FAILED"
    )


def test_s16b_unexpected_query_and_offline_guard_errors_propagate(
    tmp_path: Path,
) -> None:
    projection = load_projection(PROJECT_ROOT / "data/graph")
    auth = tmp_path / "auth"
    auth.write_text("neo4j/test-password\n", encoding="utf-8")
    spec = resolve_target("compose", {"NEO4J_AUTH_FILE": str(auth)})
    status = lambda _spec: {
        "projection_id": projection.projection_id,
        "counts": projection.counts,
        "synthetic_partition": {},
    }
    for error in (
        RuntimeError("programming error"),
        OfflineGuardViolation("socket refused"),
    ):
        service = GraphService(
            spec,
            artifact_projection_id=projection.projection_id,
            projection=projection,
            status_reader=status,
            view_reader=lambda *_args, error=error: (_ for _ in ()).throw(error),
        )
        with pytest.raises(type(error), match=str(error)):
            service.view("adjacency", "SAU-H0-721049", "public")
