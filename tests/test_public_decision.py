from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from ior_mvp.config import PROJECT_ROOT, evidence_policy_config
from ior_mvp.data_repository import get_public_case
from ior_mvp.capability import evaluate_capability
from ior_mvp.evidence import evaluate_advance_gate
from ior_mvp.public_decision import (
    DECISION_CRITICAL_FIELDS,
    DECISION_REASON_CODES,
    REJECTION_NARRATIVE_KEYS,
    DecisionIntegrityError,
    _render_public_narrative,
    compute_public_decision,
    derive_rejection_conditions,
    screen_candidate,
    select_deep_state,
)
from ior_mvp.public_snapshot import (
    PublicSnapshotIntegrityError,
    validate_public_snapshot,
)
from ior_mvp.signals import advance_supporting_signal_rule_ids
from ior_mvp.rules import evaluate_rules
from ior_mvp.public_snapshot import capability_hard_gate_names


FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "public_decision"
FIXTURES = {
    "advance": "advance-route-3.json",
    "monitor": "monitor-r3-only.json",
    "reject_exclusion": "reject-hard-exclusion.json",
    "reject_equivalence": "reject-equivalence.json",
}


def _resolved_assessments() -> dict[str, dict]:
    return {
        field: {
            "field": field,
            "evidence_class": "C",
            "resolution_status": "RESOLVED",
        }
        for field in DECISION_CRITICAL_FIELDS
    }


def _advance_gate(
    assessments: dict[str, dict] | None = None,
) -> dict:
    return evaluate_advance_gate(
        assessments or _resolved_assessments(),
        evidence_policy_config()["advance_gate"],
    )


def _exclusions(status: str = "NOT_SATISFIED") -> list[dict]:
    return [
        {
            "code": f"EX-{index:02d}",
            "status": status,
            "evidence_ids": [],
        }
        for index in range(1, 7)
    ]


def _rejections(status: str = "NOT_SATISFIED") -> list[dict]:
    return [
        {
            "code": code,
            "status": status,
            "evidence_ids": [],
        }
        for code in (
            "hard_exclusion",
            "false_or_measurement_gap",
            "equivalent_idle_qualified_supply",
            "uneconomic_at_efficient_scale",
            "structural_overcapacity",
            "generic_capacity_contradicted",
        )
    ]


def _rules(**fired: bool | None) -> list[dict]:
    return [
        {
            "rule_id": rule_id,
            "fired": fired.get(rule_id, False),
        }
        for rule_id in (
            "R1-D",
            "R2",
            "R3",
            "R4-D",
            "R5",
            "R6",
            "R7",
            "R8",
            "R9-S",
            "R10",
            "R11",
        )
    ]


def _case(trigger: dict | str = "UNAVAILABLE") -> dict:
    return {
        "decision_inputs": {
            "target_specification_demand": "UNAVAILABLE",
            "specification_equivalence": "UNAVAILABLE",
            "route_evidence": "UNAVAILABLE",
            "monitor_trigger": trigger,
        }
    }


def test_rejection_conditions_compute_pp_generic_capacity_from_r11() -> None:
    case = deepcopy(get_public_case("SAU-H0-390210"))
    case["decision_inputs"] = _case()["decision_inputs"]
    case["evidence"][0]["supports"] = ["EXPORT_IMPORT_RATIO"]

    conditions = derive_rejection_conditions(
        case,
        evaluate_rules(case),
        _exclusions("NOT_CALCULABLE"),
    )

    assert [row["code"] for row in conditions] == [
        "hard_exclusion",
        "false_or_measurement_gap",
        "equivalent_idle_qualified_supply",
        "uneconomic_at_efficient_scale",
        "structural_overcapacity",
        "generic_capacity_contradicted",
    ]
    generic = conditions[-1]
    assert generic["status"] == "SATISFIED"
    assert generic["evidence_ids"] == [
        "P-ADVANCED",
        "P-TASNEE",
        "P-WITS-390210",
    ]


def test_rejection_conditions_compute_equivalent_qualified_supply() -> None:
    case = _case()
    case["decision_inputs"].update(
        {
            "target_specification_demand": {
                "quantity_kt": 100.0,
                "evidence_ids": ["E-DEMAND"],
            },
            "specification_equivalence": {
                "domestic_product_equivalent": True,
                "qualified_available_kt": 120.0,
                "evidence_ids": ["E-EQUIVALENCE"],
            },
        }
    )

    conditions = derive_rejection_conditions(
        case,
        _rules(),
        _exclusions("NOT_CALCULABLE"),
    )

    equivalence = next(
        row
        for row in conditions
        if row["code"] == "equivalent_idle_qualified_supply"
    )
    assert equivalence == {
        "code": "equivalent_idle_qualified_supply",
        "status": "SATISFIED",
        "reason_code": "EQUIVALENT_QUALIFIED_SUPPLY",
        "evidence_ids": ["E-DEMAND", "E-EQUIVALENCE"],
    }


