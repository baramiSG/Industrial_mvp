from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import ior_mvp.decision_engine as decision_engine
from ior_mvp.app import app
from ior_mvp.data_repository import get_synthetic_scenario


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_opportunity_list_modes() -> None:
    public = client.get("/api/opportunities?mode=public")
    simulated = client.get("/api/opportunities?mode=simulated")
    assert public.status_code == simulated.status_code == 200
    assert len(public.json()) == len(simulated.json()) == 2


def test_steel_ui_manifest_uses_approved_components() -> None:
    response = client.get("/api/opportunities/SAU-H0-721049/ui-manifest?mode=simulated")
    assert response.status_code == 200
    payload = response.json()
    approved = {
        "integrity_banner",
        "decision_hero",
        "metric_grid",
        "trade_chart",
        "rule_ledger",
        "capability_matrix",
        "economics_panel",
        "evidence_ledger",
        "data_unlocks",
        "decision_actions",
    }
    assert {row["type"] for row in payload["components"]} <= approved
    assert payload["guardrails"]["real_decision_never_uses_synthetic"] is True


def test_public_manifest_omits_economics_panel() -> None:
    response = client.get("/api/opportunities/SAU-H0-721049/ui-manifest?mode=public")
    types = {row["type"] for row in response.json()["components"]}
    assert "economics_panel" not in types


def test_dossier_html_discloses_simulation() -> None:
    response = client.get("/api/opportunities/SAU-H0-721049/dossier.html?mode=simulated")
    assert response.status_code == 200
    assert "SIMULATED — NOT MINISTRY EVIDENCE" in response.text


def test_extraction_endpoint() -> None:
    response = client.get("/api/extraction-demo")
    assert response.status_code == 200
    assert response.json()["accuracy"] == 1.0


def test_unknown_opportunity_returns_404() -> None:
    response = client.get("/api/opportunities/DOES-NOT-EXIST")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "endpoint",
    [
        (
            "/api/opportunities/SAU-H0-721049"
            "?mode=simulated"
        ),
        "/api/opportunities?mode=simulated",
    ],
)
def test_evidence_integrity_failure_returns_422_json(
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    invalid = deepcopy(scenario)
    invalid["synthetic_inputs"]["demand"][
        "target_spec_demand_kt"
    ] = 288.0
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: invalid,
    )

    integrity_client = TestClient(
        app,
        raise_server_exceptions=False,
    )
    response = integrity_client.get(endpoint)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": (
                "Synthetic scenario reconciliation failed for "
                "SYN-MINISTRY-STEEL-001: "
                "target_spec_demand_within_public_imports"
            ),
        }
    }


def test_missing_scenario_in_simulated_mode_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: None,
    )

    response = client.get(
        "/api/opportunities/SAU-H0-721049"
        "?mode=simulated"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "No synthetic scenario is available for "
            "SAU-H0-721049"
        )
    }


@pytest.mark.parametrize(
    "endpoint",
    [
        (
            "/api/opportunities/SAU-H0-721049"
            "?mode=simulated"
        ),
        "/api/opportunities?mode=simulated",
    ],
)
def test_ground_truth_mismatch_returns_422_without_partial_analysis(
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    invalid = deepcopy(scenario)
    invalid["ground_truth"][
        "expected_simulation_state"
    ] = "REJECT"
    invalid["ground_truth"]["expected_route_code"] = 0
    pp_scenario = get_synthetic_scenario("SAU-H0-390210")
    assert pp_scenario is not None
    invalid["decision_narrative"]["REJECT"] = deepcopy(
        pp_scenario["decision_narrative"]["REJECT"]
    )
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: invalid,
    )

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).get(endpoint)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": (
                "Synthetic scenario ground-truth back-test failed "
                "for SYN-MINISTRY-STEEL-001: "
                "expected state=REJECT, route_code=0; "
                "actual state=ADVANCE, route_code=5"
            ),
        }
    }
