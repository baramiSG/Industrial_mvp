"""Malformed executive boundaries and evidence-partition regressions."""

from __future__ import annotations

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ior_mvp.app import app
from ior_mvp.data_repository import synthetic_scenarios
from ior_mvp.decision_engine import analyze
from ior_mvp.executive import provenance, service
from ior_mvp.executive.case_projection import build_steps, build_vectors
from ior_mvp.executive.models import (
    EvidenceReference, ExecutiveCase, SyntheticEvsiCase,
)
from ior_mvp.executive.taxonomy import ExecutiveIntegrityError
from ior_mvp.executive.validation import finite_number

STEEL = "SAU-H0-721049"
ALUMINIUM = "SAU-H6-760429"
EVSI_FIELDS = (
    "approximate_evsi_m_sar", "route_change_probability",
    "value_difference_m_sar", "evidence_cost_m_sar", "delay_cost_m_sar",
)
INVALID_NUMBERS = [
    pytest.param(None, id="null"), pytest.param("bad", id="nonnumeric"),
    pytest.param("5", id="numeric-string"), pytest.param(True, id="true"),
    pytest.param(False, id="false"), pytest.param(float("nan"), id="nan"),
    pytest.param(float("inf"), id="positive-infinity"),
    pytest.param(float("-inf"), id="negative-infinity"),
]
BAD_TRADE = [
    pytest.param([], id="empty"), pytest.param(None, id="null"),
    pytest.param({}, id="mapping"), pytest.param(["row"], id="nonmapping-row"),
    pytest.param([{}], id="missing-year"),
    *[pytest.param([{"year": value}], id=f"year-{name}") for name, value in (
        ("null", None), ("true", True), ("false", False),
        ("string", "2024"), ("float", 2024.0),
    )],
]


@pytest.fixture(autouse=True)
def _clear_executive_caches():
    service.clear_executive_caches()
    yield
    service.clear_executive_caches()


def _inject_analysis(monkeypatch, mutate, *, mode="public", opportunity=STEEL):
    def changed(opportunity_id, requested_mode="public"):
        value = deepcopy(analyze(opportunity_id, requested_mode))
        if opportunity_id == opportunity and requested_mode == mode:
            mutate(value)
        return value

    monkeypatch.setattr(service, "analyze", changed)


def _assert_integrity_response(path):
    response = TestClient(app, raise_server_exceptions=False).get(path)
    assert response.status_code == 422, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "EXECUTIVE_INTEGRITY_ERROR"
    assert "/home/" not in detail["message"]
    assert "SECRET-SENTINEL" not in detail["message"]


@pytest.mark.parametrize("trade", BAD_TRADE)
@pytest.mark.parametrize("builder", [build_steps, build_vectors])
def test_trade_shape_and_year_fail_with_typed_integrity_error(trade, builder):
    public = deepcopy(analyze(STEEL, "public"))
    public["trade"] = trade
    with pytest.raises(ExecutiveIntegrityError, match="trade"):
        builder(public, None, {}) if builder is build_steps else builder(public)


@pytest.mark.parametrize("trade", BAD_TRADE)
def test_malformed_trade_returns_typed_api_422(monkeypatch, trade):
    _inject_analysis(monkeypatch, lambda row: row.update(trade=trade))
    _assert_integrity_response(f"/api/executive/opportunities/{STEEL}")


@pytest.mark.parametrize("duplicate", [False, True], ids=["missing", "duplicate"])
def test_required_r11_is_unique_at_step_boundary_and_api(monkeypatch, duplicate):
    def mutate(row):
        if duplicate:
            row["rules"].append(deepcopy(next(r for r in row["rules"] if r["rule_id"] == "R11")))
        else:
            row["rules"] = [r for r in row["rules"] if r["rule_id"] != "R11"]

    public = deepcopy(analyze(STEEL, "public"))
    mutate(public)
    with pytest.raises(ExecutiveIntegrityError, match="R11"):
        build_steps(public, None, {})
    _inject_analysis(monkeypatch, mutate)
    _assert_integrity_response(f"/api/executive/opportunities/{STEEL}")


@pytest.mark.parametrize("field", EVSI_FIELDS)
@pytest.mark.parametrize("value", INVALID_NUMBERS)
def test_supplied_evsi_invalid_number_returns_typed_api_422(monkeypatch, field, value):
    _inject_analysis(monkeypatch, lambda row: row["evsi"].update({field: value}), mode="simulated")
    _assert_integrity_response("/api/executive/summary")


