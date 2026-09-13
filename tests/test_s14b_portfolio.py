from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.data_repository import get_public_case
from ior_mvp.decision_engine import analyze
from ior_mvp.dossier import build_dossier, render_dossier_html
from ior_mvp.evidence import (
    public_decision_fingerprint,
    reconcile_synthetic_scenario,
    synthetic_evidence_rows,
    validate_synthetic_scenario,
)
from ior_mvp.genui import build_ui_manifest
from ior_mvp.narratives import localize_rule_rows
from ior_mvp.rules import evaluate_rules
from ior_mvp.scenario_contract import validate_simulation_contract
from ior_mvp.signals import material_trigger_rule_ids
from ior_mvp.simulation import evaluate_ground_truth_backtest, simulate


S14_CASES = (
    ("SAU-H6-721061", "GALVALUME", "ADVANCE", 3),
    ("SAU-H6-721012", "TINPLATE", "ADVANCE", 7),
    ("SAU-H6-760711", "ALU-FOIL", "ADVANCE", 6),
    ("SAU-H6-760429", "ALU-PROFILES", "ADVANCE", 4),
    ("SAU-H6-392010", "PE-FILM", "REJECT", 0),
)
S14_IDS = tuple(row[0] for row in S14_CASES)
EXPECTED_REASONS = {
    "SAU-H6-721061": "ALL_ADVANCE_GATES_PASS",
    "SAU-H6-721012": "ALL_ADVANCE_GATES_PASS",
    "SAU-H6-760711": "ALL_ADVANCE_GATES_PASS",
    "SAU-H6-760429": "ALL_ADVANCE_GATES_PASS",
    "SAU-H6-392010": "HARD_EXCLUSION_SATISFIED",
}
EXPECTED_SELECTION = {
    opportunity_id: (
        "EVIDENCED_NO_INTERVENTION"
        if route_code == 0
        else "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE"
    )
    for opportunity_id, _, _, route_code in S14_CASES
}
EXPECTED_GATE_B = {
    "SAU-H6-721061": (
        "PASS",
        "NOT_APPLICABLE",
        "PASS",
        "NOT_APPLICABLE",
        "INFORMATIONAL",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "PASS",
    ),
    "SAU-H6-721012": (
        "PASS",
        "NOT_APPLICABLE",
        "PASS",
        "NOT_APPLICABLE",
        "INFORMATIONAL",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "PASS",
    ),
    "SAU-H6-760711": (
        "PASS",
        "NOT_APPLICABLE",
        "PASS",
        "NOT_APPLICABLE",
        "INFORMATIONAL",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "PASS",
    ),
    "SAU-H6-760429": (
        "PASS",
        "NOT_APPLICABLE",
        "PASS",
        "PASS",
        "INFORMATIONAL",
        "PASS",
        "PASS",
        "NOT_APPLICABLE",
        "PASS",
        "PASS",
    ),
    "SAU-H6-392010": (
        "PASS",
        "NOT_APPLICABLE",
        "PASS",
        "PASS",
        "INFORMATIONAL",
        "PASS",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
        "NOT_APPLICABLE",
    ),
}
EXPECTED_ROUTES = {
    "SAU-H6-721061": (
        ("fails", ("ROUTE_0_GAP_REQUIRES_ACTION",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("passes", (), None),
        (
            "fails",
            (
                "CONSTRAINT_CLASS_NOT_APPLICABLE",
                "LOWER_ROUTE_FULLY_RESOLVES",
            ),
            3,
        ),
        (
            "fails",
            (
                "CONSTRAINT_CLASS_NOT_APPLICABLE",
                "LOWER_ROUTE_FULLY_RESOLVES",
            ),
            3,
        ),
        (
            "fails",
            (
                "CONSTRAINT_CLASS_NOT_APPLICABLE",
                "LOWER_ROUTE_FULLY_RESOLVES",
            ),
            3,
        ),
        (
            "fails",
            (
                "CONSTRAINT_CLASS_NOT_APPLICABLE",
                "LOWER_ROUTE_FULLY_RESOLVES",
            ),
            3,
        ),
        ("NOT_CALCULABLE", ("GRAPH_REQUIRED",), None),
    ),
    "SAU-H6-721012": (
        ("fails", ("ROUTE_0_GAP_REQUIRES_ACTION",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("FEASIBILITY_FAILED",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("passes", (), None),
        ("NOT_CALCULABLE", ("GRAPH_REQUIRED",), None),
    ),
    "SAU-H6-760711": (
        ("fails", ("ROUTE_0_GAP_REQUIRES_ACTION",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("FEASIBILITY_FAILED",), None),
        ("passes", (), None),
        (
            "fails",
            ("ROUTE_EVIDENCE_REQUIRED", "LOWER_ROUTE_FULLY_RESOLVES"),
            6,
        ),
        ("NOT_CALCULABLE", ("GRAPH_REQUIRED",), None),
    ),
    "SAU-H6-760429": (
        ("fails", ("ROUTE_0_GAP_REQUIRES_ACTION",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("fails", ("CONSTRAINT_CLASS_NOT_APPLICABLE",), None),
        ("passes", (), None),
        ("fails", ("POLICY_FAILED", "LOWER_ROUTE_FULLY_RESOLVES"), 4),
        (
            "fails",
            (
                "CONSTRAINT_CLASS_NOT_APPLICABLE",
                "LOWER_ROUTE_FULLY_RESOLVES",
            ),
            4,
        ),
        (
            "fails",
            ("ROUTE_EVIDENCE_REQUIRED", "LOWER_ROUTE_FULLY_RESOLVES"),
            4,
        ),
        ("NOT_CALCULABLE", ("GRAPH_REQUIRED",), None),
    ),
    "SAU-H6-392010": (
        ("passes", ("EVIDENCED_NO_INTERVENTION",), None),
        *(
            (
                "fails",
                ("ROUTE_EVIDENCE_REQUIRED", "LOWER_ROUTE_FULLY_RESOLVES"),
                0,
            )
            for _ in range(7)
        ),
        ("NOT_CALCULABLE", ("GRAPH_REQUIRED",), None),
    ),
}


def _scenario_path(slug: str) -> Path:
    return (
        PROJECT_ROOT
        / "data"
        / "synthetic"
        / f"SYN-MINISTRY-{slug}-001.json"
    )


def _scenario(slug: str) -> dict:
    return json.loads(_scenario_path(slug).read_text(encoding="utf-8"))


def _snapshot_path(opportunity_id: str) -> Path:
    hs6 = opportunity_id.rsplit("-", 1)[-1]
    path = (
        PROJECT_ROOT
        / "data"
        / "snapshots"
        / "public"
        / f"PUBLIC-SAU-H6-{hs6}-2026-09-12.json"
    )
    assert path.is_file(), f"integration snapshot is pending: {path.name}"
    return path


def _route_rows(branch: dict) -> tuple[tuple[str, tuple[str, ...], int | None], ...]:
    return tuple(
        (
            row["status"],
            tuple(row["reason_codes"]),
            row["precedence"]["blocked_by_lower_route"],
        )
        for row in branch["route_hypotheses"]
    )


@pytest.mark.parametrize(
    ("opportunity_id", "slug", "_state", "_route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_five_s14_snapshots_are_builder_output_not_authored(
    opportunity_id: str,
    slug: str,
    _state: str,
    _route: int,
) -> None:
    del slug, _state, _route
    committed = _snapshot_path(opportunity_id)
    from ior_mvp.cases.build import build_from_brief
    from ior_mvp.cases.projection import canonical_bytes

    brief = (
        PROJECT_ROOT
        / "data"
        / "cases"
        / "briefs"
        / f"CASE-BRIEF-{opportunity_id}-v1.json"
    )
    rebuilt = build_from_brief(brief, root=PROJECT_ROOT)
    assert committed.read_bytes() == canonical_bytes(rebuilt)


@pytest.mark.parametrize(
    ("opportunity_id", "slug", "state", "route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_each_s14_scenario_validates_contract_2_0_0_and_metadata(
    opportunity_id: str,
    slug: str,
    state: str,
    route: int,
) -> None:
    scenario = _scenario(slug)
    validate_synthetic_scenario(scenario)
    validate_simulation_contract(scenario)

    assert scenario["scenario_version"] == "2.0.0"
    assert scenario["opportunity_id"] == opportunity_id
    assert scenario["synthetic_flag"] is True
    assert scenario["evidence_class"] == "D"
    assert scenario["source"] == "DEMO_GENERATOR"
    assert scenario["display_label"] == "SIMULATED — NOT MINISTRY EVIDENCE"
    assert scenario["narrative_metadata"] == {
        "arabic_text_status": "ANALYST_AUTHORED_DRAFT"
    }
    assert scenario["ground_truth"]["expected_simulation_state"] == state
    assert scenario["ground_truth"]["expected_route_code"] == route
    assert scenario["ground_truth"]["basis"]
    assert scenario["seed_basis"]


@pytest.mark.parametrize(
    ("opportunity_id", "slug", "_state", "_route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_each_s14_scenario_reconciles_gate_b_without_fail(
    opportunity_id: str,
    slug: str,
    _state: str,
    _route: int,
) -> None:
    del _state, _route
    _snapshot_path(opportunity_id)
    report = reconcile_synthetic_scenario(
        _scenario(slug),
        get_public_case(opportunity_id),
    )

    assert report["status"] == "PASS"
    assert tuple(row["result"] for row in report["checks"]) == (
        EXPECTED_GATE_B[opportunity_id]
    )
    assert all(row["result"] != "FAIL" for row in report["checks"])


@pytest.mark.parametrize(
    ("opportunity_id", "slug", "state", "route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_each_s14_scenario_reaches_planted_truth_by_computation(
    opportunity_id: str,
    slug: str,
    state: str,
    route: int,
) -> None:
    _snapshot_path(opportunity_id)
    scenario = _scenario(slug)
    branch = simulate(get_public_case(opportunity_id), scenario)
    decision = branch["simulation_decision"]

    assert decision["state"] == state
    assert decision["route_code"] == route
    assert decision["decision_reason_code"] == EXPECTED_REASONS[opportunity_id]
    assert branch["preferred_hypothesis"]["route_code"] == route
    assert (
        branch["preferred_hypothesis"]["selection_basis"]
        == EXPECTED_SELECTION[opportunity_id]
    )
    assert evaluate_ground_truth_backtest(scenario, decision)["match"] is True


@pytest.mark.parametrize(
    ("opportunity_id", "slug", "_state", "_route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_lower_routes_fail_with_recorded_reason_codes(
    opportunity_id: str,
    slug: str,
    _state: str,
    _route: int,
) -> None:
    del _state, _route
    _snapshot_path(opportunity_id)
    branch = simulate(get_public_case(opportunity_id), _scenario(slug))
    assert _route_rows(branch) == EXPECTED_ROUTES[opportunity_id]


@pytest.mark.parametrize(
    "opportunity_id",
    S14_IDS,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_monitor_is_unreachable_for_every_s14_case_because_public_material_triggers_fire(
    opportunity_id: str,
) -> None:
    _snapshot_path(opportunity_id)
    public = get_public_case(opportunity_id)
    public_rules = evaluate_rules(public)

    assert "R1-D" in material_trigger_rule_ids(public_rules)
    assert analyze(opportunity_id, "public")["real_decision"]["state"] != (
        "MONITOR"
    )
    assert analyze(opportunity_id, "simulated")["active_decision"]["state"] != (
        "MONITOR"
    )


@pytest.mark.parametrize(
    ("opportunity_id", "_slug", "_state", "_route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_s14_simulations_never_change_real_decision(
    opportunity_id: str,
    _slug: str,
    _state: str,
    _route: int,
) -> None:
    del _slug, _state, _route
    _snapshot_path(opportunity_id)
    public = analyze(opportunity_id, "public")
    simulated = analyze(opportunity_id, "simulated")

    assert simulated["real_decision"] == public["real_decision"]
    assert (
        public_decision_fingerprint(simulated["real_decision"])
        == public_decision_fingerprint(public["real_decision"])
    )
    assert simulated["integrity"][
        "real_decision_unchanged_after_simulation"
    ] is True


@pytest.mark.parametrize(
    ("opportunity_id", "slug", "_state", "_route"),
    S14_CASES,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_s14_synthetic_rows_are_class_d_and_labelled_everywhere(
    opportunity_id: str,
    slug: str,
    _state: str,
    _route: int,
) -> None:
    del _state, _route
    _snapshot_path(opportunity_id)
    scenario = _scenario(slug)
    analysis = analyze(opportunity_id, "simulated")
    rows = synthetic_evidence_rows(scenario)

    assert rows
    assert all(
        row["synthetic_flag"] is True
        and row["evidence_class"] == "D"
        and row["source"] == "DEMO_GENERATOR"
        and row["display_label"] == "SIMULATED — NOT MINISTRY EVIDENCE"
        for row in rows
    )
    assert all(
        assessment["actual_evidence_class"] == "D"
        for assessment in analysis["simulation_decision"][
            "evidence_class_assessment"
        ].values()
    )
    assert analysis["simulation_decision"]["advance_gate"]["basis"] == (
        "CLASS_IF_CONFIRMED"
    )
    dossier = build_dossier(analysis)
    for locale, label in (
        ("en", "SIMULATED — NOT MINISTRY EVIDENCE"),
        ("ar", "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة"),
    ):
        assert label in render_dossier_html(dossier, locale=locale)


@pytest.mark.parametrize(
    "opportunity_id",
    S14_IDS,
    ids=[row[1].lower() for row in S14_CASES],
)
def test_s14_public_views_carry_no_synthetic_marker(
    opportunity_id: str,
) -> None:
    _snapshot_path(opportunity_id)
    analysis = analyze(opportunity_id, "public")
    encoded = json.dumps(analysis, ensure_ascii=False)

    assert not any(
        row.get("synthetic_flag") is True for row in analysis["evidence"]
    )
    assert not any(
        row.get("synthetic_flag") is True for row in analysis["rules"]
    )
    for forbidden in (
        "DEMO_GENERATOR",
        "SYN-MINISTRY",
        "SIMULATED — NOT MINISTRY EVIDENCE",
        "محاكاة — ليست بيانات أو أدلة صادرة عن الوزارة",
    ):
        assert forbidden not in encoded


def test_721061_partner_detail_state_is_carried_not_zero() -> None:
    opportunity_id = "SAU-H6-721061"
    _snapshot_path(opportunity_id)
    public = get_public_case(opportunity_id)
    brief = json.loads(
        (
            PROJECT_ROOT
            / "data/cases/briefs/CASE-BRIEF-SAU-H6-721061-v1.json"
        ).read_text(encoding="utf-8")
    )
    detail = public["partner_detail"]
    analysis = analyze(opportunity_id, "public")
    r3 = next(row for row in analysis["rules"] if row["rule_id"] == "R3")
    r4d = next(row for row in analysis["rules"] if row["rule_id"] == "R4-D")

    assert detail["state"] in {
        "PARTNER_DETAIL_MISSING",
        "PARTNER_DETAIL_OBSERVED",
    }
    assert detail["state"] == brief["partner_detail"]["state"]
    assert detail["state"] != "PARTNER_TRADE_OBSERVED_ZERO"
    if detail["state"] == "PARTNER_DETAIL_MISSING":
        assert public["partner_observations"] == "UNAVAILABLE"
        assert detail["observed_partner_rows"] == "UNAVAILABLE"
        assert detail["attempt_passport_ids"]
        assert r3["result_code"] == "PARTNER_DETAIL_MISSING"
        assert r4d["result_code"] == "PARTNER_DETAIL_MISSING"
        assert r3["result_values"]["partner_detail_reason"] == detail["reason"]
        assert r3["metrics"]["value"]["reason"].startswith(
            "PARTNER_DETAIL_MISSING:"
        )
        assert r3["metrics"]["quantity"]["reason"].startswith(
            "PARTNER_DETAIL_MISSING:"
        )
        assert analysis["supplier_metrics"] is None
        dossier = build_dossier(analysis)
        assert dossier["partner_detail"]["state"] == "PARTNER_DETAIL_MISSING"
        metric_grid = next(
            row
            for row in build_ui_manifest(analysis)["components"]
            if row["type"] == "metric_grid"
        )
        assert metric_grid["props"]["partner_detail"]["state"] == (
            "PARTNER_DETAIL_MISSING"
        )
    else:
        observations = public["partner_observations"]
        assert isinstance(observations, list) and observations
        assert detail["observed_partner_rows"] == len(observations)
        assert r3["result_code"] not in {
            "PARTNER_DETAIL_MISSING",
            "PARTNER_TRADE_OBSERVED_ZERO",
        }
        assert any(
            evidence["evidence_id"].endswith("PARTNERS-ATTEMPT")
            or "-PARTNERS-ATTEMPT-" in evidence["evidence_id"]
            for evidence in public["evidence"]
        )


def _partner_state_double(state: str, reason: str | None) -> dict:
    case = deepcopy(get_public_case("SAU-H0-390210"))
    case["schema_version"] = "2.2.0"
    case["partner_observations"] = "UNAVAILABLE"
    case.pop("disclosed_concentration", None)
    case.pop("disclosed_dispersion", None)
    case["partner_detail"] = {
        "state": state,
        "reason": reason,
        "source_id": "UNAVAILABLE",
        "partner_snapshot_id": "UNAVAILABLE",
        "unit_key": ["390210", "imports", "2024"],
        "observed_partner_rows": (
            "UNAVAILABLE" if state == "PARTNER_DETAIL_MISSING" else 0
        ),
        "attempt_passport_ids": [],
        "observed_passport_id": None,
    }
    return case


def test_zero_state_is_distinguishable_from_missing_on_doubles() -> None:
    generic = deepcopy(get_public_case("SAU-H0-390210"))
    generic.pop("disclosed_concentration", None)
    generic.pop("disclosed_dispersion", None)
    missing = _partner_state_double(
        "PARTNER_DETAIL_MISSING",
        "NOT_ACQUIRED",
    )
    zero = _partner_state_double(
        "PARTNER_TRADE_OBSERVED_ZERO",
        None,
    )

    generic_rows = {
        row["rule_id"]: row for row in evaluate_rules(generic)
    }
    missing_rows = {
        row["rule_id"]: row
        for row in localize_rule_rows(evaluate_rules(missing))
    }
    zero_rows = {
        row["rule_id"]: row
        for row in localize_rule_rows(evaluate_rules(zero))
    }

    assert generic_rows["R3"]["result_code"] == "BOTH_BASES_NOT_CALCULABLE"
    assert generic_rows["R4-D"]["result_code"] == "COVERAGE_INSUFFICIENT"
    assert missing_rows["R3"]["result_code"] == "PARTNER_DETAIL_MISSING"
    assert missing_rows["R4-D"]["result_code"] == "PARTNER_DETAIL_MISSING"
    assert zero_rows["R3"]["result_code"] == "PARTNER_TRADE_OBSERVED_ZERO"
    assert zero_rows["R4-D"]["result_code"] == (
        "PARTNER_TRADE_OBSERVED_ZERO"
    )
    assert missing_rows["R3"]["localized"] != zero_rows["R3"]["localized"]
    assert "missing evidence, not zero trade" in missing_rows["R3"]["result"]
    assert "OBSERVED ZERO" in zero_rows["R3"]["result"]
    assert missing_rows["R3"]["metrics"]["value"]["hhi"] == (
        "NOT_CALCULABLE"
    )
    assert zero_rows["R3"]["metrics"]["value"]["hhi"] == (
        "NOT_CALCULABLE"
    )


def test_partner_scaling_six_decimals_preserves_721061_value_reconciliation(
) -> None:
    from ior_mvp.cases.projection import _scaled

    partner_primary_values = (
        15_760.266,
        1_604_501.293,
        9_149_270.971,
        45_089.066,
        9_260.8,
        1_010_515.975,
        59_314_867.85,
    )
    world_primary_value = 71_149_266.221

    scaled_sum = sum(float(_scaled(value)) for value in partner_primary_values)
    scaled_world = float(_scaled(world_primary_value))
    assert scaled_sum == pytest.approx(scaled_world, abs=1e-6)
    for decimal_places in (3, 4):
        coarser_sum = sum(
            round(value / 1_000_000, decimal_places)
            for value in partner_primary_values
        )
        coarser_world = round(
            world_primary_value / 1_000_000,
            decimal_places,
        )
        assert coarser_sum != pytest.approx(coarser_world, abs=1e-6)
