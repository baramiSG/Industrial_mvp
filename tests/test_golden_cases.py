from __future__ import annotations

import pytest

from ior_mvp.decision_engine import analyze


def test_steel_public_golden_case() -> None:
    result = analyze("SAU-H0-721049", "public")
    assert result["real_decision"]["state"] == "INVESTIGATE"
    assert result["active_decision"]["state"] == "INVESTIGATE"
    assert result["real_decision"]["route_code"] is None
    assert result["capability"]["d_star"] is None
    assert not any(
        row.get("synthetic_flag") is True
        for row in result["rules"]
    )
    fired = {row["rule_id"]: row["fired"] for row in result["rules"]}
    assert fired["R1-D"] is True
    assert fired["R2"] is True
    assert fired["R3"] is True
    assert fired["R4-D"] is True
    assert fired["R9-S"] is True
    r2 = next(row for row in result["rules"] if row["rule_id"] == "R2")
    r11 = next(row for row in result["rules"] if row["rule_id"] == "R11")
    assert r2["metrics"]["observed_span_years"] == 1
    assert r2["metrics"]["quantity_cagr"] == pytest.approx(0.6565)
    assert r11["execution"] == "FULL"
    assert r11["fired"] is False
    assert r11["metrics"][
        "computed_export_import_value_ratio"
    ] == pytest.approx(0.1144)


def test_steel_simulated_golden_case() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    assert result["real_decision"]["state"] == "INVESTIGATE"
    assert result["simulation_decision"]["state"] == "ADVANCE"
    assert result["active_decision"]["route_code"] == 5
    assert result["simulation_decision"]["route_code"] == 5
    assert result["capacity"]["effective_qualified_capacity_kt"] == pytest.approx(57.509, abs=1e-3)
    assert result["capacity"]["specification_adjusted_gap_kt"] == pytest.approx(46.491, abs=1e-3)
    assert result["capability"]["d_star"] == pytest.approx(
        0.2667,
        abs=1e-4,
    )
    assert result["capability"]["route_band"]["code"] == (
        "incremental_upgrade"
    )
    assert result["economics"][
        "unsupported_npv_m"
    ] == pytest.approx(-18.0)
    assert result["economics"]["unsupported_irr"] == pytest.approx(
        0.095,
        abs=1e-5,
    )
    assert result["economics"]["minimum_effective_support_m"] == pytest.approx(18.0)
    assert result["economics"]["national_value"]["incremental_national_value_m_sar"] == pytest.approx(198.0)
    assert result["competition"]["post_entry_capacity_to_downside_demand"] < 1.25
    assert result["competition"][
        "post_entry_capacity_to_downside_demand"
    ] == pytest.approx(1.0751)
    assert result["competition"]["warning_fires"] is False
    assert result["simulation_scenario"]["scenario_version"] == (
        "2.0.0"
    )
    assert result["integrity"]["ground_truth_backtest"] == {
        "expected": {"state": "ADVANCE", "route_code": 5},
        "actual": {"state": "ADVANCE", "route_code": 5},
        "match": True,
    }
    assert result["integrity"]["real_decision_unchanged_after_simulation"] is True


def test_polypropylene_public_golden_case() -> None:
    result = analyze("SAU-H0-390210", "public")
    assert result["real_decision"]["state"] == "REJECT"
    assert result["real_decision"]["route_code"] == 0
    assert not any(
        row.get("synthetic_flag") is True
        for row in result["rules"]
    )
    fired = {row["rule_id"]: row["fired"] for row in result["rules"]}
    assert fired["R1-D"] is True
    assert fired["R2"] is False
    assert fired["R11"] is True
    r2 = next(row for row in result["rules"] if row["rule_id"] == "R2")
    r11 = next(row for row in result["rules"] if row["rule_id"] == "R11")
    assert r2["metrics"]["quantity_cagr"] == pytest.approx(-0.1642)
    assert r11["execution"] == "FULL"
    assert r11["metrics"][
        "computed_export_import_value_ratio"
    ] == pytest.approx(50.6013)
    assert r11["metrics"][
        "disclosed_export_import_value_ratio"
    ] == pytest.approx(50.6)


def test_polypropylene_simulation_still_rejects_support() -> None:
    result = analyze("SAU-H0-390210", "simulated")
    assert result["real_decision"]["state"] == "REJECT"
    assert result["simulation_decision"]["state"] == "REJECT"
    assert result["simulation_decision"]["route_code"] == 0
    assert result["capacity"]["formula_capacity_kt"] == pytest.approx(
        104.49,
    )
    assert result["capacity"]["qualified_available_kt"] == 80.0
    assert result["capacity"]["target_spec_demand_kt"] == 56.0
    assert result["capacity"]["specification_adjusted_gap_kt"] < 0
    assert result["capacity"][
        "specification_adjusted_gap_kt"
    ] == -24.0
    assert result["capacity"]["domestic_grade_equivalent"] is True
    assert result["economics"]["minimum_effective_support_m"] == 0
    assert result["integrity"]["ground_truth_backtest"] == {
        "expected": {"state": "REJECT", "route_code": 0},
        "actual": {"state": "REJECT", "route_code": 0},
        "match": True,
    }


