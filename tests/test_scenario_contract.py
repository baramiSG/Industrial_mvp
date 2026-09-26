from __future__ import annotations

from copy import deepcopy

import pytest

import ior_mvp.scenario_contract as scenario_contract
from ior_mvp.data_repository import get_public_case, get_synthetic_scenario
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.scenario_contract import (
    SUPPORTED_SCENARIO_CONTRACT_VERSIONS,
    decision_narrative_for_state,
    project_simulated_case,
    validate_scenario_pairing,
    validate_simulation_contract,
)
from ior_mvp.simulation import capacity_projection, simulation_capability


def _steel() -> dict:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    return deepcopy(scenario)


def test_supported_versions_are_2_0_0_and_2_1_0() -> None:
    assert SUPPORTED_SCENARIO_CONTRACT_VERSIONS == frozenset({"2.0.0", "2.1.0"})
    validate_simulation_contract(_steel())


@pytest.mark.parametrize("version", ["1.1.0", "2.2.0"])
def test_unsupported_versions_rejected(version: str) -> None:
    scenario = _steel()
    scenario["scenario_version"] = version
    with pytest.raises(
        EvidenceIntegrityError,
        match="unsupported",
    ):
        validate_simulation_contract(scenario)


def test_unknown_synthetic_input_key_rejected() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["unknown_block"] = {}
    with pytest.raises(
        EvidenceIntegrityError,
        match="unknown keys",
    ):
        validate_simulation_contract(scenario)


def test_invalid_expansion_assumption_rejected() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["expansion_assumption"] = {
        "planned_nameplate_kt": -1,
        "commissioning_year": "x",
        "disclosed": False,
    }
    with pytest.raises(EvidenceIntegrityError) as captured:
        validate_simulation_contract(scenario)
    assert "expansion_assumption" in str(captured.value)


def test_route_8_record_rejected() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["route_evidence"].append(
        {
            "route_code": 8,
            "binding_constraint": "capacity_or_availability",
            "basis": "forbidden",
        }
    )
    with pytest.raises(
        EvidenceIntegrityError,
        match="route_code 8",
    ):
        validate_simulation_contract(scenario)


def test_route_5_inherited_fields_rejected() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["route_evidence"][0]["hurdle_rate"] = 0.12
    with pytest.raises(
        EvidenceIntegrityError,
        match="route-5 record must not declare",
    ):
        validate_simulation_contract(scenario)


def test_narrative_placeholder_rejected() -> None:
    scenario = _steel()
    scenario["decision_narrative"]["ADVANCE"]["headline"]["en"] = (
        "bad {placeholder}"
    )
    with pytest.raises(
        EvidenceIntegrityError,
        match="placeholder",
    ):
        validate_simulation_contract(scenario)


def test_decision_narrative_for_state_returns_mapping_or_none() -> None:
    scenario = _steel()
    assert decision_narrative_for_state(scenario, "ADVANCE") is not None
    assert decision_narrative_for_state(scenario, "REJECT") is None


def test_project_simulated_case_steel_projection() -> None:
    scenario = _steel()
    public = get_public_case("SAU-H0-721049")
    capacity, _, _, _ = capacity_projection(scenario["synthetic_inputs"])
    capability = simulation_capability(public, scenario["synthetic_inputs"])
    composite = project_simulated_case(
        public,
        scenario,
        capacity,
        capability,
    )
    assert composite["opportunity"]["decision_object_status"] == "resolved"
    assert composite["domestic_capability"]["unresolved_hard_gates"] == []
    demand = composite["decision_inputs"]["target_specification_demand"]
    assert demand["quantity_kt"] == pytest.approx(104.0)
    assert demand["downside_quantity_kt"] == pytest.approx(100.0)
    route = composite["decision_inputs"]["route_evidence"][0]
    economics = scenario["synthetic_inputs"]["economics"]
    assert route["downside_cash_flows_m_sar"] == economics[
        "cash_flows_without_support"
    ]
    assert route["hurdle_rate"] == economics["hurdle_rate"]


def test_validate_scenario_pairing_rejects_unknown_gate_name() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["decision_specific_hard_gates"] = {
        "unknown_gate": "resolved",
    }
    with pytest.raises(
        EvidenceIntegrityError,
        match="unknown to public case",
    ):
        validate_scenario_pairing(scenario, get_public_case("SAU-H0-721049"))


