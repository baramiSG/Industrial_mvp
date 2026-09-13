from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ior_mvp.graph.api import get_graph_service, router
from ior_mvp.graph.service import GraphService


pytestmark = pytest.mark.graph_unavailable


def _client(connection_spec, projection) -> TestClient:
    service = GraphService(
        connection_spec,
        artifact_projection_id=projection.projection_id,
        projection=projection,
    )
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_graph_service] = lambda: service
    return TestClient(app)


def test_status_is_graph_unavailable_when_service_down(
    connection_spec,
    projection,
) -> None:
    started = time.monotonic()
    response = _client(connection_spec, projection).get("/api/graph/status")
    elapsed = time.monotonic() - started
    assert response.status_code == 200
    assert response.json()["graph_status"] == "GRAPH_UNAVAILABLE"
    assert response.json()["reason_code"] == "CONNECTION_FAILED"
    assert elapsed < 5.0


def test_views_return_typed_unavailable_not_500(
    connection_spec,
    projection,
) -> None:
    response = _client(connection_spec, projection).get(
        "/api/graph/opportunities/SAU-H0-721049/views/adjacency?mode=public"
    )
    assert response.status_code == 200
    assert response.json()["graph_status"] == "GRAPH_UNAVAILABLE"
    assert response.json()["nodes"] == []
    assert response.json()["edges"] == []