@pytest.mark.parametrize("field", EVSI_FIELDS)
def test_supplied_evsi_missing_number_returns_typed_api_422(monkeypatch, field):
    _inject_analysis(monkeypatch, lambda row: row["evsi"].pop(field), mode="simulated")
    _assert_integrity_response("/api/executive/summary")


@pytest.mark.parametrize("mutation", ["list", "string", "empty", "blank-next-fact", "missing-next-fact"])
def test_supplied_evsi_shape_and_fact_fail_closed(monkeypatch, mutation):
    def mutate(row):
        if mutation == "blank-next-fact":
            row["evsi"]["next_fact"] = " \t\n "
        elif mutation == "missing-next-fact":
            row["evsi"].pop("next_fact")
        else:
            row["evsi"] = {"list": [], "string": "SECRET-SENTINEL", "empty": {}}[mutation]

    _inject_analysis(monkeypatch, mutate, mode="simulated")
    _assert_integrity_response("/api/executive/summary")


def test_zero_evsi_stays_available_and_absent_evsi_stays_unavailable(monkeypatch):
    _inject_analysis(monkeypatch, lambda row: row["evsi"].update({key: 0 for key in EVSI_FIELDS}), mode="simulated")
    response = TestClient(app).get("/api/executive/summary")
    assert response.status_code == 200
    rows = {row["opportunity_id"]: row for row in response.json()["synthetic_evsi"]["cases"]}
    assert rows[STEEL]["availability"] == "AVAILABLE"
    assert all(rows[STEEL][key] == 0.0 for key in EVSI_FIELDS)
    assert rows["SAU-H6-294110"]["availability"] == "UNAVAILABLE"
    assert all(rows["SAU-H6-294110"][key] is None for key in EVSI_FIELDS)


@pytest.mark.parametrize("field", EVSI_FIELDS)
@pytest.mark.parametrize("value", INVALID_NUMBERS)
def test_evsi_model_rejects_coerced_or_nonfinite_numeric_values(field, value):
    row = dict(opportunity_id=STEEL, scenario_id="SYN-MINISTRY-STEEL-001",
               availability="AVAILABLE", next_fact="Named evidence action",
               **{key: 0.0 for key in EVSI_FIELDS})
    row[field] = value
    with pytest.raises(ValidationError):
        SyntheticEvsiCase(**row)


@pytest.mark.parametrize("field", EVSI_FIELDS)
def test_unavailable_evsi_model_rejects_supplied_numeric_values(field):
    with pytest.raises(ValidationError):
        SyntheticEvsiCase(opportunity_id=STEEL, scenario_id="SYN-TEST",
                          availability="UNAVAILABLE", **{field: 0.0})


@pytest.mark.parametrize("marker", [{"status": "synthetic"}, {"source": "DEMO_GENERATOR"}])
def test_public_evidence_reference_rejects_synthetic_marker(marker):
    row = dict(evidence_id="E-PUBLIC", source="PUBLIC", status="observed",
               evidence_class="D", synthetic_flag=False, supports=())
    row.update(marker)
    with pytest.raises(ValidationError):
        EvidenceReference(**row)


def test_public_class_d_proxy_remains_valid():
    row = EvidenceReference(evidence_id="E-PROXY", source="PUBLIC-PROXY",
                            status="inferred", evidence_class="D",
                            synthetic_flag=False, supports=())
    assert row.evidence_class.value == "D" and row.synthetic_flag is False
    assert row.scenario_id is None and row.display_labels is None


@pytest.mark.parametrize("mutation", [
    "scenarios-null", "scenarios-list", "scenarios-string",
    "unrelated-row-null", "unrelated-row-list", "unrelated-row-string",
    "dependent-row-null", "dependent-row-list", "dependent-row-string",
    "inputs-null", "inputs-list", "inputs-string",
])
def test_dependent_scenario_mapping_errors_return_typed_api_422(monkeypatch, mutation):
    scenarios = deepcopy(synthetic_scenarios())
    kind, shape = mutation.rsplit("-", 1)
    malformed = {"null": None, "list": [], "string": "SECRET-SENTINEL"}[shape]
    if kind == "scenarios":
        scenarios = malformed
    elif kind == "unrelated-row":
        scenarios[STEEL] = malformed
    elif kind == "dependent-row":
        scenarios["SAU-H6-760711"] = malformed
    else:
        scenarios["SAU-H6-760711"]["synthetic_inputs"] = malformed
    # Bypass only the scenario repository; real service/provenance/API guards run.
    monkeypatch.setattr(provenance, "synthetic_scenarios", lambda: scenarios)
    _assert_integrity_response(f"/api/executive/opportunities/{ALUMINIUM}")


