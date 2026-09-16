from __future__ import annotations

import json
from pathlib import Path

import pytest

import ior_mvp.simulation as simulation
from ior_mvp.cases.build import build_from_brief
from ior_mvp.cases.projection import canonical_bytes
from ior_mvp.config import PROJECT_ROOT, project_config
from ior_mvp.data_repository import (
    clear_repository_caches,
    get_public_case,
    get_synthetic_scenario,
    public_cases,
)
from ior_mvp.decision_engine import analyze
from ior_mvp.economics import approximate_evsi
from ior_mvp.evidence import EvidenceIntegrityError, validate_synthetic_scenario


S15B_CASES = {
    "SAU-H6-294110": "PUBLIC-SAU-H6-294110-2026-09-12",
    "SAU-H6-294120": "PUBLIC-SAU-H6-294120-2026-09-12",
    "SAU-H6-310430": "PUBLIC-SAU-H6-310430-2026-09-12",
    "SAU-H6-310510": "PUBLIC-SAU-H6-310510-2026-09-12",
}


def test_project_lists_eleven_cases_with_s15b_quartet_last() -> None:
    configured = [row["opportunity_id"] for row in project_config()["golden_cases"]]

    assert len(configured) == 11
    assert configured[-4:] == list(S15B_CASES)


def test_s15b_public_snapshots_are_exact_builder_outputs() -> None:
    for opportunity_id, snapshot_id in S15B_CASES.items():
        hs6 = opportunity_id.rsplit("-", 1)[1]
        brief = PROJECT_ROOT / "data" / "cases" / "briefs" / f"CASE-BRIEF-SAU-H6-{hs6}-v1.json"
        snapshot = PROJECT_ROOT / "data" / "snapshots" / "public" / f"{snapshot_id}.json"

        assert snapshot.is_file()
        assert snapshot.read_bytes() == canonical_bytes(build_from_brief(brief))


def test_s15b_public_cases_compute_investigate_without_route() -> None:
    clear_repository_caches()
    try:
        assert len(public_cases()) == 11
        for opportunity_id in S15B_CASES:
            result = analyze(opportunity_id, "public")
            assert result["real_decision"]["state"] == "INVESTIGATE"
            assert result["real_decision"]["route_code"] is None
            assert result["real_decision"]["decision_reason_code"] == (
                "ROUTE_CHANGING_EVIDENCE_UNRESOLVED"
            )
            assert result["capability"]["d_star"] is None
    finally:
        clear_repository_caches()


S15B_SCENARIOS = {
    "SAU-H6-294110": (
        "SYN-MINISTRY-PENICILLIN-API-001.json",
        "SYN-MINISTRY-PENICILLIN-API-001",
        "ADVANCE",
        1,
        None,
    ),
    "SAU-H6-294120": (
        "SYN-MINISTRY-STREPTOMYCIN-API-001.json",
        "SYN-MINISTRY-STREPTOMYCIN-API-001",
        "REJECT",
        0,
        "EX-03_UNSATISFIABLE_HARD_GATE",
    ),
    "SAU-H6-310430": (
        "SYN-MINISTRY-SOP-001.json",
        "SYN-MINISTRY-SOP-001",
        "ADVANCE",
        2,
        None,
    ),
    "SAU-H6-310510": (
        "SYN-MINISTRY-FERT-RETAIL-PACKS-001.json",
        "SYN-MINISTRY-FERT-RETAIL-PACKS-001",
        "REJECT",
        0,
        "EX-01_HETEROGENEOUS_RESIDUAL",
    ),
}


def _scenario_file(filename: str) -> dict:
    path = PROJECT_ROOT / "data" / "synthetic" / filename
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"scenario is not authored: {filename}"
    return json.loads(text)


@pytest.mark.parametrize(
    ("opportunity_id", "scenario_spec"),
    list(S15B_SCENARIOS.items()),
)
def test_s15b_scenarios_are_valid_paired_class_d_records(
    opportunity_id: str,
    scenario_spec: tuple[str, str, str, int, str | None],
) -> None:
    filename, scenario_id, expected_state, expected_route, _ = scenario_spec
    scenario = _scenario_file(filename)

    validate_synthetic_scenario(scenario)
    assert scenario["scenario_id"] == scenario_id
    assert scenario["opportunity_id"] == opportunity_id
    assert scenario["ground_truth"] == {
        "expected_simulation_state": expected_state,
        "expected_route_code": expected_route,
        "basis": scenario["ground_truth"]["basis"],
    }
    assert scenario["synthetic_flag"] is True
    assert scenario["evidence_class"] == "D"
    assert scenario["source"] == "DEMO_GENERATOR"
    assert "shared_enabler" not in scenario["synthetic_inputs"]


