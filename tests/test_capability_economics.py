from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.capability import effective_qualified_capacity, evaluate_capability
from ior_mvp.data_repository import get_public_case, get_synthetic_scenario
from ior_mvp.decision_engine import analyze
from ior_mvp.simulation import simulation_capability
from ior_mvp.economics import approximate_evsi, incremental_national_value, minimum_effective_support, npv


def test_effective_qualified_capacity_formula() -> None:
    result = effective_qualified_capacity(250, 0.92, 0.94, 0.38, 0.70)
    assert result == pytest.approx(57.5092, abs=1e-6)


def test_public_steel_dstar_is_withheld_for_unresolved_hard_gates() -> None:
    case = get_public_case("SAU-H0-721049")
    result = evaluate_capability(
        case["opportunity"]["sector_profile"],
        case["domestic_capability"]["public_dimension_states"],
        case["domestic_capability"]["unresolved_hard_gates"],
    )
    assert result["known_weight_coverage"] >= 0.70
    assert result["internal_d_star_before_gate"] is not None
    assert result["d_star"] is None
    assert result["route_publishable"] is False


def test_unknowns_cannot_improve_adjacency() -> None:
    mostly_unknown = {
        "feedstock_chemistry": 0,
        "core_process_route": "U",
        "equipment_envelope": "U",
        "finishing_spec_control": "U",
        "qa_lab_metrology": "U",
        "certification_customer_qualification": "U",
        "capacity_time_window": "U",
        "utilities_ehs_permitting": "U",
        "skills_market_integration": "U",
    }
    result = evaluate_capability("coated_steel", mostly_unknown, [])
    assert result["known_weight_coverage"] == pytest.approx(0.05)
    assert result["internal_d_star_before_gate"] == pytest.approx(0.475)
    assert result["d_star"] is None


def test_simulated_steel_capability_is_incremental_upgrade() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    inputs = scenario["synthetic_inputs"]
    result = evaluate_capability("coated_steel", inputs["capability_states"], inputs["hard_gates"])
    assert result["route_publishable"] is True
    assert result["d_star"] == pytest.approx(0.2667, abs=1e-4)
    assert result["route_band"]["code"] == "incremental_upgrade"


