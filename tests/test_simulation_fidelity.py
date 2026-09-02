from __future__ import annotations

import ast
from copy import deepcopy

import pytest

import ior_mvp.decision_engine as decision_engine
from ior_mvp.config import PROJECT_ROOT, thresholds_config
from ior_mvp.data_repository import (
    get_public_case,
    get_synthetic_scenario,
)
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.rules import (
    NOT_CALCULABLE,
    evaluate_simulated_rules,
)

ARABIC_DISCLOSURE = "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"


def _scenario(opportunity_id: str) -> dict:
    scenario = get_synthetic_scenario(opportunity_id)
    assert scenario is not None
    return deepcopy(scenario)


def _synthetic_rules(result: dict) -> list[dict]:
    return [
        row
        for row in result["rules"]
        if row.get("synthetic_flag") is True
    ]


def _by_id(rows: list[dict], rule_id: str) -> dict:
    return next(row for row in rows if row["rule_id"] == rule_id)


def test_simulation_contract_version_and_ground_truth_are_explicit() -> None:
    expected = {
        "SAU-H0-721049": ("ADVANCE", 5),
        "SAU-H0-390210": ("REJECT", 0),
    }
    for opportunity_id, pair in expected.items():
        scenario = _scenario(opportunity_id)
        assert scenario["scenario_version"] == "1.1.0"
        assert (
            scenario["ground_truth"]["expected_simulation_state"],
            scenario["ground_truth"]["expected_route_code"],
        ) == pair
        assert scenario["ground_truth"]["basis"]
        assert "INVESTIGATE" in scenario["decision_narrative"]


def test_supported_scenario_contract_version_is_accepted() -> None:
    scenario = _scenario("SAU-H0-721049")

    assert (
        decision_engine.SUPPORTED_SCENARIO_CONTRACT_VERSIONS
        == frozenset({"1.1.0"})
    )
    decision_engine.validate_simulation_contract(scenario)


def test_unsupported_scenario_contract_version_is_rejected() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["scenario_version"] = "1.2.0"

    with pytest.raises(
        EvidenceIntegrityError,
        match="scenario_version is unsupported: 1.2.0",
    ):
        decision_engine.validate_simulation_contract(scenario)


@pytest.mark.parametrize(
    "field",
    ["scenario_version", "ground_truth", "decision_narrative"],
)
def test_missing_simulation_contract_field_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    del scenario[field]
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: scenario,
    )

    with pytest.raises(EvidenceIntegrityError) as captured:
        decision_engine.analyze_simulated("SAU-H0-721049")

    assert field in str(captured.value)


def test_malformed_investigate_narrative_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    del scenario["decision_narrative"]["INVESTIGATE"][
        "rationale"
    ]
    monkeypatch.setattr(
        decision_engine,
        "get_synthetic_scenario",
        lambda opportunity_id: scenario,
    )

    with pytest.raises(
        EvidenceIntegrityError,
        match="INVESTIGATE.rationale",
    ):
        decision_engine.analyze_simulated("SAU-H0-721049")


def test_computed_state_without_narrative_is_typed_integrity_error() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["synthetic_inputs"]["equivalence"] = {
        "domestic_grade_equivalent": True,
        "qualified_available_kt": 104.0,
        "binding_market_failure": "none verified",
    }
    assert "REJECT" not in scenario["decision_narrative"]

    with pytest.raises(
        EvidenceIntegrityError,
        match="scenario.decision_narrative.REJECT must be a mapping",
    ):
        decision_engine._simulate(
            get_public_case("SAU-H0-721049"),
            scenario,
        )


def test_decision_narrative_is_projected_verbatim_from_scenario() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        scenario = _scenario(opportunity_id)
        result = decision_engine.analyze(
            opportunity_id,
            "simulated",
        )
        decision = result["simulation_decision"]
        narrative = scenario["decision_narrative"][
            decision["state"]
        ]

        for field in ("headline", "route_label", "rationale"):
            assert decision[field] == narrative[field]
        assert decision["conditions"] == narrative["conditions"]
        assert (
            decision["kill_conditions"]
            == narrative["kill_conditions"]
        )
        if "competition_finding" in narrative:
            assert (
                result["competition"]["finding"]
                == narrative["competition_finding"]
            )