@pytest.mark.parametrize(
    ("opportunity_id", "scenario_spec"),
    list(S15B_SCENARIOS.items()),
)
def test_s15b_simulations_compute_reviewed_states_routes_and_exclusions(
    opportunity_id: str,
    scenario_spec: tuple[str, str, str, int, str | None],
) -> None:
    _, scenario_id, expected_state, expected_route, expected_exclusion = scenario_spec
    clear_repository_caches()
    try:
        scenario = get_synthetic_scenario(opportunity_id)
        assert scenario is not None
        assert scenario["scenario_id"] == scenario_id
        public = analyze(opportunity_id, "public")
        simulated = analyze(opportunity_id, "simulated")
    finally:
        clear_repository_caches()

    assert simulated["real_decision"] == public["real_decision"]
    assert simulated["simulation_decision"]["state"] == expected_state
    assert simulated["simulation_decision"]["route_code"] == expected_route
    assert simulated["integrity"]["ground_truth_backtest"]["match"] is True
    assert simulated["route_hypotheses"][8]["reason_codes"] == ["GRAPH_REQUIRED"]
    assert all(
        row["evidence_class"] == "D"
        for row in simulated["simulation_decision"]["evidence_class_assessment"].values()
    )
    satisfied = {
        row["code"] for row in simulated["hard_exclusions"] if row["status"] == "SATISFIED"
    }
    if expected_exclusion is None:
        assert satisfied == set()
        assert simulated["route_hypotheses"][expected_route]["status"] == "passes"
    else:
        assert satisfied == {expected_exclusion}
        assert simulated["simulation_decision"]["decision_reason_code"] == (
            "HARD_EXCLUSION_SATISFIED"
        )


@pytest.mark.parametrize("opportunity_id", list(S15B_SCENARIOS))
def test_s15b_absent_evsi_skips_calculation_and_returns_none(
    opportunity_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scenario = _scenario_file(S15B_SCENARIOS[opportunity_id][0])
    assert "evsi" not in scenario["synthetic_inputs"]

    def unexpected(_: dict) -> dict:
        raise AssertionError("approximate_evsi must not run for an absent block")

    monkeypatch.setattr(simulation, "approximate_evsi", unexpected)
    branch = simulation.simulate(get_public_case(opportunity_id), scenario)

    assert branch["evsi"] is None


@pytest.mark.parametrize("invalid", [None, [], "invalid", False, 1])
def test_s15b_supplied_non_mapping_evsi_remains_invalid(invalid: object) -> None:
    scenario = _scenario_file(S15B_SCENARIOS["SAU-H6-294110"][0])
    scenario["synthetic_inputs"]["evsi"] = invalid

    with pytest.raises(EvidenceIntegrityError, match="evsi must be a mapping"):
        simulation.simulate(get_public_case("SAU-H6-294110"), scenario)


@pytest.mark.parametrize(
    "evsi",
    [
        {},
        {"route_change_probability": 0.5},
        {
            "route_change_probability": None,
            "value_difference_m_sar": 10.0,
            "evidence_cost_m_sar": 1.0,
            "delay_cost_m_sar": 1.0,
        },
        {
            "route_change_probability": "invalid",
            "value_difference_m_sar": 10.0,
            "evidence_cost_m_sar": 1.0,
            "delay_cost_m_sar": 1.0,
        },
    ],
)
def test_s15b_supplied_incomplete_or_invalid_evsi_remains_invalid(
    evsi: dict,
) -> None:
    scenario = _scenario_file(S15B_SCENARIOS["SAU-H6-294110"][0])
    scenario["synthetic_inputs"]["evsi"] = evsi

    with pytest.raises(EvidenceIntegrityError, match="evsi contains an invalid value"):
        simulation.simulate(get_public_case("SAU-H6-294110"), scenario)


def test_existing_scenarios_retain_exact_evsi_calculations(
    s16b_simulate,
) -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
        "SAU-H6-721061",
        "SAU-H6-721012",
        "SAU-H6-760711",
        "SAU-H6-760429",
        "SAU-H6-392010",
    ):
        scenario = get_synthetic_scenario(opportunity_id)
        assert scenario is not None
        expected = approximate_evsi(scenario["synthetic_inputs"]["evsi"])
        assert s16b_simulate(
            get_public_case(opportunity_id), scenario
        )["evsi"] == expected


def test_supplied_zero_and_negative_evsi_stay_numeric() -> None:
    scenario = _scenario_file(S15B_SCENARIOS["SAU-H6-294110"][0])
    for value_difference, evidence_cost, expected in (
        (4.0, 2.0, 0.0),
        (2.0, 3.0, -2.0),
    ):
        scenario["synthetic_inputs"]["evsi"] = {
            "route_change_probability": 0.5,
            "value_difference_m_sar": value_difference,
            "evidence_cost_m_sar": evidence_cost,
            "delay_cost_m_sar": 0.0,
        }
        result = simulation.simulate(
            get_public_case("SAU-H6-294110"),
            scenario,
        )["evsi"]
        assert result["approximate_evsi_m_sar"] == expected
        assert result["positive"] is (expected > 0)
        assert result["next_fact"] is None