def _s16b_shared_scenario() -> dict:
    scenario = get_synthetic_scenario("SAU-H6-760711")
    assert scenario is not None
    scenario = deepcopy(scenario)
    scenario["scenario_version"] = "2.1.0"
    scenario["synthetic_inputs"]["shared_enabler"] = {
        "enabler_id": "ENABLER-SYN-TEST-001",
        "enabler_kind": "input_supply",
        "label": {"en": "Test shared input", "ar": "مدخل مشترك اختباري"},
        "enabler_cost_m_sar": 25.0,
        "valuation_route_code": 6,
        "constraint_classes_addressed": ["capability_or_technology"],
        "removes_binding_constraint": True,
        "unlock_probability": 0.6,
        "dependency_share": 0.5,
        "components": {
            "technical_feasibility_confirmed": True,
            "investment_already_approved_or_financed": False,
            "proceeds_without_intervention": False,
            "policy_prohibition_identified": False,
            "distortion_unacceptable": False,
            "intervention_proportionate_to_constraint": True,
            "competition": {
                "existing_effective_capacity_kt": 2.5,
                "proposed_incremental_capacity_kt": 39.6,
                "downside_demand_kt": 39.2,
            },
        },
        "basis": "DEMO_GENERATOR test declaration",
    }
    return scenario


def test_s16b_scenario_2_1_shared_enabler_is_supported() -> None:
    scenario = _s16b_shared_scenario()
    assert "2.1.0" in scenario_contract.SUPPORTED_SCENARIO_CONTRACT_VERSIONS
    scenario_contract.validate_simulation_contract(scenario)
    declaration = scenario_contract.validate_shared_enabler(scenario)
    assert declaration == scenario["synthetic_inputs"]["shared_enabler"]


def test_s16b_explicit_valuation_is_independent_of_ground_truth() -> None:
    scenario = _s16b_shared_scenario()
    code, value = scenario_contract.shared_enabler_valuation(scenario)
    assert (code, value) == (6, 172.0)
    scenario["ground_truth"]["expected_route_code"] = 4
    assert scenario_contract.shared_enabler_valuation(scenario) == (6, 172.0)


@pytest.mark.parametrize("value", [True, 0, 8, 7])
def test_s16b_invalid_valuation_references_fail(value: object) -> None:
    scenario = _s16b_shared_scenario()
    scenario["synthetic_inputs"]["shared_enabler"][
        "valuation_route_code"
    ] = value
    with pytest.raises(EvidenceIntegrityError, match="valuation_route_code"):
        scenario_contract.validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("unlock_probability",), float("nan")),
        (("dependency_share",), True),
        (("enabler_cost_m_sar",), True),
        (("removes_binding_constraint",), 1),
        (("constraint_classes_addressed",), ["capability_or_technology"] * 2),
        (("constraint_classes_addressed",), [[]]),
        (("components", "technical_feasibility_confirmed"), 1),
        (("components", "competition", "downside_demand_kt"), 0.0),
    ],
)
def test_s16b_malformed_shared_enabler_values_fail(
    path: tuple[str, ...],
    value: object,
) -> None:
    scenario = _s16b_shared_scenario()
    target = scenario["synthetic_inputs"]["shared_enabler"]
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(EvidenceIntegrityError):
        scenario_contract.validate_simulation_contract(scenario)


def test_s16b_unknown_and_missing_shared_enabler_fields_fail() -> None:
    unknown = _s16b_shared_scenario()
    unknown["synthetic_inputs"]["shared_enabler"]["raw_delta_nv"] = 1
    with pytest.raises(EvidenceIntegrityError, match="fields are invalid"):
        scenario_contract.validate_simulation_contract(unknown)
    missing = _s16b_shared_scenario()
    del missing["synthetic_inputs"]["shared_enabler"]["basis"]
    with pytest.raises(EvidenceIntegrityError, match="fields are invalid"):
        scenario_contract.validate_simulation_contract(missing)


def test_s16b_unavailable_and_nonpositive_valuation_fail() -> None:
    for value in ("UNAVAILABLE", {"domestic_value_added": -1000.0}):
        scenario = _s16b_shared_scenario()
        record = next(
            row
            for row in scenario["synthetic_inputs"]["route_evidence"]
            if row["route_code"] == 6
        )
        record["national_value"] = value
        with pytest.raises(EvidenceIntegrityError, match="positive"):
            scenario_contract.validate_simulation_contract(scenario)


def test_s16b_duplicate_route_and_membership_fail() -> None:
    scenario = _s16b_shared_scenario()
    selected = next(
        row
        for row in scenario["synthetic_inputs"]["route_evidence"]
        if row["route_code"] == 6
    )
    scenario["synthetic_inputs"]["route_evidence"].append(deepcopy(selected))
    with pytest.raises(EvidenceIntegrityError, match="duplicate route_code"):
        scenario_contract.validate_simulation_contract(scenario)
    first = _s16b_shared_scenario()
    second = deepcopy(first)
    second["scenario_id"] = "SYN-TEST-DUPLICATE-DEPENDENT"
    with pytest.raises(EvidenceIntegrityError, match="duplicate dependent"):
        scenario_contract.validate_shared_enabler_consistency([first, second])


