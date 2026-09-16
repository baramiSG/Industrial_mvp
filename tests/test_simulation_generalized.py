from __future__ import annotations

from copy import deepcopy

import pytest

import ior_mvp.decision_engine as decision_engine
import ior_mvp.simulation as simulation
from ior_mvp.data_repository import get_public_case, get_synthetic_scenario
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.graph.engine_feed import shared_enabler_inputs
from ior_mvp.graph.projection import build_evidence_layer
from ior_mvp.public_decision import DecisionIntegrityError
from ior_mvp.scenario_contract import validate_simulation_contract


def _steel() -> dict:
    scenario = get_synthetic_scenario("SAU-H0-721049")
    assert scenario is not None
    return deepcopy(scenario)


def test_simulate_matches_frozen_steel_outcome() -> None:
    public = get_public_case("SAU-H0-721049")
    scenario = _steel()
    branch = simulation.simulate(public, scenario)
    decision = branch["simulation_decision"]
    assert decision["state"] == "ADVANCE"
    assert decision["route_code"] == 5
    assert decision["decision_reason_code"] == "ALL_ADVANCE_GATES_PASS"
    assert decision["narrative_source"] == "scenario"
    assert decision["advance_gate"]["basis"] == "CLASS_IF_CONFIRMED"
    assert decision["counterfactual"]["q2_missing_capabilities"] == [
        "equipment_envelope",
        "finishing_spec_control",
        "certification_customer_qualification",
        "capacity_time_window",
    ]
    assert all(
        row["evidence_class"] == "D"
        for row in decision["evidence_class_assessment"].values()
    )


def test_analyze_public_wrapper_matches_direct_simulate() -> None:
    public = decision_engine.analyze_public("SAU-H0-721049")
    scenario = _steel()
    direct = simulation.simulate(public, scenario)["simulation_decision"]
    wrapped = decision_engine.analyze("SAU-H0-721049", "simulated")[
        "simulation_decision"
    ]
    assert direct["state"] == wrapped["state"]
    assert direct["route_code"] == wrapped["route_code"]
    assert direct["decision_reason_code"] == wrapped["decision_reason_code"]


def test_decision_engine_reexports_simulation() -> None:
    assert decision_engine.SUPPORTED_SCENARIO_CONTRACT_VERSIONS == frozenset(
        {"2.0.0", "2.1.0"}
    )
    assert decision_engine._simulate is simulation.simulate


def test_scenario_without_class_if_confirmed_never_reaches_advance() -> None:
    scenario = _steel()
    del scenario["synthetic_inputs"]["class_if_confirmed"]
    branch = simulation.simulate(get_public_case("SAU-H0-721049"), scenario)
    assert branch["simulation_decision"]["state"] != "ADVANCE"


def test_catalogue_fallback_when_state_narrative_missing() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["equivalence"] = {
        "domestic_grade_equivalent": True,
        "qualified_available_kt": 104.0,
        "basis": "test",
    }
    branch = simulation.simulate(get_public_case("SAU-H0-721049"), scenario)
    assert branch["simulation_decision"]["state"] == "REJECT"
    assert branch["simulation_decision"]["narrative_source"] == "catalogue"
    assert branch["simulation_decision"]["localized_narrative"]["ar"][
        "headline"
    ]["text"]


def test_monitor_without_trigger_fails_closed() -> None:
    scenario = _steel()
    scenario["ground_truth"]["expected_simulation_state"] = "MONITOR"
    scenario["ground_truth"]["expected_route_code"] = 0
    with pytest.raises(EvidenceIntegrityError):
        simulation.simulate(get_public_case("SAU-H0-721049"), scenario)


def test_public_analysis_unchanged_by_simulation_branch() -> None:
    before_steel = decision_engine.analyze("SAU-H0-721049", "public")
    before_pp = decision_engine.analyze("SAU-H0-390210", "public")
    decision_engine.analyze("SAU-H0-721049", "simulated")
    decision_engine.analyze("SAU-H0-390210", "simulated")
    after_steel = decision_engine.analyze("SAU-H0-721049", "public")
    after_pp = decision_engine.analyze("SAU-H0-390210", "public")
    assert before_steel["real_decision"] == after_steel["real_decision"]
    assert before_pp["real_decision"] == after_pp["real_decision"]


FIXTURE_ROOT = (
    __import__("ior_mvp.config", fromlist=["PROJECT_ROOT"]).PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "simulation"
)
PUBLIC_FIXTURE_ROOT = (
    __import__("ior_mvp.config", fromlist=["PROJECT_ROOT"]).PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "public_decision"
)


def _load_fixture(name: str) -> dict:
    import json

    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _load_public_fixture(name: str) -> dict:
    import json

    return json.loads(
        (PUBLIC_FIXTURE_ROOT / name).read_text(encoding="utf-8")
    )


