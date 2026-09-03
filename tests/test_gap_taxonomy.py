from __future__ import annotations

from copy import deepcopy

import pytest

from ior_mvp.data_repository import get_public_case
from ior_mvp.public_decision import (
    DecisionIntegrityError,
    _require_one_primary,
    classify_gap,
)
from ior_mvp.rules import evaluate_rules


GAP_ORDER = (
    "false_or_measurement",
    "quantity",
    "specification_or_quality",
    "application",
    "timing",
    "resilience",
    "evidence",
)


def _assessments(resolved: bool = True) -> dict[str, dict]:
    return {
        field: {
            "field": field,
            "evidence_class": "B" if resolved else "E",
            "resolution_status": "RESOLVED" if resolved else "MISSING",
        }
        for field in (
            "product_identity",
            "demand_at_required_specification",
            "domestic_supply_or_capability",
            "hard_regulatory_or_process_gate",
        )
    }


def _rules(**fired: bool | None) -> list[dict]:
    return [
        {
            "rule_id": rule_id,
            "fired": fired.get(rule_id),
            "execution": "FULL",
            "metrics": {},
        }
        for rule_id in ("R3", "R4-D", "R10", "R11")
    ]


def _exclusions(status: str = "NOT_SATISFIED") -> list[dict]:
    return [
        {"code": f"EX-{index:02d}", "status": status}
        for index in range(1, 7)
    ]


def _case() -> dict:
    return {
        "opportunity": {"decision_object_status": "resolved"},
        "decision_inputs": {
            "target_specification_demand": {
                "quantity_kt": 100.0,
                "downside_quantity_kt": 90.0,
                "evidence_ids": ["E-DEMAND"],
            },
            "specification_equivalence": {
                "domestic_product_equivalent": True,
                "qualified_available_kt": 100.0,
                "evidence_ids": ["E-CAP"],
            },
            "route_evidence": "UNAVAILABLE",
            "monitor_trigger": "UNAVAILABLE",
        },
        "domestic_capability": {
            "public_dimension_states": {
                "capacity_time_window": 0,
            }
        },
    }


@pytest.mark.parametrize(
    ("expected", "configure"),
    [
        (
            "evidence",
            lambda case, assessments, rules, exclusions: assessments[
                "product_identity"
            ].update(
                {
                    "evidence_class": "E",
                    "resolution_status": "MISSING",
                }
            ),
        ),
        (
            "false_or_measurement",
            lambda case, assessments, rules, exclusions: rules[3].update(
                {"fired": True}
            ),
        ),
        (
            "quantity",
            lambda case, assessments, rules, exclusions: case[
                "decision_inputs"
            ]["specification_equivalence"].update(
                {"qualified_available_kt": 99.0}
            ),
        ),
        (
            "specification_or_quality",
            lambda case, assessments, rules, exclusions: (
                case["decision_inputs"][
                    "specification_equivalence"
                ].update({"domestic_product_equivalent": False}),
                case["decision_inputs"].update(
                    {
                        "route_evidence": [
                            {
                                "binding_constraint": (
                                    "specification_or_grade"
                                )
                            }
                        ]
                    }
                ),
            ),
        ),
        (
            "application",
            lambda case, assessments, rules, exclusions: (
                case["decision_inputs"][
                    "specification_equivalence"
                ].update({"domestic_product_equivalent": False}),
                case["decision_inputs"].update(
                    {
                        "route_evidence": [
                            {
                                "binding_constraint": (
                                    "qualification_or_certification"
                                )
                            }
                        ]
                    }
                ),
            ),
        ),
        (
            "timing",
            lambda case, assessments, rules, exclusions: case[
                "domestic_capability"
            ]["public_dimension_states"].update(
                {"capacity_time_window": 1}
            ),
        ),
        (
            "resilience",
            lambda case, assessments, rules, exclusions: rules[0].update(
                {"fired": True}
            ),
        ),
    ],
)
def test_each_methodology_primary_gap_branch(
    expected: str,
    configure,
) -> None:
    case = _case()
    assessments = _assessments()
    rules = _rules()
    exclusions = _exclusions()
    configure(case, assessments, rules, exclusions)

    result = classify_gap(case, rules, assessments, exclusions)

    assert result["primary"] == expected
    assert result["primary"] in GAP_ORDER
    assert result["primary"] not in result["secondary"]


def test_unresolved_evidence_overrides_business_hypotheses() -> None:
    case = _case()
    case["decision_inputs"]["specification_equivalence"][
        "qualified_available_kt"
    ] = 50.0
    assessments = _assessments(resolved=False)

    result = classify_gap(
        case,
        _rules(R3=True, R11=True),
        assessments,
        _exclusions("SATISFIED"),
    )

    assert result["primary"] == "evidence"
    assert result["secondary"] == [
        "false_or_measurement",
        "quantity",
        "resilience",
    ]