# Provisional S14 public recordings. T6 re-records and finalizes these only
# after the s14a merge and the authoritative 2.2.0 builder run.
RECORDED_PUBLIC_FIRED = {
    "SAU-H6-721061": {"R0", "R1-D", "R12"},
    "SAU-H6-721012": {"R0", "R1-D", "R2", "R4-D", "R12"},
    "SAU-H6-760711": {"R0", "R1-D", "R2", "R12"},
    "SAU-H6-760429": {
        "R0",
        "R1-D",
        "R2",
        "R3",
        "R4-D",
        "R5",
        "R9-S",
        "R10",
        "R12",
    },
    "SAU-H6-392010": {"R0", "R1-D", "R2", "R4-D", "R12"},
}

SIMULATION_PINS = {
    "SAU-H6-721061": {
        "scenario_id": "SYN-MINISTRY-GALVALUME-001",
        "state": "ADVANCE",
        "route": 3,
        "reason": "ALL_ADVANCE_GATES_PASS",
        "d_star": 0.25,
        "band": "incremental_upgrade",
        "capacity": {
            "effective_qualified_capacity_kt": 24.872,
            "target_spec_demand_kt": 48.0,
            "specification_adjusted_gap_kt": 23.128,
        },
        "economics": {
            "unsupported_npv_m": -4.743,
            "unsupported_irr": 0.08686,
            "minimum_effective_support_m": 5.0,
        },
        "national_value": 82.0,
        "competition_ratio": 1.1494,
        "competition_warning": False,
    },
    "SAU-H6-721012": {
        "scenario_id": "SYN-MINISTRY-TINPLATE-001",
        "state": "ADVANCE",
        "route": 7,
        "reason": "ALL_ADVANCE_GATES_PASS",
        "d_star": 0.9,
        "band": "greenfield_likely",
        "capacity": {
            "effective_qualified_capacity_kt": 0.0,
            "target_spec_demand_kt": 95.0,
            "specification_adjusted_gap_kt": 95.0,
        },
        "economics": {
            "unsupported_npv_m": -136.839,
            "unsupported_irr": 0.06986,
            "minimum_effective_support_m": 137.0,
        },
        "national_value": 220.0,
        "competition_ratio": 1.125,
        "competition_warning": False,
    },
    "SAU-H6-760711": {
        "scenario_id": "SYN-MINISTRY-ALU-FOIL-001",
        "state": "ADVANCE",
        "route": 6,
        "reason": "ALL_ADVANCE_GATES_PASS",
        "d_star": 0.5667,
        "band": "major_line_or_jv",
        "capacity": {
            "effective_qualified_capacity_kt": 0.0,
            "target_spec_demand_kt": 40.0,
            "specification_adjusted_gap_kt": 40.0,
        },
        "economics": {
            "unsupported_npv_m": -50.09,
            "unsupported_irr": 0.07904,
            "minimum_effective_support_m": 51.0,
        },
        "national_value": 172.0,
        "competition_ratio": 1.0588,
        "competition_warning": False,
    },
    "SAU-H6-760429": {
        "scenario_id": "SYN-MINISTRY-ALU-PROFILES-001",
        "state": "ADVANCE",
        "route": 4,
        "reason": "ALL_ADVANCE_GATES_PASS",
        "d_star": 0.25,
        "band": "incremental_upgrade",
        "capacity": {
            "formula_capacity_kt": 2.497,
            "qualified_available_kt": 2.5,
            "target_spec_demand_kt": 6.0,
            "specification_adjusted_gap_kt": 3.5,
        },
        "economics": {
            "unsupported_npv_m": 1.19,
            "unsupported_irr": 0.16319,
            "minimum_effective_support_m": 0.0,
        },
        "national_value": 31.0,
        "competition_ratio": 1.1725,
        "competition_warning": False,
    },
    "SAU-H6-392010": {
        "scenario_id": "SYN-MINISTRY-PE-FILM-001",
        "state": "REJECT",
        "route": 0,
        "reason": "HARD_EXCLUSION_SATISFIED",
        "d_star": 0.0,
        "band": "immediate_adjacency",
        "capacity": {
            "formula_capacity_kt": 23.085,
            "qualified_available_kt": 24.0,
            "target_spec_demand_kt": 16.0,
            "specification_adjusted_gap_kt": -8.0,
        },
        "economics": {
            "minimum_effective_support_m": 0.0,
        },
        "national_value": None,
        "competition_ratio": None,
        "competition_warning": None,
    },
}


