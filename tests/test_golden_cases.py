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
        "1.1.0"
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
