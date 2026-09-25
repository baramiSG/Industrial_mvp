from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from types import SimpleNamespace
from typing import Any

from ior_mvp.evidence import synthetic_display_labels
from ior_mvp.graph.api import load_view_catalogue
from ior_mvp.graph.engine_feed import (
    adjacency_explanation,
    evidence_linkage,
    route_blocking_capability,
    shared_enabler_queue_rows,
)
from ior_mvp.graph.repository import graph_projection
from ior_mvp.graph.service import GraphService


@lru_cache(maxsize=1)
def _projection():
    return graph_projection()


def _scenario_id(opportunity_id: str) -> str:
    matches = [
        node.id
        for node in _projection().nodes
        if node.label == "Scenario"
        and node.properties.get("opportunity_id") == opportunity_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Scenario identity is ambiguous: {opportunity_id}")
    return matches[0]


def _rows(view_id: str, opportunity_id: str, mode: str) -> list[dict[str, Any]]:
    projection = _projection()
    branch: str | tuple[str, str] = (
        "public" if mode == "public" else ("simulated", _scenario_id(opportunity_id))
    )
    if view_id == "adjacency":
        result = adjacency_explanation(
            projection,
            opportunity_id,
            branch=branch,
        )
        return [
            {"producer_id": producer_id, **result}
            for producer_id in result["producer_ids"]
        ]
    if view_id == "route_blocking":
        return route_blocking_capability(
            projection,
            opportunity_id,
            branch=branch,
        )
    if view_id == "shared_enabler":
        return shared_enabler_queue_rows(projection, branch=branch)
    if view_id == "evidence_to_change":
        return evidence_linkage(
            projection,
            opportunity_id,
            branch=branch,
        )
    raise ValueError(f"Unknown graph fixture view: {view_id}")


def artifact_graph_payload(
    view_id: str,
    opportunity_id: str,
    mode: str,
) -> dict[str, Any]:
    projection = _projection()
    service = GraphService(
        SimpleNamespace(target="fixture"),
        artifact_projection_id=projection.projection_id,
        projection=projection,
        status_reader=lambda _spec: {
            "projection_id": projection.projection_id,
            "counts": projection.counts,
            "synthetic_partition": {},
        },
        view_reader=lambda _spec, requested, identity, branch, _scenario: _rows(
            requested,
            identity,
            branch,
        ),
    )
    return service.view(view_id, opportunity_id, mode)


def route_blocking_fixture(opportunity_id: str) -> dict[str, Any]:
    labels = synthetic_display_labels()
    public_payload = artifact_graph_payload(
        "adjacency", opportunity_id, "public"
    )
    actual_product = deepcopy(next(
        node for node in public_payload["nodes"]
        if node["id"] == opportunity_id
    ))
    synthetic_provenance = {
        "evidence_id": "TEST-ONLY-CLASS-D-BLOCKER",
        "as_of": "2026-09-12",
        "evidence_class": "D",
        "synthetic_flag": True,
        "scenario_id": "TEST-ONLY-S17-BLOCKER",
    }
    nodes = [
        actual_product,
        {
            "id": "TEST-ONLY-INTERVENTION-5",
            "label": "Intervention",
            "catalogue_key": "node.intervention",
            "name_en": "Test-only brownfield route",
            "name_ar": "مسار توسع اختباري في منشأة قائمة",
            "properties": {"route_code": 5},
            "provenance": synthetic_provenance,
            "derived": True,
            "display_labels": labels,
        },
        {
            "id": "TEST-ONLY-CAPABILITY-CERTIFICATION",
            "label": "Capability",
            "catalogue_key": "node.capability",
            "name_en": "Test-only customer qualification",
            "name_ar": "تأهيل عميل اختباري",
            "properties": {"state": "U", "gate": True},
            "provenance": synthetic_provenance,
            "derived": False,
            "display_labels": labels,
        },
    ]
    edge = {
        "id": "TEST-ONLY-ROUTE-BLOCKER-EDGE",
        "type": "CONSTRAINED_BY",
        "source": "TEST-ONLY-INTERVENTION-5",
        "target": "TEST-ONLY-CAPABILITY-CERTIFICATION",
        "properties": {"reason_code": "TEST_ONLY_CLASS_D_BLOCKER"},
        "provenance": synthetic_provenance,
        "derived": True,
        "display_labels": labels,
    }
    return {
        "view_id": "route_blocking",
        "opportunity_id": opportunity_id,
        "mode": "simulated",
        "graph_status": "AVAILABLE",
        "reason_code": None,
        "projection_id": _projection().projection_id,
        "synthetic_flag": True,
        "display_labels": labels,
        "nodes": nodes,
        "edges": [edge],
        "explanation": {
            "catalogue_key": "view.route_blocking.explanation",
            "values": {"row_count": 1},
        },
        "drilldown": [
            {
                "element_id": row["id"],
                "evidence_ids": [row["provenance"]["evidence_id"]],
                "document_addresses": [],
            }
            for row in nodes
        ],
    }


def unavailable_graph_payload(
    view_id: str,
    opportunity_id: str,
    mode: str,
    reason_code: str = "NOT_CONFIGURED",
) -> dict[str, Any]:
    return {
        "view_id": view_id,
        "opportunity_id": opportunity_id,
        "mode": mode,
        "graph_status": "GRAPH_UNAVAILABLE",
        "reason_code": reason_code,
        "projection_id": _projection().projection_id,
        "synthetic_flag": False,
        "display_labels": None,
        "nodes": [],
        "edges": [],
        "explanation": None,
        "drilldown": [],
    }


def graph_catalogue_fixture() -> dict[str, Any]:
    return deepcopy(load_view_catalogue())


def adapt_no_candidate_expected(original: dict[str, Any]) -> dict[str, Any]:
    expected = deepcopy(original)
    identity = "FIX-PUBLIC-NO-CANDIDATE"
    components = expected["ui_manifest"]["components"]
    assert expected["analysis"]["opportunity"]["id"] == identity
    assert [component["type"] for component in components] == [
        "integrity_banner",
        "decision_hero",
        "metric_grid",
        "trade_chart",
        "rule_ledger",
        "capability_matrix",
        "evidence_ledger",
        "data_unlocks",
        "decision_actions",
    ]
    for authority in (
        expected["analysis"]["authority"],
        components[0]["props"]["authority"],
    ):
        versions = authority["config_versions"]
        assert versions["thresholds"] == "1.2.0"
        assert versions["decision_narratives"] == "1.3.0"
        assert versions["ui_strings"] == "1.3.0"
        versions["thresholds"] = "1.3.0"
        versions["decision_narratives"] = "1.4.0"
        versions["ui_strings"] = "1.7.0"
    assert components[-1] == {
        "id": "actions",
        "props": {"mode": "public", "opportunity_id": identity},
        "type": "decision_actions",
    }
    components.append(
        {
            "type": "graph_view",
            "id": "graph-view",
            "props": {"opportunity_id": identity, "mode": "public"},
        }
    )
    assert original != expected
    return expected