def test_public_has_zero_synthetic_rule_rows_and_simulated_has_three() -> None:
    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        public = decision_engine.analyze(
            opportunity_id,
            "public",
        )
        simulated = decision_engine.analyze(
            opportunity_id,
            "simulated",
        )

        assert not any(
            row.get("synthetic_flag") is True
            for row in public["rules"]
        )
        rows = _synthetic_rules(simulated)
        assert [row["rule_id"] for row in rows] == [
            "R6",
            "R7",
            "R8",
        ]
        assert len(simulated["rules"]) == len(public["rules"]) + 3
        scenario = get_synthetic_scenario(opportunity_id)
        assert scenario is not None
        for row in rows:
            assert row["synthetic_flag"] is True
            assert row["scenario_id"] == scenario["scenario_id"]
            assert row["source"] == "DEMO_GENERATOR"
            assert row["evidence_class"] == "D"
            assert row["display_label"] == (
                "SIMULATED — NOT MINISTRY EVIDENCE"
            )
            assert row["display_labels"] == {
                "en": row["display_label"],
                "ar": ARABIC_DISCLOSURE,
            }
            assert row["basis"] == "synthetic"
            assert set(
                (
                    "rule_id",
                    "execution",
                    "fired",
                    "result",
                    "decision_effect",
                    "metrics",
                )
            ) <= set(row)

        assert simulated["simulation_decision"]["display_labels"] == {
            "en": "SIMULATED — NOT MINISTRY EVIDENCE",
            "ar": ARABIC_DISCLOSURE,
        }
        assert simulated["simulation_scenario"]["display_labels"] == {
            "en": "SIMULATED — NOT MINISTRY EVIDENCE",
            "ar": ARABIC_DISCLOSURE,
        }


def test_steel_simulated_r6_r7_r8_are_evidence_faithful() -> None:
    result = decision_engine.analyze(
        "SAU-H0-721049",
        "simulated",
    )
    rows = _synthetic_rules(result)
    r6 = _by_id(rows, "R6")
    r7 = _by_id(rows, "R7")
    r8 = _by_id(rows, "R8")

    assert r6["execution"] == "DEGRADED"
    assert r6["fired"] is True
    assert r6["metrics"]["effective_utilisation"] == pytest.approx(
        0.89
    )
    assert r6["metrics"][
        "effective_qualified_capacity_kt"
    ] == pytest.approx(57.509)
    assert r6["metrics"]["shortage_ratio"] == pytest.approx(
        0.8084
    )
    assert r6["metrics"]["shortage_denominator"] == (
        "effective_qualified_capacity_kt"
    )
    assert r6["metrics"]["sustained_period"] == NOT_CALCULABLE

    assert r7["execution"] == "DEGRADED"
    assert r7["fired"] is False
    assert r7["metrics"]["effective_utilisation"] == pytest.approx(
        0.89
    )
    assert (
        r7["metrics"]["specification_equivalence"]
        == NOT_CALCULABLE
    )

    assert r8["execution"] == "DISABLED"
    assert r8["fired"] is None
    assert r8["metrics"]["committed_demand_kt"] == 74.0
    assert r8["metrics"]["announced_demand_kt"] == 22.0
    assert r8["metrics"]["target_spec_demand_kt"] == 104.0
    assert r8["metrics"]["downside_demand_kt"] == 100.0
    for key in (
        "base_demand_kt",
        "commitment_probability",
        "probability_adjusted_committed_demand_kt",
        "probability_adjusted_demand_addition",
        "minimum_efficient_scale_kt",
        "mes_fill",
    ):
        assert r8["metrics"][key] == NOT_CALCULABLE
    assert r8["metrics"][
        "minimum_probability_adjusted_demand_addition"
    ] == pytest.approx(0.20)
    assert r8["metrics"]["minimum_mes_fill"] == pytest.approx(
        0.25
    )


def test_pp_simulated_r6_r7_r8_are_evidence_faithful() -> None:
    result = decision_engine.analyze(
        "SAU-H0-390210",
        "simulated",
    )
    rows = _synthetic_rules(result)
    r6 = _by_id(rows, "R6")
    r7 = _by_id(rows, "R7")
    r8 = _by_id(rows, "R8")

    assert r6["execution"] == "DEGRADED"
    assert r6["fired"] is False
    assert r6["metrics"]["effective_utilisation"] == pytest.approx(
        0.78
    )
    assert r6["metrics"][
        "effective_qualified_capacity_kt"
    ] == pytest.approx(104.49)
    assert r6["metrics"]["shortage_ratio"] == pytest.approx(
        -0.4641
    )
    assert r6["metrics"]["sustained_period"] == NOT_CALCULABLE

    assert r7["execution"] == "FULL"
    assert r7["fired"] is False
    assert r7["metrics"]["effective_utilisation"] == pytest.approx(
        0.78
    )
    assert r7["metrics"]["specification_equivalence"] is True
    assert r7["metrics"]["qualified_available_kt"] == 80.0

    assert r8["execution"] == "DISABLED"
    assert r8["fired"] is None
    assert r8["metrics"]["committed_demand_kt"] == 0.0
    assert r8["metrics"]["announced_demand_kt"] == 0.0
    assert r8["metrics"]["target_spec_demand_kt"] == 56.0
    assert r8["metrics"]["downside_demand_kt"] == 51.0