@pytest.mark.parametrize(
    ("fixture_name", "public_fixture", "expected_route"),
    [
        ("sim-route-1-barrier.json", "advance-route-3.json", 1),
        ("sim-route-2-linkage.json", "advance-route-3.json", 2),
        ("sim-route-3-certification.json", "advance-route-3.json", 3),
        ("sim-route-4-offtake.json", "advance-route-3.json", 4),
        ("sim-route-6-technology-jv.json", "advance-route-3.json", 6),
        ("sim-route-7-greenfield.json", "advance-route-3.json", 7),
    ],
)
def test_route_fixtures_advance_on_expected_route(
    fixture_name: str,
    public_fixture: str,
    expected_route: int,
) -> None:
    scenario = _load_fixture(fixture_name)
    public = _load_public_fixture(public_fixture)
    branch = simulation.simulate(public, scenario)
    decision = branch["simulation_decision"]
    assert decision["state"] == "ADVANCE"
    assert decision["route_code"] == expected_route
    assert decision["decision_reason_code"] == "ALL_ADVANCE_GATES_PASS"
    assert (
        branch["route_hypotheses"][expected_route]["status"] == "passes"
    )
    if expected_route == 7:
        assert branch["route_hypotheses"][5]["reason_codes"] == [
            "FEASIBILITY_FAILED"
        ]
        assert branch["route_hypotheses"][0]["reason_codes"] == [
            "ROUTE_0_GAP_REQUIRES_ACTION"
        ]
    elif expected_route == 6:
        assert branch["route_hypotheses"][7]["reason_codes"] == [
            "ROUTE_EVIDENCE_REQUIRED",
            "LOWER_ROUTE_FULLY_RESOLVES",
        ]
        assert (
            branch["route_hypotheses"][7]["precedence"][
                "blocked_by_lower_route"
            ]
            == 6
        )
    else:
        for route in branch["route_hypotheses"]:
            code = route["route_code"]
            if code > expected_route and code < 8:
                assert route["status"] == "fails"
                assert "LOWER_ROUTE_FULLY_RESOLVES" in route.get(
                    "reason_codes", []
                )
                assert (
                    route.get("precedence", {}).get(
                        "blocked_by_lower_route"
                    )
                    == expected_route
                )


def test_monitor_fixture_returns_named_trigger_monitor() -> None:
    scenario = _load_fixture("sim-monitor-named-trigger.json")
    public = _load_public_fixture("monitor-r3-only.json")
    branch = simulation.simulate(public, scenario)
    decision = branch["simulation_decision"]
    assert decision["state"] == "MONITOR"
    assert decision["route_code"] == 0
    assert decision["decision_reason_code"] == "NAMED_TRIGGER_MONITOR"
    assert branch["route_hypotheses"][0]["reason_codes"] == [
        "MONITOR_NO_IMMEDIATE_ACTION"
    ]


def test_partial_routes_prefer_max_defensible_incremental_national_value() -> (
    None
):
    scenario = _load_fixture("sim-two-partial-routes-max-nv.json")
    public = _load_public_fixture("advance-route-3.json")
    branch = simulation.simulate(public, scenario)
    decision = branch["simulation_decision"]
    assert decision["state"] == "ADVANCE"
    assert decision["route_code"] == 4
    preferred = branch["preferred_hypothesis"]
    assert preferred["route_code"] == 4
    assert (
        preferred["selection_basis"]
        == "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE"
    )
    assert "PARTIAL_RESOLUTION" in branch["route_hypotheses"][3][
        "reason_codes"
    ]
    assert "PARTIAL_RESOLUTION" in branch["route_hypotheses"][4][
        "reason_codes"
    ]


def test_partial_route_tie_selects_lower_route_code() -> None:
    scenario = _load_fixture("sim-two-partial-routes-max-nv.json")
    public = _load_public_fixture("advance-route-3.json")
    for record in scenario["synthetic_inputs"]["route_evidence"]:
        record["national_value"]["domestic_value_added"] = 44.0
    branch = simulation.simulate(public, scenario)
    assert branch["simulation_decision"]["route_code"] == 3
    assert branch["preferred_hypothesis"]["route_code"] == 3


def test_lower_route_blocks_escalation_to_higher_route() -> None:
    scenario = _load_fixture("sim-lower-route-blocks-escalation.json")
    public = _load_public_fixture("advance-route-3.json")
    branch = simulation.simulate(public, scenario)
    decision = branch["simulation_decision"]
    assert decision["state"] == "ADVANCE"
    assert decision["route_code"] == 3
    route_four = branch["route_hypotheses"][4]
    assert route_four["status"] == "fails"
    assert "LOWER_ROUTE_FULLY_RESOLVES" in route_four["reason_codes"]
    assert route_four["precedence"]["blocked_by_lower_route"] == 3