def test_rejection_conditions_compute_uneconomic_at_efficient_scale(
) -> None:
    case = json.loads(
        (FIXTURE_ROOT / FIXTURES["advance"]).read_text(
            encoding="utf-8"
        )
    )
    route = case["decision_inputs"]["route_evidence"][0]
    route["downside_cash_flows_m_sar"] = [-1000.0, 1.0]

    conditions = derive_rejection_conditions(
        case,
        evaluate_rules(case),
        _exclusions(),
    )

    uneconomic = next(
        row
        for row in conditions
        if row["code"] == "uneconomic_at_efficient_scale"
    )
    assert uneconomic == {
        "code": "uneconomic_at_efficient_scale",
        "status": "SATISFIED",
        "reason_code": "UNECONOMIC_AT_EFFICIENT_SCALE",
        "evidence_ids": ["E-ROUTE"],
    }


def test_satisfied_hard_exclusion_selects_reject_route_zero() -> None:
    exclusions = _exclusions()
    exclusions[2]["status"] = "SATISFIED"

    decision = select_deep_state(
        case=_case(),
        rules=_rules(),
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=exclusions,
        rejection_conditions=_rejections(),
        selected_hypothesis=None,
        preferred_hypothesis=None,
        evidence_needs=[],
        advance_support_signal_rule_ids=[],
    )

    assert decision == {
        "state": "REJECT",
        "route_code": 0,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": "HARD_EXCLUSION_SATISFIED",
    }


def test_equivalence_rejection_selects_reject_route_zero() -> None:
    rejections = _rejections()
    rejections[2]["status"] = "SATISFIED"

    decision = select_deep_state(
        case=_case(),
        rules=_rules(),
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=_exclusions("NOT_CALCULABLE"),
        rejection_conditions=rejections,
        selected_hypothesis=None,
        preferred_hypothesis=None,
        evidence_needs=[],
        advance_support_signal_rule_ids=[],
    )

    assert decision["state"] == "REJECT"
    assert decision["route_code"] == 0
    assert decision["decision_reason_code"] == (
        "EQUIVALENT_QUALIFIED_SUPPLY"
    )


def test_passing_selected_route_and_all_gates_select_advance() -> None:
    selected = {"route_code": 3, "status": "passes"}

    decision = select_deep_state(
        case=_case(),
        rules=_rules(**{"R9-S": True}),
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=_exclusions(),
        rejection_conditions=_rejections(),
        selected_hypothesis=selected,
        preferred_hypothesis=selected,
        evidence_needs=[],
        advance_support_signal_rule_ids=["R9-S"],
    )

    assert decision == {
        "state": "ADVANCE",
        "route_code": 3,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": "ALL_ADVANCE_GATES_PASS",
    }


def test_unresolved_fact_with_positive_route_value_selects_investigate() -> None:
    assessments = _resolved_assessments()
    assessments["product_identity"].update(
        {"evidence_class": "E", "resolution_status": "MISSING"}
    )

    decision = select_deep_state(
        case=_case(),
        rules=_rules(**{"R1-D": True}),
        assessments=assessments,
        advance_gate=_advance_gate(assessments),
        exclusions=_exclusions("NOT_CALCULABLE"),
        rejection_conditions=_rejections("NOT_CALCULABLE"),
        selected_hypothesis=None,
        preferred_hypothesis={"route_code": 5},
        evidence_needs=[
            {
                "need_code": "identity/tariff-line",
                "route_effect": "Can change state or route.",
            }
        ],
        advance_support_signal_rule_ids=[],
    )

    assert decision["state"] == "INVESTIGATE"
    assert decision["route_code"] is None
    assert decision["decision_reason_code"] == (
        "ROUTE_CHANGING_EVIDENCE_UNRESOLVED"
    )


def test_r3_only_with_named_trigger_selects_monitor_route_zero() -> None:
    trigger = {
        "domain": "capacity_state",
        "condition_code": (
            "qualified_supply_falls_below_target_demand"
        ),
        "evidence_ids": ["E-TRIGGER"],
    }

    decision = select_deep_state(
        case=_case(trigger),
        rules=_rules(R3=True, R10=True),
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=_exclusions(),
        rejection_conditions=_rejections(),
        selected_hypothesis=None,
        preferred_hypothesis={"route_code": 0},
        evidence_needs=[],
        advance_support_signal_rule_ids=[],
    )

    assert decision == {
        "state": "MONITOR",
        "route_code": 0,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": "NAMED_TRIGGER_MONITOR",
        "monitor_trigger": trigger,
    }


