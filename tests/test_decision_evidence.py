from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path

import pytest

from ior_mvp.config import PROJECT_ROOT
from ior_mvp.config import evidence_policy_config
from ior_mvp.capability import evaluate_capability
from ior_mvp.data_repository import get_public_case
from ior_mvp.evidence import (
    EvidenceIntegrityError,
    evaluate_advance_gate,
)
from ior_mvp.public_decision import (
    DECISION_CRITICAL_FIELDS,
    FIELD_SUPPORT_CODES,
    SUPPORT_CODES,
    assess_decision_critical_fields,
    compute_public_decision,
)
from ior_mvp.public_snapshot import capability_hard_gate_names
from ior_mvp.rules import evaluate_rules


GOLDEN_SUPPORTS = {
    "S-WITS-721049": [
        "TRADE_VALUE",
        "TRADE_QUANTITY",
        "SUPPLIER_CONCENTRATION",
    ],
    "S-UNICOIL-EPD": [
        "DOMESTIC_NAMEPLATE_CAPACITY",
        "DOMESTIC_PROCESS_ROUTE",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_LABORATORY_METROLOGY",
    ],
    "S-UNICOIL-SPEC": [
        "BILINGUAL_SPECIFICATION_EXTRACTION",
        "DOMESTIC_SPECIFICATION_ENVELOPE",
        "DOMESTIC_DIMENSION_ENVELOPE",
    ],
    "S-HADEED": ["DOMESTIC_PROCESS_FAMILY"],
    "P-WITS-390210": [
        "TRADE_VALUE",
        "TRADE_QUANTITY",
        "EXPORT_IMPORT_RATIO",
    ],
    "P-SABIC": ["DOMESTIC_PRODUCT_PORTFOLIO"],
    "P-ADVANCED": ["DOMESTIC_NAMEPLATE_CAPACITY"],
    "P-TASNEE": ["DOMESTIC_NAMEPLATE_CAPACITY"],
}


def _passport(
    evidence_id: str,
    evidence_class: str,
    supports: list[str],
    *,
    contradiction: str | None = None,
    reviewer_status: str = "confirmed_by_responsible_authority",
    status: str = "observed",
) -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_class": evidence_class,
        "supports": supports,
        "contradiction": contradiction,
        "reviewer_status": reviewer_status,
        "status": status,
    }


def _resolved_case(
    evidence: list[dict],
) -> tuple[dict, dict]:
    case = {
        "opportunity": {"decision_object_status": "resolved"},
        "decision_inputs": {
            "target_specification_demand": {
                "quantity_kt": 100.0,
                "downside_quantity_kt": 90.0,
                "evidence_ids": ["E-DEMAND"],
            }
        },
        "domestic_capability": {
            "profile_hard_gates": {
                "gate": {
                    "status": "RESOLVED",
                    "evidence_ids": ["E-GATE"],
                }
            },
            "unresolved_hard_gates": [],
        },
        "evidence": evidence,
    }
    return case, {"route_publishable": True}


def test_controlled_support_vocabulary_and_field_map_are_exact() -> None:
    assert SUPPORT_CODES == frozenset(
        {
            "TRADE_VALUE",
            "TRADE_QUANTITY",
            "SUPPLIER_CONCENTRATION",
            "EXPORT_IMPORT_RATIO",
            "TARGET_PRODUCT_IDENTITY",
            "TARGET_SPECIFICATION_DEMAND",
            "BILINGUAL_SPECIFICATION_EXTRACTION",
            "DOMESTIC_NAMEPLATE_CAPACITY",
            "DOMESTIC_PROCESS_ROUTE",
            "DOMESTIC_PROCESS_FAMILY",
            "DOMESTIC_PRODUCT_PORTFOLIO",
            "DOMESTIC_SPECIFICATION_ENVELOPE",
            "DOMESTIC_DIMENSION_ENVELOPE",
            "DOMESTIC_LABORATORY_METROLOGY",
            "DOMESTIC_CAPABILITY_ASSESSMENT",
            "HARD_REGULATORY_PROCESS_GATES",
            "ROUTE_ECONOMICS",
            "ROUTE_NATIONAL_VALUE",
            "ROUTE_COMPETITION",
            "MONITOR_TRIGGER",
        }
    )
    assert DECISION_CRITICAL_FIELDS == (
        "product_identity",
        "demand_at_required_specification",
        "domestic_supply_or_capability",
        "hard_regulatory_or_process_gate",
    )
    assert FIELD_SUPPORT_CODES == {
        "product_identity": frozenset(
            {
                "TARGET_PRODUCT_IDENTITY",
                "BILINGUAL_SPECIFICATION_EXTRACTION",
                "DOMESTIC_PRODUCT_PORTFOLIO",
                "DOMESTIC_SPECIFICATION_ENVELOPE",
                "DOMESTIC_DIMENSION_ENVELOPE",
            }
        ),
        "demand_at_required_specification": frozenset(
            {"TARGET_SPECIFICATION_DEMAND"}
        ),
        "domestic_supply_or_capability": frozenset(
            {
                "DOMESTIC_NAMEPLATE_CAPACITY",
                "DOMESTIC_PROCESS_ROUTE",
                "DOMESTIC_PROCESS_FAMILY",
                "DOMESTIC_PRODUCT_PORTFOLIO",
                "DOMESTIC_SPECIFICATION_ENVELOPE",
                "DOMESTIC_LABORATORY_METROLOGY",
                "DOMESTIC_CAPABILITY_ASSESSMENT",
            }
        ),
        "hard_regulatory_or_process_gate": frozenset(
            {
                "DOMESTIC_PROCESS_ROUTE",
                "DOMESTIC_SPECIFICATION_ENVELOPE",
                "DOMESTIC_LABORATORY_METROLOGY",
                "HARD_REGULATORY_PROCESS_GATES",
            }
        ),
    }


