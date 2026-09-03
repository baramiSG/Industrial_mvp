from __future__ import annotations

from copy import deepcopy

import pytest

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


def test_supported_version_is_2_0_0_only() -> None:
    assert SUPPORTED_SCENARIO_CONTRACT_VERSIONS == frozenset({"2.0.0"})
    validate_simulation_contract(_steel())


@pytest.mark.parametrize("version", ["1.1.0", "2.1.0"])
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
    scenario["synthetic_inputs"]["shared_enabler"] = {}
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
