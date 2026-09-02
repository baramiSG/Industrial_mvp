from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import ior_mvp.decision_engine as decision_engine
from ior_mvp.app import STATIC_DIR, app, spa_fallback
from ior_mvp.data_repository import get_synthetic_scenario


client = TestClient(app)
ARABIC_DISCLOSURE = "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.2.0"


def test_release_version_matches_analysis_authority() -> None:
    health_response = client.get("/api/health")
    analysis_response = client.get(
        "/api/opportunities/SAU-H0-721049?mode=public"
    )

    assert health_response.status_code == 200
    assert analysis_response.status_code == 200
    assert (
        health_response.json()["version"]
        == analysis_response.json()["authority"]["project_version"]
        == "0.2.0"
    )


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
    banner = next(
        row
        for row in payload["components"]
        if row["type"] == "integrity_banner"
    )
    assert banner["props"]["synthetic_labels"] == {
        "en": "SIMULATED — NOT MINISTRY EVIDENCE",
        "ar": ARABIC_DISCLOSURE,
    }


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


def test_demo_removes_docs_link_but_engineer_route_remains() -> None:
    index_response = client.get("/")
    docs_response = client.get("/docs")

    assert index_response.status_code == 200
    assert 'href="/docs"' not in index_response.text
    assert docs_response.status_code == 200
    assert "swagger-ui" in docs_response.text


def test_spa_fallback_does_not_serve_file_outside_static_dir() -> None:
    response = spa_fallback("../../../pyproject.toml")

    assert response.path == STATIC_DIR / "index.html"


@pytest.mark.parametrize(
    "path",
    [
        "/..%2F..%2F..%2Fpyproject.toml",
        "/%2e%2e/%2e%2e/%2e%2e/pyproject.toml",
    ],
)
def test_encoded_spa_traversal_returns_index(path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert "<title></title>" in response.text
    assert 'data-i18n="brand.name"' in response.text
    assert '<script type="module" src="/static/app.js"></script>' in response.text
    assert "[project]" not in response.text
    assert 'name = "industrial-opportunity-resolution-mvp"' not in response.text


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/static/app.js", "export async function init"),
        ("/app.js", "export async function init"),
        (
            "/static/modules/api.js",
            "export async function getJSON",
        ),
        (
            "/modules/api.js",
            "export async function getJSON",
        ),
    ],
)
def test_legitimate_static_file_is_served(
    path: str,
    expected: str,
) -> None:
    response = client.get(path)

    assert response.status_code == 200
    assert expected in response.text


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


def test_missing_scenario_in_simulated_list_returns_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: None,
    )

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).get("/api/opportunities?mode=simulated")

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


@pytest.mark.parametrize(
    ("block", "missing_key"),
    [
        ("national_value", "displacement"),
        ("evsi", "route_change_probability"),
    ],
)
def test_missing_economics_input_returns_422(
    monkeypatch: pytest.MonkeyPatch,
    block: str,
    missing_key: str,
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    invalid = deepcopy(scenario)
    if block == "national_value":
        del invalid["synthetic_inputs"]["economics"][
            "national_value"
        ][missing_key]
    else:
        del invalid["synthetic_inputs"][block][missing_key]
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: invalid,
    )

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).get(
        "/api/opportunities/SAU-H0-721049"
        "?mode=simulated"
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"]["code"] == "EVIDENCE_INTEGRITY_ERROR"
    assert missing_key in payload["detail"]["message"]