def test_secondary_classes_are_ordered_unique_and_exclude_primary() -> None:
    case = _case()
    case["decision_inputs"]["specification_equivalence"][
        "qualified_available_kt"
    ] = 90.0

    result = classify_gap(
        case,
        _rules(R3=True, R10=True),
        _assessments(),
        _exclusions(),
    )

    assert result["primary"] == "quantity"
    assert result["secondary"] == ["resilience"]
    assert len(result["secondary"]) == len(set(result["secondary"]))


def test_r4d_alone_never_proves_specification_or_quality() -> None:
    result = classify_gap(
        _case(),
        _rules(**{"R4-D": True}),
        _assessments(),
        _exclusions(),
    )

    assert result["primary"] == "evidence"
    assert "specification_or_quality" not in result["secondary"]


@pytest.mark.parametrize("candidates", [[], ["quantity", "resilience"]])
def test_zero_or_multiple_internal_primary_candidates_fail_closed(
    candidates: list[str],
) -> None:
    with pytest.raises(DecisionIntegrityError, match="primary"):
        _require_one_primary(candidates)


@pytest.mark.parametrize(
    ("opportunity_id", "expected"),
    [
        (
            "SAU-H0-721049",
            {
                "primary": "evidence",
                "secondary": ["resilience"],
                "constraint_class": "capacity_or_availability",
                "reason_codes": [
                    "TARGET_SPECIFICATION_DEMAND_MISSING",
                    "CAPABILITY_GATES_UNRESOLVED",
                    "SUPPLIER_CONCENTRATION_SIGNAL",
                ],
            },
        ),
        (
            "SAU-H0-390210",
            {
                "primary": "evidence",
                "secondary": ["false_or_measurement"],
                "constraint_class": "cost_or_competitiveness",
                "reason_codes": [
                    "TARGET_SPECIFICATION_DEMAND_MISSING",
                    "TARGET_GRADE_UNRESOLVED",
                    "GENERIC_CAPACITY_CONTRADICTED",
                ],
            },
        ),
    ],
)
def test_golden_gap_taxonomy_is_exact(
    opportunity_id: str,
    expected: dict,
) -> None:
    case = deepcopy(get_public_case(opportunity_id))
    case["decision_inputs"] = {
        "target_specification_demand": "UNAVAILABLE",
        "specification_equivalence": "UNAVAILABLE",
        "route_evidence": "UNAVAILABLE",
        "monitor_trigger": "UNAVAILABLE",
    }
    assessments = _assessments()
    assessments["demand_at_required_specification"].update(
        {"evidence_class": "E", "resolution_status": "MISSING"}
    )
    assessments["domestic_supply_or_capability"].update(
        {"evidence_class": "C", "resolution_status": "UNRESOLVED"}
    )
    if opportunity_id == "SAU-H0-721049":
        assessments["product_identity"].update(
            {
                "evidence_class": "C",
                "resolution_status": "CONTRADICTORY",
            }
        )
        assessments["hard_regulatory_or_process_gate"].update(
            {
                "evidence_class": "C",
                "resolution_status": "UNRESOLVED",
            }
        )
    else:
        assessments["product_identity"].update(
            {"evidence_class": "C", "resolution_status": "PARTIAL"}
        )
        assessments["hard_regulatory_or_process_gate"].update(
            {"evidence_class": "E", "resolution_status": "MISSING"}
        )

    result = classify_gap(
        case,
        evaluate_rules(case),
        assessments,
        _exclusions("NOT_CALCULABLE"),
    )

    assert {
        key: result[key]
        for key in (
            "primary",
            "secondary",
            "constraint_class",
            "reason_codes",
        )
    } == expected
    assert result["label"] == result["localized_label"]["en"]
    assert result["localized_label"]["ar"]


def test_simulated_steel_gap_includes_timing_from_capability_dimensions() -> None:
    from ior_mvp.decision_engine import analyze

    result = analyze("SAU-H0-721049", "simulated")["gap_class"]
    assert result["secondary"] == ["timing", "resilience"]


def test_classify_gap_uses_capability_timing_when_public_states_unknown() -> None:
    case = _case()
    capability = {
        "dimensions": [
            {
                "dimension": "capacity_time_window",
                "state": 1,
            }
        ]
    }
    result = classify_gap(
        case,
        _rules(R3=True),
        _assessments(),
        _exclusions(),
        capability,
    )
    assert result["primary"] == "timing"
