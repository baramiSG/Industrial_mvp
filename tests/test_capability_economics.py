from __future__ import annotations

import pytest

from ior_mvp.capability import effective_qualified_capacity, evaluate_capability
from ior_mvp.data_repository import get_public_case, get_synthetic_scenario
from ior_mvp.decision_engine import analyze
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

    result = evaluate_capability(
        "coated_steel",
        scenario["synthetic_inputs"]["capability_states"],
        {"gate": gate_value},
    )

    assert result["unresolved_hard_gates"] == expected_unresolved


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