@pytest.mark.parametrize(
    ("gate_value", "expected_unresolved"),
    [
        ("resolved", []),
        ("resolved with upgrade", []),
        ("not applicable", []),
        ("not applicable to resin production", []),
        ("NOT_APPLICABLE", []),
        ("pending", ["gate"]),
        ("unresolved", ["gate"]),
        ("", ["gate"]),
    ],
)
def test_hard_gate_status_prefixes(
    gate_value: str,
    expected_unresolved: list[str],
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    hard_gates = dict(scenario["synthetic_inputs"]["hard_gates"])
    gate_name = next(iter(hard_gates))
    hard_gates[gate_name] = gate_value

    result = evaluate_capability(
        "coated_steel",
        scenario["synthetic_inputs"]["capability_states"],
        hard_gates,
    )

    assert result["unresolved_hard_gates"] == [
        gate_name for _ in expected_unresolved
    ]


def test_polypropylene_not_applicable_gate_publishes_capability() -> None:
    result = analyze("SAU-H0-390210", "simulated")

    assert result["capability"]["unresolved_hard_gates"] == []
    assert result["capability"]["route_publishable"] is True
    assert result["capability"]["d_star"] == 0.0
    assert result["capability"]["route_band"]["code"] == (
        "immediate_adjacency"
    )
    assert result["simulation_decision"]["state"] == "REJECT"
    assert result["simulation_decision"]["route_code"] == 0


def test_minimum_effective_support_is_18m() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    economics = scenario["synthetic_inputs"]["economics"]
    result = minimum_effective_support(economics["cash_flows_without_support"], economics["hurdle_rate"])
    assert result["unsupported_npv_m"] == pytest.approx(-18.0, abs=1e-3)
    assert result["unsupported_irr"] == pytest.approx(0.095, abs=1e-5)
    assert result["minimum_effective_support_m"] == pytest.approx(18.0)
    assert result["supported_irr"] == pytest.approx(0.12, abs=5e-4)


def test_national_value_and_evsi() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    inputs = scenario["synthetic_inputs"]
    national_value = incremental_national_value(inputs["economics"]["national_value"])
    evsi = approximate_evsi(inputs["evsi"])
    assert national_value["incremental_national_value_m_sar"] == pytest.approx(198.0)
    assert national_value["positive"] is True
    assert evsi["approximate_evsi_m_sar"] == pytest.approx(129.3)
    assert evsi["positive"] is True


def test_national_value_requires_all_components() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    components = dict(
        scenario["synthetic_inputs"]["economics"]["national_value"]
    )
    del components["displacement"]

    with pytest.raises(ValueError, match="displacement"):
        incremental_national_value(components)


def test_evsi_requires_all_inputs() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    evsi_inputs = dict(scenario["synthetic_inputs"]["evsi"])
    del evsi_inputs["route_change_probability"]

    with pytest.raises(
        ValueError,
        match="route_change_probability",
    ):
        approximate_evsi(evsi_inputs)


def test_npv_rejects_invalid_rate() -> None:
    with pytest.raises(ValueError):
        npv(-1, [-1, 2])


@pytest.mark.parametrize(
    ("gate_value", "expected_status", "unresolved"),
    [
        ("resolved", "RESOLVED", False),
        ("Resolved with upgrade", "RESOLVED", False),
        ("known failure: unsatisfiable", "KNOWN_FAILURE", False),
        ("known_failure: unsatisfiable", "KNOWN_FAILURE", False),
        ("Known Failure", "KNOWN_FAILURE", False),
        ("not applicable to resin production", "NOT_APPLICABLE", False),
        ("not_applicable", "NOT_APPLICABLE", False),
        ("NOT_APPLICABLE", "NOT_APPLICABLE", False),
        ("pending review", "UNAVAILABLE", True),
        ("", "UNAVAILABLE", True),
    ],
)
def test_profile_gate_prefix_classifier_keeps_non_applicable_meaning(
    gate_value: str,
    expected_status: str,
    unresolved: bool,
) -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    hard_gates = dict(scenario["synthetic_inputs"]["hard_gates"])
    gate_name = next(iter(hard_gates))
    hard_gates[gate_name] = gate_value

    result = evaluate_capability(
        "coated_steel",
        scenario["synthetic_inputs"]["capability_states"],
        hard_gates,
    )

    assert result["profile_hard_gates"][gate_name] == expected_status
    assert (gate_name in result["unresolved_hard_gates"]) is unresolved
    assert (gate_name in result["known_hard_gate_failures"]) is (
        expected_status == "KNOWN_FAILURE"
    )
    if expected_status == "NOT_APPLICABLE":
        assert result["profile_hard_gates"][gate_name] != "RESOLVED"


def test_typed_not_applicable_dict_does_not_become_resolved_or_unknown() -> None:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    hard_gates = {
        name: {"status": "RESOLVED", "basis": "declared"}
        for name in scenario["synthetic_inputs"]["hard_gates"]
    }
    gate_name = next(iter(hard_gates))
    hard_gates[gate_name] = {
        "status": "NOT_APPLICABLE",
        "basis": "profile does not apply",
    }

    result = evaluate_capability(
        "coated_steel",
        scenario["synthetic_inputs"]["capability_states"],
        hard_gates,
    )

    assert result["profile_hard_gates"][gate_name] == "NOT_APPLICABLE"
    assert gate_name not in result["unresolved_profile_hard_gates"]
    assert gate_name not in result["unresolved_hard_gates"]
    assert gate_name not in result["known_hard_gate_failures"]
    assert result["route_publishable"] is True


def test_decision_specific_known_failure_survives_as_known_failure() -> None:
    public = get_public_case("SAU-H6-294120")
    scenario = get_synthetic_scenario("SAU-H6-294120")
    assert scenario is not None
    raw_profile = scenario["synthetic_inputs"]["hard_gates"]["effluent"]
    raw_decision = scenario["synthetic_inputs"]["decision_specific_hard_gates"][
        "effluent"
    ]

    result = simulation_capability(public, scenario["synthetic_inputs"])

    assert result["unresolved_hard_gates"] == []
    assert result["unresolved_profile_hard_gates"] == []
    assert result["unresolved_decision_specific_hard_gates"] == []
    assert result["known_hard_gate_failures"] == ["effluent"]
    assert result["profile_hard_gates"]["effluent"] == "KNOWN_FAILURE"
    assert result["decision_specific_hard_gates"]["effluent"] == "KNOWN_FAILURE"
    assert scenario["synthetic_inputs"]["hard_gates"]["effluent"] == raw_profile
    assert (
        scenario["synthetic_inputs"]["decision_specific_hard_gates"]["effluent"]
        == raw_decision
    )


def test_overlapping_public_gate_names_dedupe_only_the_summary() -> None:
    result = analyze("SAU-H6-294110", "public")
    capability = result["capability"]
    profile_names = [
        name
        for name, status in capability["profile_hard_gates"].items()
        if status == "UNAVAILABLE"
    ]
    decision_names = capability["unresolved_decision_specific_hard_gates"]

    assert capability["unresolved_profile_hard_gates"] == [
        "named_molecule_and_synthesis_route",
        "gmp",
        "containment",
        "impurity_control",
        "analytical_validation",
        "effluent",
        "ip_fto",
    ]
    assert decision_names == capability["unresolved_profile_hard_gates"]
    assert capability["unresolved_hard_gates"] == profile_names
    assert len(capability["unresolved_hard_gates"]) == len(set(decision_names))
    assert len(profile_names) + len(decision_names) == 14


@pytest.mark.parametrize(
    ("declared_names", "expected_unresolved"),
    [
        (
            ("customer/application qualification", "effective spare capacity and allocation"),
            ["exact imported specification"],
        ),
        (
            (),
            [
                "exact imported specification",
                "customer/application qualification",
                "effective spare capacity and allocation",
            ],
        ),
    ],
)
def test_omitted_required_decision_gates_block_capability(
    declared_names: tuple[str, ...],
    expected_unresolved: list[str],
) -> None:
    public = get_public_case("SAU-H0-721049")
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    inputs = deepcopy(scenario["synthetic_inputs"])
    original = inputs["decision_specific_hard_gates"]
    inputs["decision_specific_hard_gates"] = {
        name: original[name] for name in declared_names
    }

    result = simulation_capability(public, inputs)

    assert result["unresolved_decision_specific_hard_gates"] == expected_unresolved
    assert result["unresolved_hard_gates"] == expected_unresolved
    assert result["route_publishable"] is False
    assert result["d_star"] is None
    assert all(
        result["decision_specific_hard_gates"][name] == "UNAVAILABLE"
        for name in expected_unresolved
    )
    assert inputs["decision_specific_hard_gates"] == {
        name: original[name] for name in declared_names
    }


def test_omitted_decision_gate_remains_unknown_beside_known_failure() -> None:
    public = get_public_case("SAU-H6-294120")
    scenario = get_synthetic_scenario("SAU-H6-294120")
    assert scenario is not None
    inputs = deepcopy(scenario["synthetic_inputs"])
    del inputs["decision_specific_hard_gates"]["gmp"]

    result = simulation_capability(public, inputs)

    assert result["unresolved_decision_specific_hard_gates"] == ["gmp"]
    assert result["known_hard_gate_failures"] == ["effluent"]
    assert result["decision_specific_hard_gates"]["gmp"] == "UNAVAILABLE"
    assert result["decision_specific_hard_gates"]["effluent"] == "KNOWN_FAILURE"
    assert result["route_publishable"] is False
    assert result["d_star"] is None