def _assert_s14_public_golden(
    opportunity_id: str,
    *,
    preferred_route: int | None = None,
) -> None:
    result = analyze(opportunity_id, "public")
    decision = result["real_decision"]

    assert decision["state"] == "INVESTIGATE"
    assert result["active_decision"]["state"] == "INVESTIGATE"
    assert decision["route_code"] is None
    assert decision["decision_reason_code"] == (
        "ROUTE_CHANGING_EVIDENCE_UNRESOLVED"
    )
    assert result["screening_disposition"] == "CANDIDATE"
    assert result["capability"]["d_star"] is None
    assert not any(
        row.get("synthetic_flag") is True for row in result["rules"]
    )
    assert {
        row["rule_id"]
        for row in result["rules"]
        if row["fired"] is True
    } == set(RECORDED_PUBLIC_FIRED[opportunity_id])
    preferred = result["preferred_hypothesis"]
    if preferred_route is None:
        assert preferred is None
    else:
        assert preferred["route_code"] == preferred_route
        assert preferred["selection_basis"] == (
            "EVIDENCE_PRIORITY_WITH_ECONOMICS_UNAVAILABLE"
        )


def _assert_s14_simulated_golden(opportunity_id: str) -> None:
    expected = SIMULATION_PINS[opportunity_id]
    result = analyze(opportunity_id, "simulated")
    decision = result["simulation_decision"]

    assert result["real_decision"]["state"] == "INVESTIGATE"
    assert result["real_decision"]["route_code"] is None
    assert decision["state"] == expected["state"]
    assert decision["route_code"] == expected["route"]
    assert decision["decision_reason_code"] == expected["reason"]
    assert result["active_decision"] == decision
    assert result["simulation_scenario"]["scenario_id"] == (
        expected["scenario_id"]
    )
    assert result["integrity"]["ground_truth_backtest"] == {
        "expected": {
            "state": expected["state"],
            "route_code": expected["route"],
        },
        "actual": {
            "state": expected["state"],
            "route_code": expected["route"],
        },
        "match": True,
    }
    assert result["integrity"][
        "real_decision_unchanged_after_simulation"
    ] is True
    assert result["capability"]["d_star"] == pytest.approx(
        expected["d_star"],
        abs=1e-4,
    )
    assert result["capability"]["route_band"]["code"] == expected["band"]
    for key, value in expected["capacity"].items():
        assert result["capacity"][key] == pytest.approx(value, abs=1e-3)
    for key, value in expected["economics"].items():
        assert result["economics"][key] == pytest.approx(value, abs=1e-3)
    national_value = result["economics"].get("national_value")
    if expected["national_value"] is None:
        assert not isinstance(national_value, dict)
    else:
        assert national_value[
            "incremental_national_value_m_sar"
        ] == pytest.approx(expected["national_value"], abs=1e-3)
    ratio = result["competition"][
        "post_entry_capacity_to_downside_demand"
    ]
    if expected["competition_ratio"] is None:
        assert ratio is None
    else:
        assert ratio == pytest.approx(
            expected["competition_ratio"],
            abs=1e-4,
        )
    assert result["competition"]["warning_fires"] is (
        expected["competition_warning"]
    )


def test_galvalume_public_golden_case() -> None:
    _assert_s14_public_golden("SAU-H6-721061")


def test_galvalume_simulated_golden_case() -> None:
    _assert_s14_simulated_golden("SAU-H6-721061")


def test_tinplate_public_golden_case() -> None:
    _assert_s14_public_golden("SAU-H6-721012")


def test_tinplate_simulated_golden_case() -> None:
    _assert_s14_simulated_golden("SAU-H6-721012")


def test_alu_foil_public_golden_case() -> None:
    _assert_s14_public_golden("SAU-H6-760711")


def test_alu_foil_simulated_golden_case() -> None:
    _assert_s14_simulated_golden("SAU-H6-760711")


def test_alu_profiles_public_golden_case() -> None:
    _assert_s14_public_golden(
        "SAU-H6-760429",
        preferred_route=5,
    )


def test_alu_profiles_simulated_golden_case() -> None:
    _assert_s14_simulated_golden("SAU-H6-760429")


def test_pe_film_public_golden_case() -> None:
    _assert_s14_public_golden("SAU-H6-392010")


def test_pe_film_simulated_golden_case() -> None:
    _assert_s14_simulated_golden("SAU-H6-392010")