@pytest.mark.parametrize("mutation", [
    "missing-step", "missing-vector", "duplicate-evidence", "missing-evidence",
    "unknown-claim", "public-to-synthetic", "simulated-to-public",
    "wrong-scenario", "wrong-class", "wrong-source", "wrong-labels",
])
def test_case_model_rejects_broken_ids_and_evidence_partition(mutation):
    payload = service.build_executive_case(STEEL).model_dump(mode="json")
    public = next(c for c in payload["claims"] if c["claim_id"] == "decision.public")
    simulated = next(c for c in payload["claims"] if c["claim_id"] == "decision.simulated")
    synthetic = next(e for e in payload["evidence_index"] if e["synthetic_flag"])
    if mutation == "missing-step":
        payload["steps"].pop()
    elif mutation == "missing-vector":
        payload["vectors"].pop()
    elif mutation == "duplicate-evidence":
        payload["evidence_index"].append(deepcopy(payload["evidence_index"][0]))
    elif mutation == "missing-evidence":
        payload["evidence_index"] = [e for e in payload["evidence_index"] if e["evidence_id"] != public["evidence_ids"][0]]
    elif mutation == "unknown-claim":
        payload["steps"][0]["claim_ids"].append("ABSENT")
    elif mutation == "public-to-synthetic":
        public["evidence_ids"].append(synthetic["evidence_id"])
    elif mutation == "simulated-to-public":
        simulated["evidence_ids"] = public["evidence_ids"]
    elif mutation == "wrong-scenario":
        synthetic["scenario_id"] = "SYN-FOREIGN"
    elif mutation == "wrong-class":
        synthetic["evidence_class"] = "B"
    elif mutation == "wrong-source":
        synthetic["source"] = "PUBLIC"
    else:
        synthetic["display_labels"] = {"en": "Wrong label", "ar": "غير صحيح"}
    with pytest.raises(ValidationError):
        ExecutiveCase.model_validate(payload)


@pytest.mark.parametrize("opportunity", [STEEL, ALUMINIUM])
def test_removing_one_referenced_synthetic_row_fails_closed(monkeypatch, opportunity):
    case = service.build_executive_case(opportunity)
    referenced = next(e.evidence_id for e in case.evidence_index if e.synthetic_flag
                      and any(e.evidence_id in c.evidence_ids for c in case.claims))
    payload = case.model_dump(mode="json")
    payload["evidence_index"] = [e for e in payload["evidence_index"] if e["evidence_id"] != referenced]
    with pytest.raises(ValidationError):
        ExecutiveCase.model_validate(payload)
    service.clear_executive_caches()

    def mutate(row):
        row["evidence"] = [e for e in row["evidence"] if e["evidence_id"] != referenced]
        row["simulation_decision"]["evidence_ids"] = [referenced]

    _inject_analysis(monkeypatch, mutate, mode="simulated", opportunity=opportunity)
    _assert_integrity_response(f"/api/executive/opportunities/{opportunity}")


@pytest.mark.parametrize("opportunity", ["SAU-H6-294110", "SAU-H6-294120", "SAU-H6-310430", "SAU-H6-310510"])
def test_optional_evsi_absence_does_not_require_an_evsi_evidence_row(opportunity):
    analysis = analyze(opportunity, "simulated")
    assert analysis["evsi"] is None
    assert not any(e["evidence_id"].endswith("::evsi") for e in analysis["evidence"])
    case = service.build_executive_case(opportunity)
    assert case.opportunity.opportunity_id == opportunity
    assert not any(e.evidence_id.endswith("::evsi") for e in case.evidence_index)


OVERSIZED_INTEGERS = [
    pytest.param(10**400, id="positive-oversized-integer"),
    pytest.param(-(10**400), id="negative-oversized-integer"),
]
POLYPROPYLENE = "SAU-H0-390210"
GALVALUME = "SAU-H6-721061"
TINPLATE = "SAU-H6-721012"
OVERFLOW_TOTALS = [
    pytest.param({STEEL: 1e308, TINPLATE: 1e308},
                 "total_approximate_evsi_m_sar", id="positive-total"),
    pytest.param({STEEL: -1e308, TINPLATE: -1e308},
                 "total_approximate_evsi_m_sar", id="negative-total"),
    pytest.param({STEEL: 1e308, POLYPROPYLENE: -1e308, GALVALUME: 1e308},
                 "positive_approximate_evsi_m_sar", id="positive-bucket"),
    pytest.param({STEEL: -1e308, POLYPROPYLENE: 1e308, GALVALUME: -1e308},
                 "non_positive_approximate_evsi_m_sar", id="non-positive-bucket"),
]