@pytest.mark.parametrize("evidence_class", ["A", "B", "C", "D", "E"])
def test_covering_passport_produces_its_actual_evidence_class(
    evidence_class: str,
) -> None:
    evidence = [
        _passport(
            "E-ID",
            evidence_class,
            ["TARGET_PRODUCT_IDENTITY"],
        )
    ]
    case, capability = _resolved_case(evidence)

    assessment = assess_decision_critical_fields(
        case,
        capability,
    )["product_identity"]

    assert assessment["evidence_class"] == evidence_class


def test_unrelated_best_class_passport_never_improves_a_field() -> None:
    case, capability = _resolved_case(
        [
            _passport("E-TRADE", "A", ["TRADE_VALUE"]),
            _passport(
                "E-CAP",
                "C",
                ["DOMESTIC_CAPABILITY_ASSESSMENT"],
            ),
        ]
    )

    assessments = assess_decision_critical_fields(case, capability)

    assert assessments["domestic_supply_or_capability"][
        "evidence_class"
    ] == "C"
    assert assessments["product_identity"] == {
        "field": "product_identity",
        "evidence_class": "E",
        "resolution_status": "MISSING",
        "support_codes": [],
        "evidence_ids": [],
        "contradiction_evidence_ids": [],
    }


def test_unconfirmed_covering_contradiction_blocks_even_with_class_a() -> None:
    case, capability = _resolved_case(
        [
            _passport(
                "E-A",
                "A",
                ["TARGET_PRODUCT_IDENTITY"],
            ),
            _passport(
                "E-CONFLICT",
                "C",
                ["DOMESTIC_SPECIFICATION_ENVELOPE"],
                contradiction="Conflicting target envelope.",
                reviewer_status=(
                    "unconfirmed_by_responsible_authority"
                ),
            ),
        ]
    )

    assessment = assess_decision_critical_fields(
        case,
        capability,
    )["product_identity"]

    assert assessment["evidence_class"] == "A"
    assert assessment["resolution_status"] == "CONTRADICTORY"
    assert assessment["contradiction_evidence_ids"] == ["E-CONFLICT"]


def test_confirmed_covering_contradiction_remains_visible_but_can_resolve(
) -> None:
    case, capability = _resolved_case(
        [
            _passport(
                "E-ID",
                "B",
                ["TARGET_PRODUCT_IDENTITY"],
                contradiction="Confirmed resolution.",
            )
        ]
    )

    assessment = assess_decision_critical_fields(
        case,
        capability,
    )["product_identity"]

    assert assessment["resolution_status"] == "RESOLVED"
    assert assessment["contradiction_evidence_ids"] == ["E-ID"]


def test_unresolved_covering_passport_yields_unresolved_status() -> None:
    case, capability = _resolved_case(
        [
            _passport(
                "E-ID",
                "B",
                ["TARGET_PRODUCT_IDENTITY"],
                status="unresolved",
            )
        ]
    )

    assessment = assess_decision_critical_fields(
        case,
        capability,
    )["product_identity"]

    assert assessment["resolution_status"] == "UNRESOLVED"


