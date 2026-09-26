from __future__ import annotations

from copy import deepcopy

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ior_mvp.app import app as product_app
import ior_mvp.graph.api as graph_api
from ior_mvp.graph.api import (
    get_graph_service,
    load_view_catalogue,
    router,
)
from ior_mvp.graph.service import GraphNotFound


class FakeGraphService:
    def __init__(self) -> None:
        self._status = {
            "graph_status": "AVAILABLE",
            "reason_code": None,
            "target": "compose",
            "artifact_projection_id": "GRAPH-TEST",
            "live_projection_id": "GRAPH-TEST",
            "counts": {"nodes": 3, "edges": 1},
            "synthetic_partition": {
                "public_nodes": 2,
                "synthetic_nodes": 1,
            },
        }

    def status(self) -> dict:
        return deepcopy(self._status)

    def view(self, view_id: str, opportunity_id: str, mode: str) -> dict:
        if view_id == "missing":
            raise GraphNotFound("GRAPH_VIEW_NOT_FOUND")
        if opportunity_id == "UNKNOWN":
            raise GraphNotFound("OPPORTUNITY_NOT_FOUND")
        synthetic = mode == "simulated"
        provenance = {
            "evidence_id": "E-1",
            "as_of": "2026-01-01",
            "evidence_class": "D" if synthetic else "B",
            "synthetic_flag": synthetic,
            "scenario_id": "SYN-1" if synthetic else "PUBLIC",
        }
        labels = (
            {
                "en": "SIMULATED — NOT MINISTRY EVIDENCE",
                "ar": "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة",
            }
            if synthetic
            else None
        )
        node = {
            "id": "N-1",
            "label": "Product",
            "catalogue_key": "node.product",
            "name_en": "Product",
            "name_ar": "منتج",
            "properties": {},
            "provenance": provenance,
            "derived": False,
        }
        edge = {
            "id": "R-1",
            "type": "SUPPORTED_BY_EVIDENCE",
            "source": "N-1",
            "target": "E-1",
            "properties": {},
            "provenance": provenance,
            "derived": False,
        }
        if labels is not None:
            node["display_labels"] = labels
            edge["display_labels"] = labels
        return {
            "view_id": view_id,
            "opportunity_id": opportunity_id,
            "mode": mode,
            "graph_status": "AVAILABLE",
            "projection_id": "GRAPH-TEST",
            "synthetic_flag": synthetic,
            "display_labels": labels,
            "nodes": [node],
            "edges": [edge],
            "explanation": {"catalogue_key": "view.explanation", "values": {}},
            "drilldown": [
                {
                    "element_id": "N-1",
                    "evidence_ids": ["E-1"],
                    "document_addresses": [],
                }
            ],
        }

    def shared_enablers(self, mode: str) -> dict:
        return {
            "mode": mode,
            "graph_status": "AVAILABLE",
            "projection_id": "GRAPH-TEST",
            "rows": [],
        }


class UnavailableGraphService(FakeGraphService):
    def status(self) -> dict:
        result = super().status()
        result.update(
            {
                "graph_status": "GRAPH_UNAVAILABLE",
                "reason_code": "NOT_CONFIGURED",
                "target": None,
                "live_projection_id": None,
                "counts": None,
                "synthetic_partition": None,
            }
        )
        return result

    def view(self, view_id: str, opportunity_id: str, mode: str) -> dict:
        return {
            "view_id": view_id,
            "opportunity_id": opportunity_id,
            "mode": mode,
            "graph_status": "GRAPH_UNAVAILABLE",
            "reason_code": "NOT_CONFIGURED",
            "projection_id": "GRAPH-TEST",
            "synthetic_flag": False,
            "display_labels": None,
            "nodes": [],
            "edges": [],
            "explanation": None,
            "drilldown": [],
        }


def _client(service: FakeGraphService) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_graph_service] = lambda: service
    return TestClient(app)


def _flatten_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            item
            for nested in value.values()
            for item in _flatten_strings(nested)
        ]
    if isinstance(value, list):
        return [
            item
            for nested in value
            for item in _flatten_strings(nested)
        ]
    return []


def test_status_unavailable_typed_200() -> None:
    response = _client(UnavailableGraphService()).get("/api/graph/status")
    assert response.status_code == 200
    assert response.json()["graph_status"] == "GRAPH_UNAVAILABLE"
    assert response.json()["reason_code"] == "NOT_CONFIGURED"


def test_catalogue_from_yaml_bilingual() -> None:
    catalogue = load_view_catalogue()
    assert catalogue["metadata"]["version"] == "1.0.0"
    assert [row["view_id"] for row in catalogue["views"]] == [
        "adjacency",
        "route_blocking",
        "shared_enabler",
        "evidence_to_change",
    ]
    assert all(
        set(row["label"]) == {"en", "ar"}
        and set(row["description"]) == {"en", "ar"}
        for row in catalogue["views"]
    )


