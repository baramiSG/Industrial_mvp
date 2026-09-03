from __future__ import annotations

import ast
import json
from copy import deepcopy

import pytest

from ior_mvp.config import PROJECT_ROOT, thresholds_config
from ior_mvp.data_repository import get_public_case
from ior_mvp.evidence import EvidenceIntegrityError
from ior_mvp.route_hypotheses import (
    ROUTE_CONSTRAINTS,
    ROUTE_KEYS,
    apply_precedence,
    evaluate_route_hypotheses,
    select_preferred_hypothesis,
)
from ior_mvp.rules import evaluate_rules


FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "public_decision"


def _fixture(name: str) -> dict:
    return json.loads(
        (FIXTURE_ROOT / name).read_text(encoding="utf-8")
    )


def _rejections(
    satisfied: str | None = None,
) -> list[dict]:
    return [
        {
            "code": code,
            "status": (
                "SATISFIED"
                if code == satisfied
                else "NOT_SATISFIED"
            ),
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
        {"rule_id": rule_id, "fired": fired.get(rule_id, False)}
        for rule_id in ("R3", "R9-S", "R10", "R11")
    ]


def _capability(d_star: float | None = 0.0) -> dict:
    return {
        "route_publishable": d_star is not None,
        "d_star": d_star,
    }


def test_route_keys_order_and_constraint_domains_are_exact() -> None:
    assert ROUTE_KEYS == {
        0: "no_intervention",
        1: "administrative_barrier_removal",
        2: "information_market_linkage",
        3: "certification_testing_quality",
        4: "demand_aggregation_offtake",
        5: "brownfield_incremental_expansion",
        6: "technology_or_jv",
        7: "targeted_greenfield",
        8: "shared_enabler",
    }
    assert ROUTE_CONSTRAINTS == {
        1: {"administrative_or_regulatory"},
        2: {
            "commercial_or_relationship",
            "information_or_market_linkage",
        },
        3: {
            "qualification_or_certification",
            "specification_or_grade",
        },
        4: {"demand_fragmentation_or_offtake"},
        5: {
            "capacity_or_availability",
            "cost_or_competitiveness",
        },
        6: {
            "capability_or_technology",
            "specification_or_grade",
        },
        7: {
            "capacity_or_availability",
            "capability_or_technology",
        },
    }


def test_advance_fixture_emits_nine_routes_and_route_three_passes() -> None:
    case = _fixture("advance-route-3.json")

    hypotheses = evaluate_route_hypotheses(
        case,
        _rules(),
        _capability(),
        {"primary": "application"},
        _rejections(),
    )
    route = hypotheses[3]

    assert [row["route_code"] for row in hypotheses] == list(range(9))
    assert {row["status"] for row in hypotheses} <= {
        "passes",
        "fails",
        "NOT_CALCULABLE",
    }
    assert route["route_key"] == "certification_testing_quality"
    assert hypotheses[0]["status"] == "fails"
    assert route["status"] == "passes"
    assert route["feasibility"] == "passes"
    assert route["resolves_binding_constraint"] == "passes"
    assert route["additionality"] == "passes"
    assert route["policy_permissibility"] == "passes"
    assert route["economics"]["unsupported_npv_m"] == pytest.approx(
        0.413,
        abs=1e-3,
    )
    assert route["economics"]["minimum_effective_support_m"] == 0.0
    assert route["incremental_national_value_m_sar"] == 66.0
    assert route["competition"]["capacity_ratio"] == 1.0
    assert route["evidence_ids"] == ["E-ROUTE"]


def _passing_route(
    code: int,
    value: float,
    *,
    resolves: str = "fails",
) -> dict:
    return {
        "route_code": code,
        "route_key": ROUTE_KEYS[code],
        "status": "passes",
        "resolves_binding_constraint": resolves,
        "incremental_national_value_m_sar": value,
        "unrounded_incremental_national_value_m_sar": value,
        "precedence": {"blocked_by_lower_route": None},
        "reason_codes": [],
        "reasons": [],
        "localized_reasons": {"en": [], "ar": []},
    }


def test_maximum_incremental_national_value_selects_higher_value() -> None:
    hypotheses = [
        _passing_route(5, 80.0),
        _passing_route(6, 120.0),
    ]

    preferred = select_preferred_hypothesis(
        apply_precedence(hypotheses)
    )

    assert preferred is not None
    assert preferred["route_code"] == 6
    assert preferred["selection_basis"] == (
        "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE"
    )


def test_exact_national_value_tie_selects_lower_route_code() -> None:
    hypotheses = [
        _passing_route(5, 120.0),
        _passing_route(6, 120.0),
    ]

    preferred = select_preferred_hypothesis(
        apply_precedence(hypotheses)
    )

    assert preferred is not None
    assert preferred["route_code"] == 5


def test_lower_fully_resolving_route_blocks_every_higher_route() -> None:
    hypotheses = [
        _passing_route(2, 10.0, resolves="passes"),
        _passing_route(5, 200.0),
        _passing_route(6, 300.0),
    ]

    gated = apply_precedence(hypotheses)
    preferred = select_preferred_hypothesis(gated)

    assert preferred is not None
    assert preferred["route_code"] == 2
    assert gated[1]["status"] == gated[2]["status"] == "fails"
    assert gated[1]["precedence"]["blocked_by_lower_route"] == 2
    assert "LOWER_ROUTE_FULLY_RESOLVES" in gated[1]["reason_codes"]


def test_financial_brownfield_is_not_selectable_until_lower_routes_fail(
) -> None:
    case = _fixture("advance-route-3.json")
    evidence = case["decision_inputs"]["route_evidence"][0]
    evidence["route_code"] = 5
    evidence["binding_constraint"] = "capacity_or_availability"

    hypotheses = evaluate_route_hypotheses(
        case,
        _rules(**{"R9-S": True}),
        _capability(0.3),
        {"primary": "quantity"},
        _rejections(),
    )

    assert hypotheses[5]["status"] == "NOT_CALCULABLE"
    assert "LOWER_NONFINANCIAL_ROUTES_UNRESOLVED" in hypotheses[5][
        "reason_codes"
    ]


def test_route_seven_uses_configured_strict_band_mes_and_competition() -> None:
    case = _fixture("advance-route-3.json")
    evidence = case["decision_inputs"]["route_evidence"][0]
    lower_routes = []
    for route_code in range(1, 7):
        failed = deepcopy(evidence)
        failed["route_code"] = route_code
        failed["binding_constraint"] = sorted(
            ROUTE_CONSTRAINTS[route_code]
        )[0]
        failed["technical_feasibility_confirmed"] = False
        lower_routes.append(failed)
    evidence["route_code"] = 7
    evidence["binding_constraint"] = "capability_or_technology"
    case["decision_inputs"]["route_evidence"] = [
        *lower_routes,
        evidence,
    ]
    boundary = float(
        thresholds_config()["capability"]["route_bands"][
            "major_line_or_jv_max"
        ]
    )

    equal = evaluate_route_hypotheses(
        case,
        _rules(),
        _capability(boundary),
        {"primary": "quantity"},
        _rejections(),
    )[7]
    above = evaluate_route_hypotheses(
        case,
        _rules(),
        _capability(boundary + 0.0001),
        {"primary": "quantity"},
        _rejections(),
    )[7]

    assert equal["status"] == "fails"
    assert "ROUTE_7_CAPABILITY_BAND_FAILED" in equal["reason_codes"]
    assert above["status"] == "passes"


def test_route_seven_cannot_leapfrog_unresolved_lower_routes() -> None:
    case = _fixture("advance-route-3.json")
    evidence = case["decision_inputs"]["route_evidence"][0]
    evidence["route_code"] = 7
    evidence["binding_constraint"] = "capability_or_technology"
    boundary = float(
        thresholds_config()["capability"]["route_bands"][
            "major_line_or_jv_max"
        ]
    )

    route = evaluate_route_hypotheses(
        case,
        _rules(),
        _capability(boundary + 0.0001),
        {"primary": "quantity"},
        _rejections(),
    )[7]

    assert route["status"] == "NOT_CALCULABLE"
    assert "LOWER_ROUTES_UNRESOLVED" in route["reason_codes"]


def test_route_eight_is_always_graph_required() -> None:
    hypotheses = evaluate_route_hypotheses(
        _fixture("advance-route-3.json"),
        _rules(),
        _capability(),
        {"primary": "application"},
        _rejections(),
    )

    assert hypotheses[8]["status"] == "NOT_CALCULABLE"
    assert hypotheses[8]["reason_codes"] == ["GRAPH_REQUIRED"]
    assert hypotheses[8]["precedence"]["blocked_by_lower_route"] is None


def test_snapshot_route_eight_evidence_is_rejected() -> None:
    case = _fixture("advance-route-3.json")
    case["decision_inputs"]["route_evidence"][0]["route_code"] = 8

    with pytest.raises(EvidenceIntegrityError, match="route 8"):
        evaluate_route_hypotheses(
            case,
            _rules(),
            _capability(),
            {"primary": "application"},
            _rejections(),
        )


def test_steel_has_preferred_route_five_with_no_formal_selection() -> None:
    case = deepcopy(get_public_case("SAU-H0-721049"))
    case["decision_inputs"] = {
        "target_specification_demand": "UNAVAILABLE",
        "specification_equivalence": "UNAVAILABLE",
        "route_evidence": "UNAVAILABLE",
        "monitor_trigger": "UNAVAILABLE",
    }

    hypotheses = evaluate_route_hypotheses(
        case,
        evaluate_rules(case),
        {"route_publishable": False, "d_star": None},
        {
            "primary": "evidence",
            "constraint_class": "capacity_or_availability",
        },
        _rejections(),
    )
    preferred = select_preferred_hypothesis(hypotheses)

    assert hypotheses[5]["status"] == "NOT_CALCULABLE"
    assert preferred is not None
    assert preferred["route_code"] == 5
    assert preferred["selection_basis"] == (
        "EVIDENCE_PRIORITY_WITH_ECONOMICS_UNAVAILABLE"
    )


def test_pp_route_zero_blocks_routes_one_through_seven() -> None:
    case = deepcopy(get_public_case("SAU-H0-390210"))
    case["decision_inputs"] = {
        "target_specification_demand": "UNAVAILABLE",
        "specification_equivalence": "UNAVAILABLE",
        "route_evidence": "UNAVAILABLE",
        "monitor_trigger": "UNAVAILABLE",
    }

    hypotheses = evaluate_route_hypotheses(
        case,
        evaluate_rules(case),
        {"route_publishable": False, "d_star": None},
        {
            "primary": "evidence",
            "constraint_class": "cost_or_competitiveness",
        },
        _rejections("generic_capacity_contradicted"),
    )
    preferred = select_preferred_hypothesis(hypotheses)

    assert hypotheses[0]["status"] == "passes"
    assert preferred is not None
    assert preferred["route_code"] == 0
    assert all(
        hypotheses[code]["status"] == "fails"
        and hypotheses[code]["precedence"][
            "blocked_by_lower_route"
        ] == 0
        for code in range(1, 8)
    )
    assert hypotheses[8]["status"] == "NOT_CALCULABLE"
    assert hypotheses[8]["reason_codes"] == ["GRAPH_REQUIRED"]


def test_monitor_fixture_route_zero_passes_with_monitor_reason_and_blocks_higher_routes() -> None:
    case = _fixture("monitor-r3-only.json")
    hypotheses = evaluate_route_hypotheses(
        case,
        evaluate_rules(case),
        _capability(0.0),
        {"primary": "resilience"},
        _rejections(),
    )
    assert hypotheses[0]["status"] == "passes"
    assert hypotheses[0]["reason_codes"] == [
        "MONITOR_NO_IMMEDIATE_ACTION"
    ]
    assert hypotheses[0]["reasons"] == [
        (
            "No immediate action is selected while the named "
            "observable trigger is monitored."
        )
    ]
    for code in range(1, 8):
        assert hypotheses[code]["status"] == "fails"
        assert hypotheses[code]["precedence"]["blocked_by_lower_route"] == 0
    assert hypotheses[8]["status"] == "NOT_CALCULABLE"
    assert hypotheses[8]["reason_codes"] == ["GRAPH_REQUIRED"]


def test_preferred_route_zero_reference_uses_monitor_basis_and_reason() -> None:
    case = _fixture("monitor-r3-only.json")
    hypotheses = evaluate_route_hypotheses(
        case,
        evaluate_rules(case),
        _capability(0.0),
        {"primary": "resilience"},
        _rejections(),
    )
    preferred = select_preferred_hypothesis(hypotheses)
    assert preferred is not None
    assert preferred["route_code"] == 0
    assert (
        preferred["selection_basis"] == "MONITOR_NO_IMMEDIATE_ACTION"
    )
    assert preferred["reason_code"] == "MONITOR_NO_IMMEDIATE_ACTION"
    assert preferred["reason"] == (
        "No immediate action is selected while the named "
        "observable trigger is monitored."
    )


def test_passing_route_zero_without_governed_reason_fails_closed() -> None:
    hypotheses = [
        {
            "route_code": 0,
            "status": "passes",
            "reason_codes": ["SOMETHING_ELSE"],
            "incremental_national_value_m_sar": 0.0,
        }
    ]
    with pytest.raises(EvidenceIntegrityError):
        select_preferred_hypothesis(hypotheses)


def test_route_module_ast_has_no_case_identity_or_first_pass_dispatch() -> None:
    path = PROJECT_ROOT / "src" / "ior_mvp" / "route_hypotheses.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    strings = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    assert "SAU-H0-721049" not in strings
    assert "SAU-H0-390210" not in strings
    assert "first passing" not in " ".join(strings).casefold()