def _normalized_golden(opportunity_id: str) -> dict:
    case = deepcopy(get_public_case(opportunity_id))
    for passport in case["evidence"]:
        passport["supports"] = GOLDEN_SUPPORTS[passport["evidence_id"]]
    case["decision_inputs"] = {
        "target_specification_demand": "UNAVAILABLE",
        "specification_equivalence": "UNAVAILABLE",
        "route_evidence": "UNAVAILABLE",
        "monitor_trigger": "UNAVAILABLE",
    }
    return case


@pytest.mark.parametrize(
    ("opportunity_id", "expected"),
    [
        (
            "SAU-H0-721049",
            {
                "product_identity": ("C", "CONTRADICTORY"),
                "demand_at_required_specification": ("E", "MISSING"),
                "domestic_supply_or_capability": ("C", "UNRESOLVED"),
                "hard_regulatory_or_process_gate": (
                    "C",
                    "UNRESOLVED",
                ),
            },
        ),
        (
            "SAU-H0-390210",
            {
                "product_identity": ("C", "PARTIAL"),
                "demand_at_required_specification": ("E", "MISSING"),
                "domestic_supply_or_capability": ("C", "UNRESOLVED"),
                "hard_regulatory_or_process_gate": ("E", "MISSING"),
            },
        ),
    ],
)
def test_golden_field_classes_and_resolution_are_evidence_bounded(
    opportunity_id: str,
    expected: dict[str, tuple[str, str]],
) -> None:
    assessments = assess_decision_critical_fields(
        _normalized_golden(opportunity_id),
        {"route_publishable": False},
    )

    assert {
        field: (
            assessment["evidence_class"],
            assessment["resolution_status"],
        )
        for field, assessment in assessments.items()
    } == expected