def test_evidence_to_change_api_preserves_product_target_and_sources() -> None:
    from ior_mvp.graph.service import GraphService
    from tests.test_graph_projection import (
        _BROAD_NEED_FIELDS,
        project_sorted_capability_needs,
    )
    from ior_mvp.graph.engine_feed import evidence_linkage

    from types import SimpleNamespace

    projected = project_sorted_capability_needs()
    rows = evidence_linkage(projected, "SAU-TEST", branch="public")

    def status(_spec: object) -> dict:
        return {
            "projection_id": projected.projection_id,
            "counts": projected.counts,
            "synthetic_partition": {},
        }

    service = GraphService(
        SimpleNamespace(target="compose"),
        artifact_projection_id=projected.projection_id,
        projection=projected,
        status_reader=status,
        view_reader=lambda *_args: rows,
    )
    payload = _client(service).get(
        "/api/graph/opportunities/SAU-TEST/views/evidence_to_change?mode=public"
    ).json()
    constrained = [
        edge
        for edge in payload["edges"]
        if edge["type"] == "CONSTRAINED_BY"
        and edge["properties"].get("blocked_field") in _BROAD_NEED_FIELDS
    ]
    assert payload["graph_status"] == "AVAILABLE"
    assert {edge["target"] for edge in constrained} == {"SAU-TEST"}
    assert all(edge["properties"]["evidence_ids"] for edge in constrained)


def test_view_payload_schema_with_fake_service() -> None:
    response = _client(FakeGraphService()).get(
        "/api/graph/opportunities/SAU-H0-721049/views/adjacency?mode=public"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["view_id"] == "adjacency"
    assert payload["graph_status"] == "AVAILABLE"
    assert payload["nodes"][0]["provenance"]["scenario_id"] == "PUBLIC"
    assert payload["edges"][0]["type"] == "SUPPORTED_BY_EVIDENCE"


def test_unknown_view_and_opportunity_typed_404() -> None:
    client = _client(FakeGraphService())
    response = client.get(
        "/api/graph/opportunities/SAU-H0-721049/views/missing?mode=public"
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "GRAPH_VIEW_NOT_FOUND"
    response = client.get(
        "/api/graph/opportunities/UNKNOWN/views/adjacency?mode=public"
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "OPPORTUNITY_NOT_FOUND"


def test_public_view_payload_has_no_synthetic_marker() -> None:
    payload = _client(FakeGraphService()).get(
        "/api/graph/opportunities/SAU-H0-721049/views/adjacency?mode=public"
    ).json()
    strings = _flatten_strings(payload)
    assert "SIMULATED — NOT MINISTRY EVIDENCE" not in strings
    assert "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة" not in strings
    assert all(
        node["provenance"]["synthetic_flag"] is False
        for node in payload["nodes"]
    )


def test_simulated_view_carries_display_labels_on_every_synthetic_element() -> None:
    payload = _client(FakeGraphService()).get(
        "/api/graph/opportunities/SAU-H0-721049/views/adjacency?mode=simulated"
    ).json()
    synthetic_elements = [
        *(
            node
            for node in payload["nodes"]
            if node["provenance"]["synthetic_flag"]
        ),
        *(
            edge
            for edge in payload["edges"]
            if edge["provenance"]["synthetic_flag"]
        ),
    ]
    assert synthetic_elements
    assert all(set(row["display_labels"]) == {"en", "ar"} for row in synthetic_elements)


def test_labels_resolve_to_catalogue_key_or_bilingual_pair() -> None:
    payload = _client(FakeGraphService()).get(
        "/api/graph/opportunities/SAU-H0-721049/views/adjacency?mode=public"
    ).json()
    assert all(
        node.get("catalogue_key")
        or (node.get("name_en") and node.get("name_ar"))
        for node in payload["nodes"]
    )


def test_s16b_product_app_mounts_existing_graph_router() -> None:
    response = TestClient(product_app).get("/api/graph/catalogue")
    assert response.status_code == 200
    assert response.json()["metadata"]["version"] == "1.0.0"


def test_s16b_corrupt_canonical_graph_returns_sanitized_422(
    monkeypatch,
) -> None:
    from ior_mvp.graph.repository import GraphRepositoryError

    def invalid_projection():
        raise GraphRepositoryError("private artifact detail")

    monkeypatch.setattr(graph_api, "graph_projection", invalid_projection)
    response = TestClient(product_app, raise_server_exceptions=False).get(
        "/api/graph/status"
    )
    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "GRAPH_ARTIFACT_INTEGRITY_ERROR"
    }
    assert "private artifact detail" not in response.text