@pytest.mark.parametrize(
    "trigger",
    [
        "UNAVAILABLE",
        {
            "domain": "invented",
            "condition_code": "anything",
            "evidence_ids": ["E"],
        },
    ],
)
def test_monitor_without_an_allowed_named_trigger_fails_closed(
    trigger,
) -> None:
    with pytest.raises(DecisionIntegrityError, match="MONITOR"):
        select_deep_state(
            case=_case(trigger),
            rules=_rules(R3=True),
            assessments=_resolved_assessments(),
            advance_gate=_advance_gate(),
            exclusions=_exclusions(),
            rejection_conditions=_rejections(),
            selected_hypothesis=None,
            preferred_hypothesis=None,
            evidence_needs=[],
            advance_support_signal_rule_ids=[],
        )


def test_other_unmatched_residual_still_fails_closed() -> None:
    with pytest.raises(DecisionIntegrityError, match="legal branch"):
        select_deep_state(
            case=_case(),
            rules=_rules(R2=True),
            assessments=_resolved_assessments(),
            advance_gate={"passes": False},
            exclusions=_exclusions(),
            rejection_conditions=_rejections(),
            selected_hypothesis={"route_code": 3, "status": "passes"},
            preferred_hypothesis={"route_code": 3, "status": "passes"},
            evidence_needs=[],
            advance_support_signal_rule_ids=["R2"],
        )


def test_screening_helper_never_assigns_a_formal_deep_state() -> None:
    assert screen_candidate(
        has_candidate_trigger=False,
        screen_exclusion_satisfied=False,
    ) == {
        "screening_disposition": "NO_CANDIDATE",
        "state": None,
    }
    assert screen_candidate(
        has_candidate_trigger=True,
        screen_exclusion_satisfied=True,
    ) == {
        "screening_disposition": "SCREENED_OUT",
        "state": None,
    }


def test_four_public_decision_fixtures_are_complete_physical_json() -> None:
    expected_ids = {
        "advance": "FIX-PUBLIC-ADVANCE-ROUTE-3",
        "monitor": "FIX-PUBLIC-MONITOR-R3-ONLY",
        "reject_exclusion": "FIX-PUBLIC-REJECT-HARD-EXCLUSION",
        "reject_equivalence": "FIX-PUBLIC-REJECT-EQUIVALENCE",
    }
    for key, filename in FIXTURES.items():
        path = FIXTURE_ROOT / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["schema_version"] == "2.1.0"
        assert payload["snapshot_id"] == expected_ids[key]
        assert payload["opportunity"]["id"] == expected_ids[key]
        assert payload["supersedes"] == "UNAVAILABLE"
        assert payload["source_boundary"] == "public"
        assert payload["evidence"]
        assert "$ref" not in path.read_text(encoding="utf-8")


def _compute(case: dict) -> dict:
    capability = evaluate_capability(
        case["opportunity"]["sector_profile"],
        case["domestic_capability"]["public_dimension_states"],
        case["domestic_capability"]["profile_hard_gates"],
        capability_hard_gate_names(case["domestic_capability"]),
    )
    rules = evaluate_rules(case)
    return compute_public_decision(case, rules, capability)


def test_no_fired_signal_deep_case_is_no_candidate_with_null_state() -> None:
    case = json.loads(
        (
            FIXTURE_ROOT / "no-candidate-no-fired-signal.json"
        ).read_text(encoding="utf-8")
    )
    validate_public_snapshot(case)

    result = _compute(case)

    assert result["state"] is None
    assert result["route_code"] is None
    assert result["screening_disposition"] == "NO_CANDIDATE"
    assert result["decision_reason_code"] == "NO_TRIGGER_FIRED"
    assert result["advance_support_signal_rule_ids"] == []
    assert re.search(
        r"[\u0600-\u06ff]",
        result["localized_narrative"]["ar"]["headline"]["text"],
    )
    assert len(result["conditions"]) == 1
    assert result["kill_conditions"] == []


def test_no_trigger_fired_is_a_registered_decision_reason_code() -> None:
    assert "NO_TRIGGER_FIRED" in DECISION_REASON_CODES


@pytest.mark.parametrize(
    ("filename", "state", "route_code"),
    [
        ("advance-route-3.json", "ADVANCE", 3),
        ("monitor-r3-only.json", "MONITOR", 0),
        ("reject-hard-exclusion.json", "REJECT", 0),
        ("reject-equivalence.json", "REJECT", 0),
    ],
)
def test_exact_public_decision_fixtures_cover_all_formal_branches(
    filename: str,
    state: str,
    route_code: int,
) -> None:
    case = json.loads(
        (FIXTURE_ROOT / filename).read_text(encoding="utf-8")
    )

    result = _compute(case)

    assert result["state"] == state
    assert result["route_code"] == route_code
    assert result["screening_disposition"] == "CANDIDATE"
    assert len(result["route_hypotheses"]) == 9
    assert result["narrative_version"] == "1.0.0"
    assert result["headline"] == result["localized_narrative"]["en"][
        "headline"
    ]["text"]


