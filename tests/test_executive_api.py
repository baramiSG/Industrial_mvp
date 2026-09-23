"""Mounted read-only executive API contracts."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from ior_mvp.app import app
from ior_mvp.executive.service import (
    build_executive_case,
    build_executive_summary,
    clear_executive_caches,
)


@pytest.fixture(autouse=True)
def _clear_executive_cache() -> None:
    clear_executive_caches()
    yield
    clear_executive_caches()


def test_summary_and_case_responses_equal_typed_service_models() -> None:
    client = TestClient(app)
    summary = client.get("/api/executive/summary")
    case = client.get("/api/executive/opportunities/SAU-H0-721049")

    assert summary.status_code == 200
    assert summary.json() == build_executive_summary().model_dump(mode="json")
    assert case.status_code == 200
    assert case.json() == build_executive_case(
        "SAU-H0-721049"
    ).model_dump(mode="json")


def test_unknown_opportunity_returns_typed_404() -> None:
    response = TestClient(app).get(
        "/api/executive/opportunities/SAU-H0-000000"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "code": "EXECUTIVE_OPPORTUNITY_NOT_FOUND",
            "message": "SAU-H0-000000",
        }
    }


def test_governed_integrity_failure_returns_typed_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import ior_mvp.executive.api as executive_api
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    def fail_summary():
        raise ExecutiveIntegrityError("Injected governed failure")

    with monkeypatch.context() as scoped:
        scoped.setattr(
            executive_api.service,
            "build_executive_summary",
            fail_summary,
        )
        response = TestClient(app).get("/api/executive/summary")
    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EXECUTIVE_INTEGRITY_ERROR",
            "message": "Injected governed failure",
        }
    }


def test_routes_are_mounted_before_spa_fallback_and_accept_no_mode_or_source() -> None:
    from ior_mvp.executive.api import router as executive_router

    fallback_index = next(
        index
        for index, route in enumerate(app.routes)
        if getattr(route, "path", None) == "/{path:path}"
    )
    executive_index = next(
        index
        for index, route in enumerate(app.routes)
        if getattr(route, "original_router", None) is executive_router
    )
    assert executive_index < fallback_index

    schema = app.openapi()
    summary = schema["paths"]["/api/executive/summary"]["get"]
    case = schema["paths"][
        "/api/executive/opportunities/{opportunity_id}"
    ]["get"]
    assert summary.get("parameters", []) == []
    assert [parameter["name"] for parameter in case["parameters"]] == [
        "opportunity_id"
    ]
    assert summary["responses"]["200"]["content"]["application/json"][
        "schema"
    ] == {"$ref": "#/components/schemas/ExecutiveSummary"}
    assert case["responses"]["200"]["content"]["application/json"][
        "schema"
    ] == {"$ref": "#/components/schemas/ExecutiveCase"}


def test_executive_runtime_does_not_import_acquisition_transport() -> None:
    import inspect
    import ior_mvp.executive.api as executive_api
    import ior_mvp.executive.service as executive_service

    source = inspect.getsource(executive_api) + inspect.getsource(
        executive_service
    )
    assert "acquisition" not in source
    assert "requests" not in source
    assert "httpx" not in source


@pytest.mark.parametrize("opportunity_id", [
    "SAU-H0-390210", "SAU-H0-721049", "SAU-H6-294110", "SAU-H6-294120",
    "SAU-H6-310430", "SAU-H6-310510", "SAU-H6-392010", "SAU-H6-721012",
    "SAU-H6-721061", "SAU-H6-760429", "SAU-H6-760711",
])
def test_am4_all_loaded_case_endpoints_are_typed_200(opportunity_id):
    from ior_mvp.executive.models import ExecutiveCase
    response = TestClient(app).get(f"/api/executive/opportunities/{opportunity_id}")
    assert response.status_code == 200, response.text
    model = ExecutiveCase.model_validate(response.json())
    assert len(model.steps) == 8 and len(model.vectors) == 4
    assert model == build_executive_case(opportunity_id)


@pytest.mark.parametrize("preferred", [None, {}, pytest.param({"route_code": True}, id="true-route-code"),
    pytest.param({"route_code": False}, id="false-route-code"),
    {"route_code": "5"}, {"route_code": 5.0}, {"route_code": -1}, {"route_code": 9},
    {"route_code": None}, {"route_code": 7}, [], "route", 5, "MISSING"])
def test_am4_preferred_route_contract_service_and_typed_api(monkeypatch, preferred):
    from copy import deepcopy
    from ior_mvp.decision_engine import analyze
    import ior_mvp.executive.service as service
    from ior_mvp.executive.taxonomy import ExecutiveIntegrityError

    def changed(opportunity_id, mode="public"):
        value = deepcopy(analyze(opportunity_id, mode))
        if mode == "public":
            if preferred == "MISSING":
                value.pop("preferred_hypothesis")
            else:
                value["preferred_hypothesis"] = preferred
            value["route_hypotheses"] = [r for r in value["route_hypotheses"] if r["route_code"] != 7]
            for i, route in enumerate(value["route_hypotheses"]):
                route["status"] = "fails" if i % 2 else "NOT_CALCULABLE"
        return value

    monkeypatch.setattr(service, "analyze", changed)
    # PP retains its real route 0; present None cannot be coupled to that route or status mix.
    opportunity_id = "SAU-H0-390210"
    if preferred is None:
        case = build_executive_case(opportunity_id)
        value = next(v for s in case.steps for v in s.values if v.key == "preferred_route_code")
        assert (value.availability.value, value.value) == ("NOT_CALCULABLE", None)
        assert case.decisions.public.route_code == 0
    else:
        with pytest.raises(ExecutiveIntegrityError):
            build_executive_case(opportunity_id)
    response = TestClient(app).get(f"/api/executive/opportunities/{opportunity_id}")
    assert response.status_code == (200 if preferred is None else 422), response.text
    if preferred is None:
        value = next(v for s in response.json()["steps"] for v in s["values"] if v["key"] == "preferred_route_code")
        assert value["availability"] == "NOT_CALCULABLE" and value["value"] is None
    else:
        assert response.json()["detail"]["code"] == "EXECUTIVE_INTEGRITY_ERROR"


@pytest.mark.parametrize("mutation", [
    "unrelated_shared", "other_suffix", "absent", "wrong_route", "wrong_field",
    "forged_enabler", "missing_declaration", "missing_stored", "missing_scenario",
    "duplicate_scenario", "duplicate_id", "missing_id", "extra_id", "wrong_projection",
    "wrong_dependents", "missing_payload", "graph_unavailable", "graph_missing",
    "nonstring_id", "empty_id", "malformed_ids",
])
def test_am4_foreign_or_malformed_simulated_references_return_typed_422(monkeypatch, mutation):
    from copy import deepcopy
    from ior_mvp.decision_engine import analyze
    from ior_mvp.data_repository import synthetic_scenarios
    from ior_mvp.evidence import synthetic_evidence_rows
    from ior_mvp.graph.repository import GraphRepositoryError
    import ior_mvp.executive.service as service
    import ior_mvp.executive.provenance as provenance

    opportunity_id = "SAU-H6-760429"
    public = analyze(opportunity_id, "public")
    simulated = deepcopy(analyze(opportunity_id, "simulated"))
    decision = simulated["simulation_decision"]
    route = next(r for r in decision["route_hypotheses"] if r["route_code"] == 8)
    payload = route["shared_enabler"]
    foreign_id = "SYN-MINISTRY-ALU-FOIL-001::shared_enabler"
    scenarios = deepcopy(synthetic_scenarios())
    foreign = scenarios["SAU-H6-760711"]
    if mutation in {"unrelated_shared", "other_suffix", "absent", "wrong_route"}:
        bad = {"unrelated_shared": "ANY-UNRELATED::shared_enabler", "other_suffix": "ANY-UNRELATED::other_suffix",
               "absent": "ABSENT", "wrong_route": foreign_id}[mutation]
        decision["route_hypotheses"][0]["evidence_ids"].append(bad)
    elif mutation == "wrong_field":
        decision["unrelated"] = {"evidence_ids": [foreign_id]}
    elif mutation == "forged_enabler":
        foreign["synthetic_inputs"]["shared_enabler"]["enabler_id"] = "FORGED"
    elif mutation == "missing_declaration":
        foreign["synthetic_inputs"].pop("shared_enabler")
    elif mutation == "missing_scenario":
        scenarios.pop("SAU-H6-760711")
    elif mutation == "duplicate_scenario":
        foreign["scenario_id"] = scenarios[opportunity_id]["scenario_id"]
    elif mutation == "missing_stored":
        monkeypatch.setattr(provenance, "synthetic_evidence_rows", lambda scenario: [r for r in synthetic_evidence_rows(scenario) if r["evidence_id"] != foreign_id], raising=False)
    elif mutation in {"duplicate_id", "missing_id", "extra_id"}:
        if mutation == "duplicate_id":
            payload["evidence_ids"].append(foreign_id)
        elif mutation == "missing_id":
            payload["evidence_ids"].remove(foreign_id)
        else:
            payload["evidence_ids"].append("ANY-UNRELATED::shared_enabler")
    elif mutation == "wrong_projection":
        payload["graph_projection_id"] = "FORGED"
    elif mutation == "wrong_dependents":
        payload["dependent_opportunity_ids"].reverse()
    elif mutation == "missing_payload":
        route.pop("shared_enabler")
    elif mutation == "graph_unavailable":
        def unavailable():
            raise GraphRepositoryError("Unavailable bound graph")
        monkeypatch.setattr(provenance, "graph_projection", unavailable, raising=False)
    elif mutation == "graph_missing":
        monkeypatch.setattr(provenance, "shared_enabler_inputs", lambda *a, **kw: None, raising=False)
    else:
        decision["unrelated"] = {"evidence_ids": {"nonstring_id": [42], "empty_id": [""], "malformed_ids": "bad"}[mutation]}
    monkeypatch.setattr(provenance, "synthetic_scenarios", lambda: scenarios, raising=False)
    monkeypatch.setattr(service, "analyze", lambda _id, mode="public": public if mode == "public" else simulated)
    response = TestClient(app).get(f"/api/executive/opportunities/{opportunity_id}")
    assert response.status_code == 422, response.text
    assert response.json()["detail"]["code"] == "EXECUTIVE_INTEGRITY_ERROR"