def test_route_six_band_mutation_fails_capability_band() -> None:
    scenario = _load_fixture("sim-route-6-technology-jv.json")
    public = _load_public_fixture("advance-route-3.json")
    scenario["synthetic_inputs"]["capability_states"][
        "core_process_route"
    ] = 0
    branch = simulation.simulate(public, scenario)
    decision = branch["simulation_decision"]
    assert decision["state"] == "INVESTIGATE"
    route_six = branch["route_hypotheses"][6]
    assert "CAPABILITY_BAND_FAILED" in route_six["reason_codes"]


@pytest.mark.parametrize(
    "mutator",
    [
        lambda block: block.update({"product_identity": "D"}),
        lambda block: block.update({"demand_at_required_specification": "E"}),
        lambda block: block.pop("domestic_supply_or_capability"),
    ],
)
def test_class_if_confirmed_mutations_block_advance(
    mutator: object,
) -> None:
    scenario = _steel()
    mutator(scenario["synthetic_inputs"]["class_if_confirmed"])
    branch = simulation.simulate(
        get_public_case("SAU-H0-721049"),
        scenario,
    )
    assert branch["simulation_decision"]["state"] != "ADVANCE"


def test_route_eight_refused_in_scenario_contract() -> None:
    scenario = _steel()
    scenario["synthetic_inputs"]["route_evidence"].append(
        {
            "route_code": 8,
            "binding_constraint": "capacity_or_availability",
            "basis": "forbidden",
        }
    )
    with pytest.raises(EvidenceIntegrityError):
        validate_simulation_contract(scenario)


def test_simulated_evidence_rows_remain_class_d_and_labelled() -> None:
    result = decision_engine.analyze("SAU-H0-721049", "simulated")
    for row in result["evidence"]:
        if row.get("synthetic_flag"):
            assert row["evidence_class"] == "D"
            assert row["source"] == "DEMO_GENERATOR"
            assert row.get("display_label")
    for assessment in result["simulation_decision"][
        "evidence_class_assessment"
    ].values():
        assert assessment["evidence_class"] == "D"
        assert assessment["synthetic_flag"] is True


def test_s16b_honest_projection_fixture_selects_route_eight_and_backtests() -> None:
    opportunities = ("SAU-H6-760711", "SAU-H6-760429")
    public_cases = {
        opportunity_id: deepcopy(get_public_case(opportunity_id))
        for opportunity_id in opportunities
    }
    scenarios = {}
    for opportunity_id in opportunities:
        scenario = deepcopy(get_synthetic_scenario(opportunity_id))
        assert scenario is not None
        suffix = "A" if opportunity_id == "SAU-H6-760711" else "B"
        scenario["scenario_id"] = f"SYN-TEST-ROUTE8-{suffix}"
        block = scenario["synthetic_inputs"]["shared_enabler"]
        block["enabler_id"] = "ENABLER-SYN-TEST-ROUTE8"
        block["unlock_probability"] = 1.0
        block["dependency_share"] = 1.0
        selected_route = block["valuation_route_code"]
        selected = next(
            record
            for record in scenario["synthetic_inputs"]["route_evidence"]
            if record["route_code"] == selected_route
        )
        selected["binding_constraint_fully_removed"] = False
        scenario["ground_truth"]["expected_route_code"] = 8
        scenario["ground_truth"]["expected_simulation_state"] = "ADVANCE"
        scenario["decision_narrative"].pop("ADVANCE")
        scenarios[opportunity_id] = scenario
    projection = build_evidence_layer(
        public_cases=public_cases,
        scenarios=scenarios,
        entity_artifacts=[],
        briefs=[],
        tariff_snapshots=[],
        tariff_attempts=[],
        projection_id="GRAPH-TEST",
        engine_run_id="ENGINE-TEST",
        inputs=[],
    )
    for opportunity_id, scenario in scenarios.items():
        branch = simulation.simulate(
            public_cases[opportunity_id],
            scenario,
            shared_enabler=shared_enabler_inputs(
                projection,
                opportunity_id,
                branch=("simulated", scenario["scenario_id"]),
            ),
        )
        decision = branch["simulation_decision"]
        assert decision["state"] == "ADVANCE"
        assert decision["route_code"] == 8
        assert branch["route_hypotheses"][8][
            "unrounded_incremental_national_value_m_sar"
        ] == 178.0
        assert decision["narrative_source"] == "catalogue"
        assert decision["route_label"] == "Shared enabling infrastructure"
        assert simulation.evaluate_ground_truth_backtest(
            scenario,
            decision,
        )["match"] is True
