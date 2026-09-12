from __future__ import annotations

import json
import re
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import ior_mvp.decision_engine as decision_engine
from ior_mvp.app import STATIC_DIR, app, spa_fallback
from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import get_synthetic_scenario
from ior_mvp.narratives import NarrativeCatalogueError
from ior_mvp.public_snapshot import PublicSnapshotIntegrityError
from ior_mvp.public_snapshot import validate_public_snapshot
from ior_mvp.rules import evaluate_rules


FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "public_decision"


def _load_advance_fixture() -> dict:
    return json.loads(
        (FIXTURE_ROOT / "advance-route-3.json").read_text(
            encoding="utf-8"
        )
    )


def _load_no_candidate_fixture() -> dict:
    return json.loads(
        (
            FIXTURE_ROOT / "no-candidate-no-fired-signal.json"
        ).read_text(encoding="utf-8")
    )


def _mount_no_candidate_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> dict:
    case = _load_no_candidate_fixture()
    validate_public_snapshot(case)
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    monkeypatch.setattr(
        decision_engine,
        "public_cases",
        lambda: {case["opportunity"]["id"]: deepcopy(case)},
    )
    return case


def test_g1_fixture_returns_200_advance_route_3_with_supporting_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _load_advance_fixture()
    validate_public_snapshot(case)
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3?mode=public"
    )
    assert response.status_code == 200
    payload = response.json()
    real = payload["real_decision"]
    assert real["state"] == "ADVANCE"
    assert real["route_code"] == 3
    assert real["advance_support_signal_rule_ids"] == ["R2"]
    assert real["decision_reason_code"] == "ALL_ADVANCE_GATES_PASS"
    assert real["headline"] == "ADVANCE — route 3"


