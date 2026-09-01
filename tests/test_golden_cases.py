from __future__ import annotations

import pytest

from ior_mvp.decision_engine import analyze


def test_steel_public_golden_case() -> None:
    result = analyze("SAU-H0-721049", "public")
    assert result["real_decision"]["state"] == "INVESTIGATE"
    assert result["active_decision"]["state"] == "INVESTIGATE"
    assert result["real_decision"]["route_code"] is None
    assert result["capability"]["d_star"] is None
    fired = {row["rule_id"]: row["fired"] for row in result["rules"]}
    assert fired["R1-D"] is True
    assert fired["R2"] is True
    assert fired["R3"] is True
    assert fired["R4-D"] is True
    assert fired["R9-S"] is True


def test_steel_simulated_golden_case() -> None:
    result = analyze("SAU-H0-721049", "simulated")
    assert result["real_decision"]["state"] == "INVESTIGATE"
    assert result["simulation_decision"]["state"] == "ADVANCE"
    assert result["active_decision"]["route_code"] == 5
    assert result["capacity"]["effective_qualified_capacity_kt"] == pytest.approx(57.509, abs=1e-3)
    assert result["capacity"]["specification_adjusted_gap_kt"] == pytest.approx(46.491, abs=1e-3)
    assert result["economics"]["minimum_effective_support_m"] == pytest.approx(18.0)
    assert result["economics"]["national_value"]["incremental_national_value_m_sar"] == pytest.approx(198.0)
    assert result["competition"]["post_entry_capacity_to_downside_demand"] < 1.25
    assert result["integrity"]["real_decision_unchanged_after_simulation"] is True


def test_polypropylene_public_golden_case() -> None:
    result = analyze("SAU-H0-390210", "public")
    assert result["real_decision"]["state"] == "REJECT"
    assert result["real_decision"]["route_code"] == 0
    fired = {row["rule_id"]: row["fired"] for row in result["rules"]}
    assert fired["R1-D"] is True
    assert fired["R2"] is False
    assert fired["R11"] is True


def test_polypropylene_simulation_still_rejects_support() -> None:
    result = analyze("SAU-H0-390210", "simulated")
    assert result["real_decision"]["state"] == "REJECT"
    assert result["simulation_decision"]["state"] == "REJECT"
    assert result["capacity"]["specification_adjusted_gap_kt"] < 0
    assert result["economics"]["minimum_effective_support_m"] == 0