def test_public_field_assessor_ast_has_no_source_type_or_case_dispatch(
) -> None:
    path = PROJECT_ROOT / "src" / "ior_mvp" / "public_decision.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "assess_decision_critical_fields"
    )
    names = {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name)
    }
    attributes = {
        node.attr
        for node in ast.walk(function)
        if isinstance(node, ast.Attribute)
    }
    constants = {
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    assert names | attributes | constants
    assert not (
        {
            "source",
            "synthetic_flag",
            "opportunity_id",
            "scenario_id",
            "producer",
            "SAU-H0-721049",
            "SAU-H0-390210",
        }
        & (names | attributes | constants)
    )


def _passing_assessments() -> dict[str, dict]:
    classes = {
        "product_identity": "B",
        "demand_at_required_specification": "B",
        "domestic_supply_or_capability": "C",
        "hard_regulatory_or_process_gate": "C",
    }
    return {
        field: {
            "field": field,
            "evidence_class": classes[field],
            "resolution_status": "RESOLVED",
        }
        for field in DECISION_CRITICAL_FIELDS
    }


def test_evidence_policy_13_advance_gate_is_directly_executable() -> None:
    policy = evidence_policy_config()

    assert policy["metadata"]["version"] == "1.3.0"
    assert policy["metadata"]["effective_date"] == "2026-09-02"
    assert policy["advance_gate"] == {
        "decision_critical_fields": list(DECISION_CRITICAL_FIELDS),
        "blocked_classes": ["D", "E"],
        "blocked_resolution_statuses": [
            "PARTIAL",
            "UNRESOLVED",
            "CONTRADICTORY",
            "MISSING",
        ],
        "confirmed_reviewer_status": (
            "confirmed_by_responsible_authority"
        ),
    }


def test_all_resolved_abc_assessments_pass_the_advance_gate() -> None:
    result = evaluate_advance_gate(
        _passing_assessments(),
        evidence_policy_config()["advance_gate"],
    )

    assert result == {
        "passes": True,
        "blocked_classes": ["D", "E"],
        "blocked_resolution_statuses": [
            "PARTIAL",
            "UNRESOLVED",
            "CONTRADICTORY",
            "MISSING",
        ],
        "blocked_fields": [],
    }


@pytest.mark.parametrize("field", DECISION_CRITICAL_FIELDS)
@pytest.mark.parametrize("evidence_class", ["D", "E"])
def test_each_single_field_d_or_e_blocks_the_advance_gate(
    field: str,
    evidence_class: str,
) -> None:
    assessments = _passing_assessments()
    assessments[field]["evidence_class"] = evidence_class

    result = evaluate_advance_gate(
        assessments,
        evidence_policy_config()["advance_gate"],
    )

    assert result["passes"] is False
    assert result["blocked_fields"] == [
        {
            "field": field,
            "evidence_class": evidence_class,
            "resolution_status": "RESOLVED",
            "reasons": ["BLOCKED_CLASS"],
        }
    ]


@pytest.mark.parametrize(
    "resolution",
    ["PARTIAL", "UNRESOLVED", "CONTRADICTORY", "MISSING"],
)
def test_each_configured_resolution_status_blocks_the_advance_gate(
    resolution: str,
) -> None:
    assessments = _passing_assessments()
    assessments["product_identity"]["resolution_status"] = resolution

    result = evaluate_advance_gate(
        assessments,
        evidence_policy_config()["advance_gate"],
    )

    assert result["passes"] is False
    assert result["blocked_fields"][0]["reasons"] == [
        "BLOCKED_RESOLUTION"
    ]


def test_advance_gate_fails_closed_on_malformed_policy() -> None:
    policy = deepcopy(evidence_policy_config()["advance_gate"])
    policy["decision_critical_fields"] = [
        *policy["decision_critical_fields"],
        "invented",
    ]

    with pytest.raises(EvidenceIntegrityError, match="decision_critical"):
        evaluate_advance_gate(_passing_assessments(), policy)


def test_advance_gate_ast_has_no_source_type_or_identity_predicate() -> None:
    path = PROJECT_ROOT / "src" / "ior_mvp" / "evidence.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "evaluate_advance_gate"
    )
    identifiers = {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name)
    } | {
        node.value
        for node in ast.walk(function)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    assert not {
        "source",
        "synthetic_flag",
        "producer",
        "opportunity_id",
        "scenario_id",
    } & identifiers


def test_changing_every_passport_source_leaves_full_decision_unchanged(
) -> None:
    import json

    path = (
        PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "public_decision"
        / "advance-route-3.json"
    )
    original = json.loads(path.read_text(encoding="utf-8"))
    changed = deepcopy(original)
    for index, passport in enumerate(changed["evidence"]):
        passport["source"] = f"CHANGED-{index}"

    def compute(case: dict) -> dict:
        capability = evaluate_capability(
            case["opportunity"]["sector_profile"],
            case["domestic_capability"]["public_dimension_states"],
            case["domestic_capability"]["profile_hard_gates"],
            capability_hard_gate_names(
                case["domestic_capability"]
            ),
        )
        return compute_public_decision(
            case,
            evaluate_rules(case),
            capability,
        )

    assert compute(changed) == compute(original)


def test_public_gate_selector_predicates_are_identity_independent() -> None:
    functions_by_file = {
        "public_decision.py": {
            "assess_decision_critical_fields",
            "classify_gap",
            "derive_rejection_conditions",
            "select_deep_state",
            "compute_public_decision",
        },
        "route_hypotheses.py": {
            "evaluate_route_hypotheses",
            "apply_precedence",
            "select_preferred_hypothesis",
        },
        "evidence_needs.py": {"derive_evidence_needs"},
        "signals.py": {
            "fired_signal_rule_ids",
            "material_trigger_rule_ids",
            "advance_supporting_signal_rule_ids",
        },
        "decision_engine.py": {"analyze_public"},
        "rules.py": {"_evaluate_rules_v2"},
        "trade_metrics.py": {
            "concentration_metrics",
            "degraded_dispersion_metrics",
            "domestic_flow_metrics",
            "established_domestic_nameplate",
        },
    }
    forbidden = {
        "synthetic_flag",
        "opportunity_id",
        "scenario_id",
        "SAU-H0-721049",
        "SAU-H0-390210",
        "WITS/UN Comtrade",
        "UNICOIL",
        "Hadeed",
        "SABIC",
        "Advanced Petrochemical",
        "Tasnee",
    }
    checked: set[str] = set()
    for filename, names in functions_by_file.items():
        path = PROJECT_ROOT / "src" / "ior_mvp" / filename
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }
        assert names <= set(functions), filename
        for name in names:
            checked.add(f"{filename}:{name}")
            predicates = [
                node
                for node in ast.walk(functions[name])
                if isinstance(
                    node,
                    (ast.If, ast.IfExp, ast.Compare),
                )
            ]
            predicate_strings = {
                nested.value
                for predicate in predicates
                for nested in ast.walk(predicate)
                if isinstance(nested, ast.Constant)
                and isinstance(nested.value, str)
            }
            assert not forbidden & predicate_strings, (
                filename,
                name,
                forbidden & predicate_strings,
            )
    assert len(checked) == sum(
        len(names) for names in functions_by_file.values()
    )