def test_degraded_only_signal_returns_200_investigate_with_degraded_reason(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _load_advance_fixture()
    case["trade"] = [
        {
            "year": 2024,
            "imports_usd_m": 8.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
        {
            "year": 2025,
            "imports_usd_m": 9.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
        {
            "year": 2026,
            "imports_usd_m": 10.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
    ]
    validate_public_snapshot(case)
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3?mode=public"
    )
    assert response.status_code == 200
    real = response.json()["real_decision"]
    assert real["state"] == "INVESTIGATE"
    assert real["route_code"] is None
    assert (
        real["decision_reason_code"]
        == "ADVANCE_SUPPORT_SIGNAL_DEGRADED"
    )
    assert real["advance_support_signal_rule_ids"] == []
    assert real["route_label"] == (
        "Certification support priority to test"
    )
    need = "Re-export and domestic-origin flow decomposition"
    assert real["missing_facts"] == [need]
    assert response.json()["data_unlocks"] == [need]
    assert response.json()["preferred_hypothesis"]["route_code"] == 3


def test_route_evidence_unavailable_returns_200_investigate_with_route_need(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _load_advance_fixture()
    case["decision_inputs"]["route_evidence"] = "UNAVAILABLE"
    validate_public_snapshot(case)
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3?mode=public"
    )
    assert response.status_code == 200
    payload = response.json()
    real = payload["real_decision"]
    assert real["state"] == "INVESTIGATE"
    assert real["route_code"] is None
    assert (
        real["decision_reason_code"]
        == "ROUTE_DETERMINATION_UNRESOLVED"
    )
    assert real["route_label"] == "Route not yet determined"
    assert payload["preferred_hypothesis"] is None
    need = (
        "Route feasibility, additionality, policy and downside "
        "economics evidence for the candidate routes"
    )
    assert payload["data_unlocks"] == [need]
    assert real["missing_facts"] == [need]


def test_public_case_with_unavailable_route_economics_returns_200_investigate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _load_advance_fixture()
    del case["decision_inputs"]["route_evidence"][0][
        "downside_cash_flows_m_sar"
    ]
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3?mode=public"
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "detail" not in payload
    real = payload["real_decision"]
    assert real["state"] == "INVESTIGATE"
    assert real["route_code"] is None
    assert (
        real["decision_reason_code"]
        == "ROUTE_DETERMINATION_UNRESOLVED"
    )
    assert payload["active_decision"] == real
    assert payload["preferred_hypothesis"] is None
    route = payload["route_hypotheses"][3]
    assert route["status"] == "NOT_CALCULABLE"
    assert "ECONOMICS_UNAVAILABLE" in route["reason_codes"]
    assert route["economics"]["unsupported_npv_m"] == "NOT_CALCULABLE"
    uneconomic = next(
        row
        for row in payload["rejection_conditions"]
        if row["code"] == "uneconomic_at_efficient_scale"
    )
    assert uneconomic["status"] == "NOT_CALCULABLE"
    assert payload["advance_gate"]["passes"] is True
    assert all(
        row["status"] == "NOT_SATISFIED"
        for row in payload["hard_exclusions"]
    )
    need = (
        "Route feasibility, additionality, policy and downside "
        "economics evidence for the candidate routes"
    )
    assert need in payload["data_unlocks"]
    assert need in real["missing_facts"]
    assert (
        client.get(
            "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3/ui-manifest?mode=public"
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3/dossier.html?mode=public&locale=ar"
        ).status_code
        == 200
    )


def test_uneconomic_route_returns_200_reject_with_typed_narrative(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _load_advance_fixture()
    case["decision_inputs"]["route_evidence"][0][
        "downside_cash_flows_m_sar"
    ] = [-1000.0, 1.0]
    validate_public_snapshot(case)
    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        lambda opportunity_id: deepcopy(case),
    )
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/api/opportunities/FIX-PUBLIC-ADVANCE-ROUTE-3?mode=public"
    )
    assert response.status_code == 200
    real = response.json()["real_decision"]
    assert real["state"] == "REJECT"
    assert real["route_code"] == 0
    assert (
        real["decision_reason_code"]
        == "UNECONOMIC_AT_EFFICIENT_SCALE"
    )
    assert real["headline"] == (
        "REJECT — uneconomic at efficient scale"
    )


client = TestClient(app)
ARABIC_DISCLOSURE = "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.2.0"


def test_screening_router_is_mounted_before_the_spa_fallback() -> None:
    response = client.get("/api/screening")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert payload["snapshot_id"] == "SCREENING-SAU-2026-09-12-9b6b22032fd8"
    assert payload["universe_status"]["status"] == "AVAILABLE"
    assert [row["queue_id"] for row in payload["queues"]] == [
        "high_evsi_evidence_investigation",
        "incumbent_upgrade_investigation",
        "likely_false_positive",
        "resilience_case",
        "robust_public_finding",
    ]
    assert payload["synthetic_flag"] is False

    queue = client.get("/api/screening/queues/not-a-queue")
    assert queue.status_code == 404
    assert queue.json() == {"detail": {"code": "QUEUE_NOT_FOUND"}}
    record = client.get("/api/screening/records/000000")
    assert record.status_code == 404
    assert record.json() == {"detail": {"code": "RECORD_NOT_FOUND"}}
    page = client.get(
        "/api/screening/queues/robust_public_finding?offset=0&limit=5"
    )
    assert page.status_code == 200
    assert page.json()["total"] == 119
    assert len(page.json()["entries"]) == 5

    evidence = client.get("/api/screening/evidence")
    assert evidence.status_code == 200
    assert evidence.headers["content-type"].startswith("application/json")
    assert len(evidence.json()["evidence_passports"]) == 8


def test_screening_mount_ignores_evidence_mode_query() -> None:
    assert (
        client.get("/api/screening?mode=simulated").json()
        == client.get("/api/screening").json()
    )
    assert (
        client.get("/api/screening/evidence?mode=simulated").json()
        == client.get("/api/screening/evidence").json()
    )


def test_no_fired_signal_deep_case_returns_200_no_candidate_not_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _mount_no_candidate_fixture(monkeypatch)
    opportunity_id = case["opportunity"]["id"]
    fixture_client = TestClient(app, raise_server_exceptions=False)

    response = fixture_client.get(
        f"/api/opportunities/{opportunity_id}?mode=public"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["real_decision"]["state"] is None
    assert payload["real_decision"]["route_code"] is None
    assert payload["screening_disposition"] == "NO_CANDIDATE"
    assert payload["real_decision"]["decision_reason_code"] == (
        "NO_TRIGGER_FIRED"
    )

    manifest = fixture_client.get(
        f"/api/opportunities/{opportunity_id}/ui-manifest?mode=public"
    )
    assert manifest.status_code == 200
    hero = next(
        row
        for row in manifest.json()["components"]
        if row["type"] == "decision_hero"
    )
    banner = next(
        row
        for row in manifest.json()["components"]
        if row["type"] == "integrity_banner"
    )
    assert hero["props"]["state"] is None
    assert hero["props"]["screening_disposition"] == "NO_CANDIDATE"
    assert banner["props"]["screening_disposition"] == "NO_CANDIDATE"

    dossier = fixture_client.get(
        f"/api/opportunities/{opportunity_id}/dossier?mode=public"
    )
    html = fixture_client.get(
        f"/api/opportunities/{opportunity_id}/dossier.html"
        "?mode=public&locale=ar"
    )
    assert dossier.status_code == html.status_code == 200
    assert dossier.json()["decision_state"] is None
    assert "لا توجد حالة مرشحة" in html.text
    assert not re.search(r">\s*(?:None|null)\s*<", html.text)

    listing = fixture_client.get("/api/opportunities?mode=public")
    assert listing.status_code == 200
    assert listing.json() == [
        {
            **listing.json()[0],
            "id": opportunity_id,
            "real_state": None,
            "active_state": None,
            "screening_disposition": "NO_CANDIDATE",
        }
    ]


def test_no_candidate_expected_payloads_match_engine_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _mount_no_candidate_fixture(monkeypatch)
    opportunity_id = case["opportunity"]["id"]
    expected_path = (
        FIXTURE_ROOT / "no-candidate-no-fired-signal.expected.json"
    )
    assert expected_path.is_file()
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    fixture_client = TestClient(app, raise_server_exceptions=False)

    actual = {
        "list_entry": fixture_client.get(
            "/api/opportunities?mode=public"
        ).json()[0],
        "analysis": fixture_client.get(
            f"/api/opportunities/{opportunity_id}?mode=public"
        ).json(),
        "ui_manifest": fixture_client.get(
            f"/api/opportunities/{opportunity_id}/ui-manifest?mode=public"
        ).json(),
    }
    assert actual == expected


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


@pytest.mark.parametrize(
    ("opportunity_id", "expected_hhi"),
    [
        ("SAU-H0-721049", 0.36),
        ("SAU-H0-390210", None),
    ],
)
def test_detailed_analysis_exposes_additive_public_snapshot_v2_contract(
    opportunity_id: str,
    expected_hhi: float | None,
) -> None:
    response = client.get(
        f"/api/opportunities/{opportunity_id}?mode=public"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "2.1.0"
    assert {
        "screening_disposition",
        "gap_class",
        "route_hypotheses",
        "preferred_hypothesis",
        "evidence_class_assessment",
        "advance_gate",
        "hard_exclusions",
        "rejection_conditions",
        "narrative_version",
    } <= set(payload)
    assert payload["screening_disposition"] == "CANDIDATE"
    assert len(payload["route_hypotheses"]) == 9
    assert payload["narrative_version"] == "1.0.0"
    assert set(payload["domestic_flows"]) == {
        "period_year",
        "domestic_production_kt",
        "retained_imports_kt",
        "domestic_origin_exports_kt",
        "reexports_kt",
        "source_evidence_ids",
    }
    assert payload["criticality_designation"] == "UNAVAILABLE"
    r3 = next(
        row for row in payload["rules"] if row["rule_id"] == "R3"
    )
    assert set(r3["metrics"]) >= {"value", "quantity"}
    if expected_hhi is None:
        assert payload["supplier_metrics"] is None
    else:
        assert payload["supplier_metrics"][
            "partner_value_hhi"
        ] == pytest.approx(expected_hhi)
        assert r3["metrics"]["value"]["hhi"] == pytest.approx(
            expected_hhi
        )


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


def test_simulated_detail_mirrors_simulation_decision_branch() -> None:
    response = client.get(
        "/api/opportunities/SAU-H0-721049?mode=simulated"
    )
    assert response.status_code == 200
    payload = response.json()
    simulated = payload["simulation_decision"]
    assert payload["active_decision"] == simulated
    assert payload["preferred_hypothesis"] == simulated["preferred_hypothesis"]
    assert payload["route_hypotheses"] == simulated["route_hypotheses"]
    assert payload["real_decision"]["synthetic_flag"] is False
    assert simulated["synthetic_flag"] is True
    assert simulated["localized_narrative"]["ar"]["headline"]["text"]
    manifest = client.get(
        "/api/opportunities/SAU-H0-721049/ui-manifest?mode=simulated"
    ).json()
    hero = next(
        row for row in manifest["components"] if row["type"] == "decision_hero"
    )
    unlocks = next(
        row for row in manifest["components"] if row["type"] == "data_unlocks"
    )
    assert (
        hero["props"]["localized_narrative"]["ar"]["headline"]["text"]
        == simulated["localized_narrative"]["ar"]["headline"]["text"]
    )
    assert len(unlocks["props"]["localized_missing_facts"]["ar"]) == 5
    dossier = client.get(
        "/api/opportunities/SAU-H0-721049/dossier?mode=simulated"
    ).json()
    assert dossier["next_evidence_actions"] == simulated["missing_facts"]
    assert dossier["counterfactual"] == simulated["counterfactual"]
    html = client.get(
        "/api/opportunities/SAU-H0-721049/dossier.html?mode=simulated&locale=ar"
    )
    assert html.status_code == 200
    assert simulated["localized_narrative"]["ar"]["headline"]["text"] in html.text


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


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/opportunities/SAU-H0-721049?mode=public",
        "/api/opportunities?mode=public",
    ],
)
def test_public_snapshot_integrity_failure_returns_422_without_partial_result(
    monkeypatch: pytest.MonkeyPatch,
    endpoint: str,
) -> None:
    def fail_public_case(opportunity_id: str) -> dict:
        del opportunity_id
        raise PublicSnapshotIntegrityError("schema probe")

    monkeypatch.setattr(
        decision_engine,
        "get_public_case",
        fail_public_case,
    )
    if endpoint.startswith("/api/opportunities?"):
        monkeypatch.setattr(
            decision_engine,
            "public_cases",
            lambda: {"SAU-H0-721049": {}},
        )

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).get(endpoint)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": "schema probe",
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


def test_analysis_narrative_integrity_failure_returns_typed_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_narrative(*args, **kwargs):
        del args, kwargs
        raise NarrativeCatalogueError("narrative probe")

    monkeypatch.setattr(
        decision_engine,
        "compute_public_decision",
        fail_narrative,
    )

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).get("/api/opportunities/SAU-H0-721049?mode=public")

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "EVIDENCE_INTEGRITY_ERROR",
            "message": "narrative probe",
        }
    }