def test_s16b_governed_aluminium_declarations_are_exact_and_consistent() -> None:
    foil = get_synthetic_scenario("SAU-H6-760711")
    profiles = get_synthetic_scenario("SAU-H6-760429")
    assert foil is not None and profiles is not None
    scenario_contract.validate_shared_enabler_consistency([foil, profiles])
    foil_block = foil["synthetic_inputs"]["shared_enabler"]
    profiles_block = profiles["synthetic_inputs"]["shared_enabler"]
    assert foil_block["enabler_id"] == profiles_block["enabler_id"] == (
        "ENABLER-SYN-ALU-CASTHOUSE-001"
    )
    assert foil_block["valuation_route_code"] == 6
    assert profiles_block["valuation_route_code"] == 4
    assert (foil_block["unlock_probability"], foil_block["dependency_share"]) == (
        0.6,
        0.5,
    )
    assert (
        profiles_block["unlock_probability"],
        profiles_block["dependency_share"],
    ) == (0.7, 0.4)
    assert foil_block["enabler_cost_m_sar"] == 25.0
    assert foil_block["components"] == profiles_block["components"]
    assert scenario_contract.shared_enabler_valuation(foil) == (6, 172.0)
    assert scenario_contract.shared_enabler_valuation(profiles) == (4, 31.0)


@pytest.mark.parametrize("field", ["unlock_probability", "dependency_share"])
def test_s16b_declaration_rejects_zero_probability_or_share(field: str) -> None:
    scenario = _s16b_shared_scenario()
    scenario["synthetic_inputs"]["shared_enabler"][field] = 0.0
    with pytest.raises(EvidenceIntegrityError, match=field):
        scenario_contract.validate_simulation_contract(scenario)


def test_s16b_declaration_rejects_unknown_enabler_kind() -> None:
    scenario = _s16b_shared_scenario()
    scenario["synthetic_inputs"]["shared_enabler"][
        "enabler_kind"
    ] = "UNSUPPORTED_KIND"
    with pytest.raises(EvidenceIntegrityError, match="enabler_kind"):
        scenario_contract.validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    ("declaration", "expected_status"),
    [
        ("known_failure: effluent", "KNOWN_FAILURE"),
        ("known failure: effluent", "KNOWN_FAILURE"),
        ("not_applicable to this profile", "NOT_APPLICABLE"),
        ("not applicable to resin production", "NOT_APPLICABLE"),
        ("pending prose", "UNAVAILABLE"),
    ],
)
def test_simulated_profile_gate_uses_one_prefix_classifier(
    declaration: str,
    expected_status: str,
) -> None:
    scenario = _steel()
    public = get_public_case("SAU-H0-721049")
    gate_name = next(iter(scenario["synthetic_inputs"]["hard_gates"]))
    scenario["synthetic_inputs"]["hard_gates"][gate_name] = declaration
    capacity, _, _, _ = capacity_projection(scenario["synthetic_inputs"])
    capability = simulation_capability(public, scenario["synthetic_inputs"])
    composite = project_simulated_case(public, scenario, capacity, capability)
    status = composite["domestic_capability"]["profile_hard_gates"][gate_name][
        "status"
    ]
    assert status == expected_status
    assert scenario["synthetic_inputs"]["hard_gates"][gate_name] == declaration


def test_streptomycin_known_failure_keeps_both_sources_and_is_not_unknown() -> None:
    scenario = get_synthetic_scenario("SAU-H6-294120")
    assert scenario is not None
    scenario = deepcopy(scenario)
    public = get_public_case("SAU-H6-294120")
    public_rows = deepcopy(
        public["domestic_capability"]["unresolved_hard_gates"]
    )
    raw_decision = scenario["synthetic_inputs"]["decision_specific_hard_gates"][
        "effluent"
    ]
    capacity, _, _, _ = capacity_projection(scenario["synthetic_inputs"])
    capability = simulation_capability(public, scenario["synthetic_inputs"])
    composite = project_simulated_case(public, scenario, capacity, capability)
    rows = composite["domestic_capability"]["unresolved_hard_gates"]
    effluent = [row for row in rows if row["name"] == "effluent"]

    assert capability["known_hard_gate_failures"] == ["effluent"]
    assert capability["unresolved_hard_gates"] == []
    assert len(effluent) == 1
    assert effluent[0]["state"] == "known_failure"
    assert (
        composite["domestic_capability"]["profile_hard_gates"]["effluent"][
            "status"
        ]
        == "KNOWN_FAILURE"
    )
    assert (
        composite["domestic_capability"]["profile_hard_gates"]["effluent"][
            "evidence_ids"
        ]
        == ["SYN-MINISTRY-STREPTOMYCIN-API-001::hard_gates"]
    )
    assert raw_decision == (
        "known failure: synthetic environmental-effluent gate is unsatisfiable"
    )
    assert public["domestic_capability"]["unresolved_hard_gates"] == public_rows