@pytest.mark.parametrize(
    "failed_control",
    [
        "positive_gap",
        "route_publishable",
        "incremental_distance",
        "economics",
        "national_value",
        "competition",
    ],
)
def test_each_failed_steel_advance_control_selects_investigate(
    failed_control: str,
) -> None:
    scenario = _scenario("SAU-H0-721049")
    inputs = scenario["synthetic_inputs"]
    if failed_control == "positive_gap":
        inputs["demand"]["target_spec_demand_kt"] = 50.0
    elif failed_control == "route_publishable":
        inputs["hard_gates"][
            "mandatory_or_customer_standard"
        ] = "unresolved"
    elif failed_control == "incremental_distance":
        for dimension in inputs["capability_states"]:
            inputs["capability_states"][dimension] = 2
    elif failed_control == "economics":
        inputs["economics"][
            "cash_flows_without_support"
        ] = [-1.0]
    elif failed_control == "national_value":
        for component in inputs["economics"]["national_value"]:
            inputs["economics"]["national_value"][component] = 0.0
    elif failed_control == "competition":
        inputs["upgrade"]["incremental_capacity_kt"] = 68.0

    branch = decision_engine._simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )

    assert branch["simulation_decision"]["state"] == "INVESTIGATE"
    assert branch["simulation_decision"]["route_code"] is None
    assert branch["simulation_decision"]["headline"] == (
        scenario["decision_narrative"]["INVESTIGATE"][
            "headline"
        ]
    )


def test_equivalence_at_target_selects_reject_without_id_dispatch() -> None:
    scenario = _scenario("SAU-H0-721049")
    pp = _scenario("SAU-H0-390210")
    scenario["synthetic_inputs"]["equivalence"] = {
        "domestic_grade_equivalent": True,
        "qualified_available_kt": 104.0,
        "binding_market_failure": "none verified",
    }
    scenario["decision_narrative"]["REJECT"] = deepcopy(
        pp["decision_narrative"]["REJECT"]
    )

    branch = decision_engine._simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )

    assert branch["capacity"][
        "specification_adjusted_gap_kt"
    ] == 0.0
    assert branch["simulation_decision"]["state"] == "REJECT"
    assert branch["simulation_decision"]["route_code"] == 0


def test_ground_truth_never_drives_selection_and_mismatch_fails() -> None:
    scenario = _scenario("SAU-H0-721049")
    scenario["ground_truth"][
        "expected_simulation_state"
    ] = "REJECT"
    scenario["ground_truth"]["expected_route_code"] = 0
    scenario["decision_narrative"]["REJECT"] = deepcopy(
        _scenario("SAU-H0-390210")["decision_narrative"]["REJECT"]
    )

    branch = decision_engine._simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )
    report = decision_engine.evaluate_ground_truth_backtest(
        scenario,
        branch["simulation_decision"],
    )

    assert branch["simulation_decision"]["state"] == "ADVANCE"
    assert branch["simulation_decision"]["route_code"] == 5
    assert report == {
        "expected": {"state": "REJECT", "route_code": 0},
        "actual": {"state": "ADVANCE", "route_code": 5},
        "match": False,
    }
    with pytest.raises(
        EvidenceIntegrityError,
        match="ground-truth back-test failed",
    ):
        decision_engine.require_ground_truth_backtest(
            scenario,
            report,
        )


def test_engine_source_has_no_scenario_id_dispatch_or_narrative() -> None:
    source = (
        PROJECT_ROOT
        / "src"
        / "ior_mvp"
        / "decision_engine.py"
    ).read_text(encoding="utf-8")
    assert "SAU-H0-721049" not in source
    assert "SAU-H0-390210" not in source
    assert "_simulate_steel" not in source
    assert "_simulate_pp" not in source
    literal_strings = {
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    for opportunity_id in (
        "SAU-H0-721049",
        "SAU-H0-390210",
    ):
        narratives = _scenario(opportunity_id)[
            "decision_narrative"
        ]
        for narrative in narratives.values():
            values = [
                narrative["headline"],
                narrative["route_label"],
                narrative["rationale"],
                *narrative["conditions"],
                *narrative["kill_conditions"],
            ]
            if "competition_finding" in narrative:
                values.append(narrative["competition_finding"])
            for value in values:
                assert value not in literal_strings


def test_evaluate_simulated_rules_rejects_cross_case_use() -> None:
    scenario = _scenario("SAU-H0-721049")
    with pytest.raises(
        EvidenceIntegrityError,
        match="opportunity_id",
    ):
        evaluate_simulated_rules(
            scenario,
            get_public_case("SAU-H0-390210"),
            {
                "effective_qualified_capacity_kt": 57.509,
                "target_spec_demand_kt": 104.0,
            },
            thresholds_config(),
        )