def test_advance_fixture_exact_route_economics_and_field_gate() -> None:
    result = _compute(
        json.loads(
            (FIXTURE_ROOT / FIXTURES["advance"]).read_text(
                encoding="utf-8"
            )
        )
    )

    assert result["state"] == "ADVANCE"
    assert result["preferred_hypothesis"]["route_code"] == 3
    assert result["advance_gate"]["passes"] is True
    assert {
        field: assessment["evidence_class"]
        for field, assessment in result[
            "evidence_class_assessment"
        ].items()
    } == {
        "product_identity": "B",
        "demand_at_required_specification": "B",
        "domestic_supply_or_capability": "C",
        "hard_regulatory_or_process_gate": "C",
    }
    route = result["route_hypotheses"][3]
    assert route["status"] == "passes"
    assert route["incremental_national_value_m_sar"] == 66.0
    assert route["competition"]["capacity_ratio"] == 1.0


def test_unknown_exclusions_reduce_permission_to_investigate() -> None:
    case = json.loads(
        (FIXTURE_ROOT / FIXTURES["advance"]).read_text(
            encoding="utf-8"
        )
    )
    for block in case["hard_exclusion_inputs"].values():
        for key in list(block):
            block[key] = [] if key == "evidence_ids" else "UNAVAILABLE"

    result = _compute(case)

    assert result["advance_gate"]["passes"] is True
    assert all(
        row["status"] == "NOT_CALCULABLE"
        for row in result["hard_exclusions"]
    )
    assert result["state"] == "INVESTIGATE"
    assert result["route_code"] is None
    assert result["missing_facts"]


@pytest.mark.parametrize(
    ("passport_id", "field"),
    [
        ("E-ID", "product_identity"),
        ("E-DEMAND", "demand_at_required_specification"),
        ("E-CAP", "domestic_supply_or_capability"),
        ("E-GATE", "hard_regulatory_or_process_gate"),
    ],
)
@pytest.mark.parametrize("evidence_class", ["D", "E"])
def test_each_single_field_d_or_e_downgrades_advance_to_investigate(
    passport_id: str,
    field: str,
    evidence_class: str,
) -> None:
    case = json.loads(
        (FIXTURE_ROOT / FIXTURES["advance"]).read_text(
            encoding="utf-8"
        )
    )
    passport = next(
        item
        for item in case["evidence"]
        if item["evidence_id"] == passport_id
    )
    passport["evidence_class"] = evidence_class

    result = _compute(case)

    assert result["state"] == "INVESTIGATE"
    assert result["route_code"] is None
    resolution = (
        "UNRESOLVED"
        if field
        in {
            "domestic_supply_or_capability",
            "hard_regulatory_or_process_gate",
        }
        else "RESOLVED"
    )
    reasons = ["BLOCKED_CLASS"]
    if resolution == "UNRESOLVED":
        reasons.append("BLOCKED_RESOLUTION")
    assert result["advance_gate"]["blocked_fields"] == [
        {
            "field": field,
            "evidence_class": evidence_class,
            "resolution_status": resolution,
            "reasons": reasons,
        }
    ]


@pytest.mark.parametrize(
    ("opportunity_id", "expected"),
    [
        (
            "SAU-H0-721049",
            {
                "state": "INVESTIGATE",
                "route_code": None,
                "headline": (
                    "INVESTIGATE — binding constraint unresolved"
                ),
                "route_label": "Brownfield priority to test",
                "rationale": (
                    "Test brownfield first; greenfield is not "
                    "justified from public evidence."
                ),
            },
        ),
        (
            "SAU-H0-390210",
            {
                "state": "REJECT",
                "route_code": 0,
                "headline": "REJECT — generic capacity support",
                "route_label": "No intervention for generic capacity",
                "rationale": (
                    "Reject generic polypropylene capacity support; "
                    "investigate only explicitly defined "
                    "grade/application exceptions."
                ),
            },
        ),
    ],
)
def test_public_goldens_are_computed_with_exact_compatibility_copy(
    opportunity_id: str,
    expected: dict,
) -> None:
    result = _compute(deepcopy(get_public_case(opportunity_id)))

    assert {
        key: result[key]
        for key in (
            "state",
            "route_code",
            "headline",
            "route_label",
            "rationale",
        )
    } == expected
    assert len(result["missing_facts"]) == 5
    assert result["confidence"] == "C"