@pytest.mark.parametrize("field", EVSI_FIELDS)
@pytest.mark.parametrize("value", OVERSIZED_INTEGERS)
def test_r1_oversized_integer_fails_with_typed_integrity_error(field, value):
    with pytest.raises(ExecutiveIntegrityError, match=f"EVSI {field}"):
        finite_number(value, f"EVSI {field}")


@pytest.mark.parametrize("field", EVSI_FIELDS)
@pytest.mark.parametrize("value", OVERSIZED_INTEGERS)
def test_r1_oversized_integer_returns_typed_api_422(monkeypatch, field, value):
    _inject_analysis(monkeypatch, lambda row: row["evsi"].update({field: value}), mode="simulated")
    _assert_integrity_response("/api/executive/summary")


@pytest.mark.parametrize("field", EVSI_FIELDS)
@pytest.mark.parametrize("value", OVERSIZED_INTEGERS)
def test_r1_evsi_model_still_rejects_oversized_integer(field, value):
    row = dict(opportunity_id=STEEL, scenario_id="SYN-MINISTRY-STEEL-001",
               availability="AVAILABLE", next_fact="Named evidence action",
               **{key: 0.0 for key in EVSI_FIELDS})
    row[field] = value
    with pytest.raises(ValidationError):
        SyntheticEvsiCase(**row)


@pytest.mark.parametrize("value", [0, 0.0, -0.0, 7, -7.5, 1e308, -1e308])
def test_r1_finite_number_preserves_representable_numbers(value):
    result = finite_number(value, "EVSI evidence_cost_m_sar")
    assert type(result) is float
    assert result == value


def _inject_evsi_totals(monkeypatch, values, *, zero_other_available=False):
    def changed(opportunity_id, mode="public"):
        result = deepcopy(analyze(opportunity_id, mode))
        if mode == "simulated" and result.get("evsi") is not None:
            if opportunity_id in values:
                result["evsi"]["approximate_evsi_m_sar"] = values[opportunity_id]
            elif zero_other_available:
                result["evsi"]["approximate_evsi_m_sar"] = 0
        return result

    monkeypatch.setattr(service, "analyze", changed)


@pytest.mark.parametrize("values, field", OVERFLOW_TOTALS)
def test_r1_aggregate_overflow_fails_with_typed_integrity_error(monkeypatch, values, field):
    _inject_evsi_totals(monkeypatch, values)
    pairs = service._analysis_pairs()
    # This order makes the mixed-sign total representable before its bucket fails.
    assert tuple(row[0] for row in pairs[:4]) == (STEEL, POLYPROPYLENE, GALVALUME, TINPLATE)
    with pytest.raises(ExecutiveIntegrityError, match=f"EVSI {field}"):
        service._evsi_summary(pairs)


@pytest.mark.parametrize("values, field", OVERFLOW_TOTALS)
def test_r1_aggregate_overflow_returns_typed_api_422(monkeypatch, values, field):
    _inject_evsi_totals(monkeypatch, values)
    _assert_integrity_response("/api/executive/summary")


@pytest.mark.parametrize("values, expected", [
    pytest.param({}, (0.0, 0.0, 0.0), id="zero"),
    pytest.param({STEEL: 1e308}, (1e308, 1e308, 0.0), id="large-positive"),
    pytest.param({STEEL: -1e308}, (-1e308, 0.0, -1e308), id="large-negative"),
    pytest.param({STEEL: 1e308, POLYPROPYLENE: -1e308},
                 (0.0, 1e308, -1e308), id="successful-cancellation"),
])
@pytest.mark.parametrize("boundary", ["direct", "api"])
def test_r1_representable_aggregates_remain_available(monkeypatch, values, expected, boundary):
    _inject_evsi_totals(monkeypatch, values, zero_other_available=True)
    if boundary == "direct":
        summary = service._evsi_summary(service._analysis_pairs()).model_dump(mode="json")
    else:
        response = TestClient(app).get("/api/executive/summary")
        assert response.status_code == 200
        summary = response.json()["synthetic_evsi"]
    assert tuple(summary[field] for field in (
        "total_approximate_evsi_m_sar", "positive_approximate_evsi_m_sar",
        "non_positive_approximate_evsi_m_sar",
    )) == expected
    assert summary["available_case_count"] == 7
    assert summary["unavailable_case_count"] == 4
    assert all(row["approximate_evsi_m_sar"] is None for row in summary["cases"]
               if row["availability"] == "UNAVAILABLE")
