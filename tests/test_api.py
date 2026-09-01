from __future__ import annotations

from fastapi.testclient import TestClient

from ior_mvp.app import app


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