def _load_fixture(name: str) -> dict:
    return json.loads(
        (FIXTURE_ROOT / name).read_text(encoding="utf-8")
    )


def _degraded_signal_trade(case: dict) -> dict:
    variant = deepcopy(case)
    variant["trade"] = [
        {
            "year": 2024,
            "imports_usd_m": 8.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
        {
            "year": 2025,
            "imports_usd_m": 9.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
        {
            "year": 2026,
            "imports_usd_m": 10.0,
            "imports_kt": 10.0,
            "exports_usd_m": 1.0,
            "exports_kt": 1.0,
        },
    ]
    return variant


def _route_unavailable(case: dict) -> dict:
    variant = deepcopy(case)
    variant["decision_inputs"]["route_evidence"] = "UNAVAILABLE"
    return variant


def _missing_route_economics(case: dict, *, mutation: str) -> dict:
    variant = deepcopy(case)
    record = variant["decision_inputs"]["route_evidence"][0]
    if mutation == "delete":
        del record["downside_cash_flows_m_sar"]
    elif mutation == "cash_unavailable":
        record["downside_cash_flows_m_sar"] = "UNAVAILABLE"
    else:
        record["hurdle_rate"] = "UNAVAILABLE"
    return variant


def _uneconomic(case: dict) -> dict:
    variant = deepcopy(case)
    variant["decision_inputs"]["route_evidence"][0][
        "downside_cash_flows_m_sar"
    ] = [-1000.0, 1.0]
    return variant


def _confidence_cap(case: dict) -> dict:
    variant = _degraded_signal_trade(case)
    for passport in variant["evidence"]:
        passport["evidence_class"] = "B"
    return variant


def _all_b(case: dict) -> dict:
    variant = deepcopy(case)
    for passport in variant["evidence"]:
        passport["evidence_class"] = "B"
    return variant


def _preferred_route_zero_investigate(case: dict) -> dict:
    variant = deepcopy(case)
    passport = next(
        item for item in variant["evidence"] if item["evidence_id"] == "E-ID"
    )
    passport["evidence_class"] = "D"
    return variant


def test_advance_fixture_trade_rows_fire_r2_full_quantity_led_growth() -> None:
    case = _load_fixture(FIXTURES["advance"])
    validate_public_snapshot(case)
    assert [row["year"] for row in case["trade"]] == [2025, 2026]
    assert case["trade"][0] == {
        "year": 2025,
        "imports_usd_m": 8.0,
        "imports_kt": 8.0,
        "exports_usd_m": 1.0,
        "exports_kt": 1.0,
    }
    r2 = next(row for row in evaluate_rules(case) if row["rule_id"] == "R2")
    assert r2["execution"] == "FULL" and r2["fired"] is True
    assert r2["metrics"]["from_year"] == 2025
    assert r2["metrics"]["to_year"] == 2026
    assert r2["metrics"]["observed_span_years"] == 1
    assert r2["metrics"]["delta_ln_quantity"] == pytest.approx(
        0.2231, abs=1e-4
    )
    assert r2["metrics"]["delta_ln_unit_value"] == 0.0
    assert r2["metrics"]["quantity_contribution_share"] == 1.0
    assert r2["metrics"]["quantity_cagr"] == pytest.approx(0.25)
    assert next(
        row for row in evaluate_rules(case) if row["rule_id"] == "R1-D"
    )["fired"] is False
    result = _compute(case)
    assert (result["state"], result["route_code"]) == ("ADVANCE", 3)


def test_material_trigger_without_determinable_route_selects_investigate() -> None:
    rejections = _rejections()
    rejections[3]["status"] = "NOT_CALCULABLE"
    decision = select_deep_state(
        case=_case(),
        rules=_rules(R2=True),
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=_exclusions(),
        rejection_conditions=rejections,
        selected_hypothesis=None,
        preferred_hypothesis=None,
        evidence_needs=[
            {
                "need_code": "route economics",
                "route_effect": (
                    "Can determine whether the plausible route "
                    "proceeds unsupported."
                ),
            }
        ],
        advance_support_signal_rule_ids=[],
    )
    assert decision == {
        "state": "INVESTIGATE",
        "route_code": None,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": "ROUTE_DETERMINATION_UNRESOLVED",
    }


def test_unavailable_route_economics_without_material_trigger_does_not_select_investigate() -> None:
    with pytest.raises(DecisionIntegrityError, match="MONITOR"):
        select_deep_state(
            case=_case("UNAVAILABLE"),
            rules=_rules(R3=True),
            assessments=_resolved_assessments(),
            advance_gate=_advance_gate(),
            exclusions=_exclusions(),
            rejection_conditions=_rejections(),
            selected_hypothesis=None,
            preferred_hypothesis=None,
            evidence_needs=[],
            advance_support_signal_rule_ids=[],
        )


def test_route_unavailable_variant_investigates_with_route_need() -> None:
    case = _route_unavailable(_load_fixture(FIXTURES["advance"]))
    result = _compute(case)
    assert result["state"] == "INVESTIGATE"
    assert result["route_code"] is None
    assert (
        result["decision_reason_code"]
        == "ROUTE_DETERMINATION_UNRESOLVED"
    )
    assert result["preferred_hypothesis"] is None
    assert result["route_label"] == "Route not yet determined"
    assert (
        result["localized_narrative"]["ar"]["route_label"]["text"]
        == "لم يُحدد المسار بعد"
    )
    assert result["rationale"] == (
        "No route hypothesis can be preferred from public evidence; "
        "resolve the named route evidence before any support decision."
    )
    assert result["missing_facts"] == [
        (
            "Route feasibility, additionality, policy and downside "
            "economics evidence for the candidate routes"
        )
    ]


@pytest.mark.parametrize("mutation", ["delete", "cash_unavailable", "hurdle"])
def test_advance_fixture_minus_route_economics_computes_investigate_with_economics_unavailable(
    mutation: str,
) -> None:
    case = _missing_route_economics(
        _load_fixture(FIXTURES["advance"]),
        mutation=mutation,
    )
    result = _compute(case)
    assert result["state"] == "INVESTIGATE"
    assert result["route_code"] is None
    assert (
        result["decision_reason_code"]
        == "ROUTE_DETERMINATION_UNRESOLVED"
    )
    assert result["preferred_hypothesis"] is None
    assert result["screening_disposition"] == "CANDIDATE"
    assert result["advance_gate"]["passes"] is True
    assert all(
        row["status"] == "NOT_SATISFIED"
        for row in result["hard_exclusions"]
    )
    route = result["route_hypotheses"][3]
    assert route["status"] == "NOT_CALCULABLE"
    assert "ECONOMICS_UNAVAILABLE" in route["reason_codes"]
    assert route["economics"]["unsupported_npv_m"] == "NOT_CALCULABLE"
    uneconomic = next(
        row
        for row in result["rejection_conditions"]
        if row["code"] == "uneconomic_at_efficient_scale"
    )
    assert uneconomic["status"] == "NOT_CALCULABLE"
    assert uneconomic["reason_code"] == (
        "EFFICIENT_SCALE_ECONOMICS_UNAVAILABLE"
    )
    assert result["missing_facts"] == [
        (
            "Route feasibility, additionality, policy and downside "
            "economics evidence for the candidate routes"
        )
    ]
    assert result["headline"] == (
        "INVESTIGATE — binding constraint unresolved"
    )
    assert result["localized_narrative"]["ar"]["headline"]["text"]


def test_missing_route_cash_flows_still_fail_snapshot_validation() -> None:
    case = _missing_route_economics(
        _load_fixture(FIXTURES["advance"]),
        mutation="delete",
    )
    with pytest.raises(PublicSnapshotIntegrityError):
        validate_public_snapshot(case)


def test_degraded_only_signal_variant_investigates_with_preferred_route_narrative() -> None:
    case = _degraded_signal_trade(_load_fixture(FIXTURES["advance"]))
    result = _compute(case)
    assert result["state"] == "INVESTIGATE"
    assert result["route_code"] is None
    assert (
        result["decision_reason_code"]
        == "ADVANCE_SUPPORT_SIGNAL_DEGRADED"
    )
    assert result["advance_support_signal_rule_ids"] == []
    preferred = result["preferred_hypothesis"]
    assert preferred["route_code"] == 3
    assert (
        preferred["selection_basis"]
        == "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE"
    )
    assert result["route_label"] == (
        "Certification support priority to test"
    )
    assert (
        result["localized_narrative"]["ar"]["route_label"]["text"]
        == "أولوية اختبار دعم الشهادات"
    )
    assert result["rationale"] == (
        "Preferred hypothesis: Certification support; resolve the "
        "named evidence before any support decision."
    )
    assert (
        result["localized_narrative"]["ar"]["rationale"]["text"]
        == (
            "الفرضية المفضلة: دعم الشهادات؛ احسم الأدلة المسماة "
            "قبل أي قرار دعم."
        )
    )
    assert result["missing_facts"] == [
        "Re-export and domestic-origin flow decomposition"
    ]
    assert result["advance_gate"]["passes"] is True
    assert all(
        row["status"] == "NOT_SATISFIED"
        for row in result["hard_exclusions"]
    )


def test_g1_fixture_fires_r2_full_and_supports_advance() -> None:
    case = _load_fixture(FIXTURES["advance"])
    assert advance_supporting_signal_rule_ids(
        evaluate_rules(case)
    ) == ["R2"]
    result = _compute(case)
    assert result["advance_support_signal_rule_ids"] == ["R2"]
    assert result["decision_reason_code"] == "ALL_ADVANCE_GATES_PASS"
    assert result["state"] == "ADVANCE"
    assert result["route_code"] == 3
    assert result["headline"] == "ADVANCE — route 3"


def test_advance_requires_non_empty_supporting_signal_set() -> None:
    selected = {"route_code": 3, "status": "passes"}
    base = dict(
        case=_case(),
        rules=_rules(R2=True),
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=_exclusions(),
        rejection_conditions=_rejections(),
        selected_hypothesis=selected,
        preferred_hypothesis=selected,
        evidence_needs=[],
    )
    assert select_deep_state(
        **base,
        advance_support_signal_rule_ids=["R2"],
    ) == {
        "state": "ADVANCE",
        "route_code": 3,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": "ALL_ADVANCE_GATES_PASS",
    }
    assert select_deep_state(
        **base,
        advance_support_signal_rule_ids=[],
    ) == {
        "state": "INVESTIGATE",
        "route_code": None,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": "ADVANCE_SUPPORT_SIGNAL_DEGRADED",
    }


def test_config_disallowed_signal_blocks_advance() -> None:
    case = _load_fixture(FIXTURES["advance"])
    rules = evaluate_rules(case)
    assert advance_supporting_signal_rule_ids(
        rules,
        {"R2": {"may_support_advance": False}},
    ) == []
    selected = {"route_code": 3, "status": "passes"}
    decision = select_deep_state(
        case=case,
        rules=rules,
        assessments=_resolved_assessments(),
        advance_gate=_advance_gate(),
        exclusions=_exclusions(),
        rejection_conditions=_rejections(),
        selected_hypothesis=selected,
        preferred_hypothesis=selected,
        evidence_needs=[],
        advance_support_signal_rule_ids=[],
    )
    assert decision["state"] == "INVESTIGATE"
    assert (
        decision["decision_reason_code"]
        == "ADVANCE_SUPPORT_SIGNAL_DEGRADED"
    )


def test_fired_rule_confidence_cap_bounds_decision_confidence() -> None:
    cap_result = _compute(
        _confidence_cap(_load_fixture(FIXTURES["advance"]))
    )
    assert cap_result["state"] == "INVESTIGATE"
    assert cap_result["confidence"] == "C"
    all_b = _compute(_all_b(_load_fixture(FIXTURES["advance"])))
    assert all_b["state"] == "ADVANCE"
    assert all_b["confidence"] == "B"


def test_invalid_confidence_cap_fails_closed() -> None:
    case = _load_fixture(FIXTURES["advance"])
    rules = evaluate_rules(case)
    for row in rules:
        if row["rule_id"] == "R2":
            row["metrics"]["confidence_cap"] = "Z"
    capability = evaluate_capability(
        case["opportunity"]["sector_profile"],
        case["domestic_capability"]["public_dimension_states"],
        case["domestic_capability"]["profile_hard_gates"],
        capability_hard_gate_names(case["domestic_capability"]),
    )
    with pytest.raises(DecisionIntegrityError, match="confidence cap"):
        compute_public_decision(case, rules, capability)


def test_preferred_route_zero_investigate_renders_route_unresolved_text() -> None:
    case = _preferred_route_zero_investigate(
        _load_fixture(FIXTURES["monitor"])
    )
    result = _compute(case)
    assert result["state"] == "INVESTIGATE"
    assert (
        result["decision_reason_code"]
        == "ROUTE_CHANGING_EVIDENCE_UNRESOLVED"
    )
    preferred = result["preferred_hypothesis"]
    assert preferred["route_code"] == 0
    assert (
        preferred["selection_basis"] == "MONITOR_NO_IMMEDIATE_ACTION"
    )
    assert result["route_label"] == "Route not yet determined"
    assert (
        result["localized_narrative"]["ar"]["route_label"]["text"]
        == "لم يُحدد المسار بعد"
    )
    assert result["rationale"] == (
        "No route hypothesis can be preferred from public evidence; "
        "resolve the named route evidence before any support decision."
    )
    assert result["missing_facts"] == [
        "Saudi tariff-line and invoice description"
    ]


def test_uneconomic_rejection_renders_typed_governed_narrative() -> None:
    case = _uneconomic(_load_fixture(FIXTURES["advance"]))
    result = _compute(case)
    assert result["state"] == "REJECT"
    assert result["route_code"] == 0
    assert (
        result["decision_reason_code"]
        == "UNECONOMIC_AT_EFFICIENT_SCALE"
    )
    assert result["headline"] == (
        "REJECT — uneconomic at efficient scale"
    )
    assert result["route_label"] == "No intervention"
    assert result["rationale"] == (
        "No technically feasible route passes downside economics at "
        "minimum efficient scale; capacity support is not justified."
    )
    assert result["conditions"] == [
        (
            "Reopen only with new downside economics that pass the "
            "hurdle rate for a technically feasible route."
        )
    ]
    assert result["kill_conditions"] == [
        (
            "Stop capacity support while every feasible route fails "
            "downside economics."
        )
    ]
    ar = result["localized_narrative"]["ar"]
    assert ar["headline"]["text"] == (
        "رفض — غير اقتصادي عند الحد الأدنى للكفاءة"
    )
    assert ar["route_label"]["text"] == "لا تدخل"
    preferred = result["preferred_hypothesis"]
    assert preferred["route_code"] == 0
    assert (
        preferred["selection_basis"] == "EVIDENCED_NO_INTERVENTION"
    )
    uneconomic = next(
        row
        for row in result["rejection_conditions"]
        if row["code"] == "uneconomic_at_efficient_scale"
    )
    assert uneconomic["status"] == "SATISFIED"


def test_every_rejection_reason_code_has_registered_narrative() -> None:
    assert set(REJECTION_NARRATIVE_KEYS) == {
        "HARD_EXCLUSION_SATISFIED",
        "GENERIC_CAPACITY_CONTRADICTED",
        "EQUIVALENT_QUALIFIED_SUPPLY",
        "UNECONOMIC_AT_EFFICIENT_SCALE",
        "FALSE_OR_MEASUREMENT_GAP",
        "STRUCTURAL_OVERCAPACITY",
    }
    catalogue = yaml.safe_load(
        (PROJECT_ROOT / "config" / "decision_narratives.v1.yaml").read_text(
            encoding="utf-8"
        )
    )["templates"]
    for mapping in REJECTION_NARRATIVE_KEYS.values():
        headline, route, rationale, conditions, kills = mapping
        for key in (headline, route, rationale, *conditions, *kills):
            if key is None or key == "exclusion":
                continue
            assert key in catalogue["en"]
            assert key in catalogue["ar"]
    for code, rejection_code in (
        ("FALSE_OR_MEASUREMENT_GAP", "false_or_measurement_gap"),
        ("STRUCTURAL_OVERCAPACITY", "structural_overcapacity"),
    ):
        rejections = _rejections("NOT_CALCULABLE")
        for row in rejections:
            if row["code"] == rejection_code:
                row["status"] = "SATISFIED"
                row["reason_code"] = code
        state = select_deep_state(
            case=_case(),
            rules=_rules(),
            assessments=_resolved_assessments(),
            advance_gate=_advance_gate(),
            exclusions=_exclusions("NOT_CALCULABLE"),
            rejection_conditions=rejections,
            selected_hypothesis=None,
            preferred_hypothesis=None,
            evidence_needs=[],
            advance_support_signal_rule_ids=[],
        )
        assert state["decision_reason_code"] == code
        narrative = _render_public_narrative(
            _case(),
            state,
            None,
            _exclusions("NOT_CALCULABLE"),
            [],
        )
        assert narrative["headline"]
        assert narrative["route_label"] == "No intervention"


def test_unregistered_reject_reason_fails_closed() -> None:
    with pytest.raises(
        DecisionIntegrityError,
        match="Unregistered REJECT reason code",
    ):
        _render_public_narrative(
            _case(),
            {
                "state": "REJECT",
                "route_code": 0,
                "screening_disposition": "CANDIDATE",
                "decision_reason_code": "NOT_A_REASON",
            },
            None,
            _exclusions(),
            [],
        )


def test_decision_reason_code_registry_is_total_and_documented() -> None:
    assert DECISION_REASON_CODES == {
        "HARD_EXCLUSION_SATISFIED",
        "FALSE_OR_MEASUREMENT_GAP",
        "EQUIVALENT_QUALIFIED_SUPPLY",
        "UNECONOMIC_AT_EFFICIENT_SCALE",
        "STRUCTURAL_OVERCAPACITY",
        "GENERIC_CAPACITY_CONTRADICTED",
        "ALL_ADVANCE_GATES_PASS",
        "ADVANCE_SUPPORT_SIGNAL_DEGRADED",
        "ROUTE_CHANGING_EVIDENCE_UNRESOLVED",
        "NAMED_TRIGGER_MONITOR",
        "ROUTE_DETERMINATION_UNRESOLVED",
        "NO_TRIGGER_FIRED",
    }
    core = (
        PROJECT_ROOT / "docs" / "core" / "07_DETERMINISTIC_ENGINE_SPEC.md"
    ).read_text(encoding="utf-8")
    # The S13b T9 integrity contract owns the new Core 07 marker.
    for code in DECISION_REASON_CODES - {"NO_TRIGGER_FIRED"}:
        assert code in core
