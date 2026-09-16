from __future__ import annotations

import math
from typing import Any

from .config import evidence_policy_config
from .economics import minimum_effective_support
from .evidence import EvidenceIntegrityError, evaluate_advance_gate
from .narratives import (
    NarrativeValue,
    render_catalogue_entry,
)
from .route_hypotheses import (
    BROWNFIELD_ROUTE_CODE,
    evaluate_route_hypotheses,
    select_preferred_hypothesis,
)
from . import signals


class DecisionIntegrityError(EvidenceIntegrityError):
    """The evidence is valid but no lawful decision result exists."""


NO_CANDIDATE_REASON_CODE = "NO_TRIGGER_FIRED"


DECISION_REASON_CODES = frozenset(
    {
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
        NO_CANDIDATE_REASON_CODE,
    }
)

REJECTION_NARRATIVE_KEYS: dict[
    str,
    tuple[str, str | None, str, list[str], list[str]],
] = {
    "HARD_EXCLUSION_SATISFIED": (
        "decision.public.reject_exclusion.headline",
        None,
        "exclusion",
        ["decision.public.reject_exclusion.condition"],
        ["decision.public.reject_exclusion.kill"],
    ),
    "GENERIC_CAPACITY_CONTRADICTED": (
        "decision.public.reject_generic.headline",
        "decision.public.reject_generic.route",
        "decision.public.reject_generic.rationale",
        [
            "decision.public.reject_generic.condition.named_exception"
        ],
        [
            "decision.public.reject_generic.kill.equivalence",
            "decision.public.reject_generic.kill.no_gap",
        ],
    ),
    "EQUIVALENT_QUALIFIED_SUPPLY": (
        "decision.public.reject_equivalence.headline",
        None,
        "decision.public.reject_equivalence.rationale",
        ["decision.public.reject_equivalence.condition"],
        ["decision.public.reject_equivalence.kill"],
    ),
    "UNECONOMIC_AT_EFFICIENT_SCALE": (
        "decision.public.reject_uneconomic.headline",
        None,
        "decision.public.reject_uneconomic.rationale",
        ["decision.public.reject_uneconomic.condition"],
        ["decision.public.reject_uneconomic.kill"],
    ),
    "FALSE_OR_MEASUREMENT_GAP": (
        "decision.public.reject_false_gap.headline",
        None,
        "decision.public.reject_false_gap.rationale",
        ["decision.public.reject_false_gap.condition"],
        ["decision.public.reject_false_gap.kill"],
    ),
    "STRUCTURAL_OVERCAPACITY": (
        "decision.public.reject_overcapacity.headline",
        None,
        "decision.public.reject_overcapacity.rationale",
        ["decision.public.reject_overcapacity.condition"],
        ["decision.public.reject_overcapacity.kill"],
    ),
}
DECISION_CRITICAL_FIELDS = (
    "product_identity",
    "demand_at_required_specification",
    "domestic_supply_or_capability",
    "hard_regulatory_or_process_gate",
)
SUPPORT_CODES = frozenset(
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
FIELD_SUPPORT_CODES = {
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
_CLASS_ORDER = {
    evidence_class: index
    for index, evidence_class in enumerate(("A", "B", "C", "D", "E"))
}
_CONFIRMED_REVIEW = "confirmed_by_responsible_authority"


def _passport_supports(passport: dict[str, Any]) -> set[str]:
    raw = passport.get("supports")
    if not isinstance(raw, list) or not raw:
        raise EvidenceIntegrityError(
            "Evidence passport supports must be a non-empty list"
        )
    supports = set(raw)
    unknown = sorted(supports - SUPPORT_CODES)
    if unknown:
        raise EvidenceIntegrityError(
            "Evidence passport has unknown support code(s): "
            + ", ".join(unknown)
        )
    return supports


def _best_class(
    covering: list[dict[str, Any]],
    contradicted_ids: set[str],
) -> str:
    eligible = [
        passport
        for passport in covering
        if passport.get("evidence_id") not in contradicted_ids
    ]
    candidates = eligible or covering
    classes = [passport.get("evidence_class") for passport in candidates]
    if any(value not in _CLASS_ORDER for value in classes):
        raise EvidenceIntegrityError(
            "Covering evidence passport has an invalid evidence class"
        )
    return min(classes, key=_CLASS_ORDER.__getitem__)


def _target_demand_resolved(
    case: dict[str, Any],
    covering_ids: set[str],
) -> bool:
    decision_inputs = case.get("decision_inputs")
    target = (
        decision_inputs.get("target_specification_demand")
        if isinstance(decision_inputs, dict)
        else None
    )
    if not isinstance(target, dict):
        return False
    quantity = target.get("quantity_kt")
    references = target.get("evidence_ids")
    return (
        not isinstance(quantity, bool)
        and isinstance(quantity, (int, float))
        and math.isfinite(float(quantity))
        and quantity >= 0
        and isinstance(references, list)
        and bool(references)
        and set(references) <= covering_ids
    )


def _profile_gates_resolved(case: dict[str, Any]) -> bool:
    capability = case.get("domestic_capability")
    gates = (
        capability.get("profile_hard_gates")
        if isinstance(capability, dict)
        else None
    )
    if not isinstance(gates, dict) or not gates:
        return False
    return all(
        isinstance(item, dict)
        and item.get("status") == "RESOLVED"
        and isinstance(item.get("evidence_ids"), list)
        and bool(item["evidence_ids"])
        for item in gates.values()
    )


def _decision_gates_resolved(case: dict[str, Any]) -> bool:
    capability = case.get("domestic_capability")
    gates = (
        capability.get("unresolved_hard_gates")
        if isinstance(capability, dict)
        else None
    )
    return isinstance(gates, list) and not gates


def _field_completion_status(
    field: str,
    case: dict[str, Any],
    capability: dict[str, Any],
    evidence_class: str,
    covering_ids: set[str],
) -> str:
    if field == "product_identity":
        opportunity = case.get("opportunity")
        status = (
            opportunity.get("decision_object_status")
            if isinstance(opportunity, dict)
            else None
        )
        return "RESOLVED" if status == "resolved" else "PARTIAL"
    if field == "demand_at_required_specification":
        return (
            "RESOLVED"
            if _target_demand_resolved(case, covering_ids)
            else "PARTIAL"
        )
    if field == "domestic_supply_or_capability":
        return (
            "RESOLVED"
            if evidence_class in {"A", "B", "C"}
            and capability.get("route_publishable") is True
            else "UNRESOLVED"
        )
    return (
        "RESOLVED"
        if evidence_class in {"A", "B", "C"}
        and capability.get("route_publishable") is True
        and _profile_gates_resolved(case)
        and _decision_gates_resolved(case)
        else "UNRESOLVED"
    )


def assess_decision_critical_fields(
    case: dict[str, Any],
    capability: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    evidence = case.get("evidence")
    if not isinstance(evidence, list):
        raise EvidenceIntegrityError(
            "Public decision evidence must be a list"
        )
    support_sets = [
        _passport_supports(passport)
        if isinstance(passport, dict)
        else set()
        for passport in evidence
    ]
    assessments: dict[str, dict[str, Any]] = {}
    for field in DECISION_CRITICAL_FIELDS:
        allowed = FIELD_SUPPORT_CODES[field]
        covering = [
            passport
            for passport, supports in zip(
                evidence,
                support_sets,
                strict=True,
            )
            if isinstance(passport, dict) and supports & allowed
        ]
        if not covering:
            assessments[field] = {
                "field": field,
                "evidence_class": "E",
                "resolution_status": "MISSING",
                "support_codes": [],
                "evidence_ids": [],
                "contradiction_evidence_ids": [],
            }
            continue
        unconfirmed = {
            str(passport.get("evidence_id"))
            for passport in covering
            if passport.get("contradiction") is not None
            and passport.get("reviewer_status") != _CONFIRMED_REVIEW
        }
        contradictions = sorted(
            str(passport.get("evidence_id"))
            for passport in covering
            if passport.get("contradiction") is not None
        )
        evidence_class = _best_class(covering, unconfirmed)
        covering_ids = {
            str(passport.get("evidence_id"))
            for passport in covering
        }
        completion = _field_completion_status(
            field,
            case,
            capability,
            evidence_class,
            covering_ids,
        )
        if any(
            passport.get("status") == "unresolved"
            for passport in covering
        ) or completion == "UNRESOLVED":
            resolution = "UNRESOLVED"
        elif unconfirmed:
            resolution = "CONTRADICTORY"
        else:
            resolution = completion
        assessments[field] = {
            "field": field,
            "evidence_class": evidence_class,
            "resolution_status": resolution,
            "support_codes": sorted(
                {
                    code
                    for passport, supports in zip(
                        evidence,
                        support_sets,
                        strict=True,
                    )
                    if passport in covering
                    for code in supports & allowed
                }
            ),
            "evidence_ids": sorted(covering_ids),
            "contradiction_evidence_ids": contradictions,
        }
    return assessments


_EXCLUSION_SPECS = (
    (
        "EX-01_HETEROGENEOUS_RESIDUAL",
        "heterogeneous_residual_code",
        "exclusion.heterogeneous_residual",
    ),
    (
        "EX-02_MARKET_BELOW_MES",
        "downside_market_below_mes",
        "exclusion.market_below_mes",
    ),
    (
        "EX-03_UNSATISFIABLE_HARD_GATE",
        "unsatisfiable_hard_gate",
        "exclusion.unsatisfiable_gate",
    ),
    (
        "EX-04_IDLE_EQUIVALENT_CAPACITY",
        "idle_equivalent_domestic_capacity",
        "exclusion.idle_equivalent_capacity",
    ),
    (
        "EX-05_TRANSITORY_OR_MEASUREMENT",
        "transitory_or_measurement_gap",
        "exclusion.transitory_gap",
    ),
    (
        "EX-06_REDUNDANCY_OR_CROWD_OUT",
        "redundancy_or_crowd_out",
        "exclusion.redundancy",
    ),
)


def _known_number(value: Any) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        return None
    return float(value)


def _ex01(block: dict[str, Any]) -> str:
    separable = block.get("commercial_product_separable")
    product_evidence = block.get("product_level_evidence_available")
    if separable is True or product_evidence is True:
        return "NOT_SATISFIED"
    if separable is False and product_evidence is False:
        return "SATISFIED"
    return "NOT_CALCULABLE"


def _ex02(block: dict[str, Any]) -> str:
    demand = _known_number(
        block.get("sustainable_downside_demand_kt")
    )
    efficient_scale = _known_number(
        block.get("minimum_efficient_scale_kt")
    )
    export_contract = block.get("credible_export_contract")
    if export_contract is True:
        return "NOT_SATISFIED"
    if demand is not None and efficient_scale is not None:
        if demand >= efficient_scale:
            return "NOT_SATISFIED"
        if export_contract is False:
            return "SATISFIED"
    return "NOT_CALCULABLE"


def _ex03(block: dict[str, Any]) -> str:
    value = block.get("gate_satisfiability")
    if value == "UNSATISFIABLE":
        return "SATISFIED"
    if value == "SATISFIABLE":
        return "NOT_SATISFIED"
    return "NOT_CALCULABLE"


def _ex04(block: dict[str, Any]) -> str:
    equivalent = block.get("domestic_specification_equivalent")
    idle = _known_number(block.get("qualified_idle_capacity_kt"))
    demand = _known_number(
        block.get("target_specification_demand_kt")
    )
    market_failure = block.get("binding_market_failure")
    if (
        equivalent is False
        or market_failure is True
        or (
            idle is not None
            and demand is not None
            and idle < demand
        )
    ):
        return "NOT_SATISFIED"
    if (
        equivalent is True
        and idle is not None
        and demand is not None
        and idle >= demand
        and market_failure is False
    ):
        return "SATISFIED"
    return "NOT_CALCULABLE"


def _ex05(block: dict[str, Any]) -> str:
    cause = block.get("dominant_cause")
    if cause in {
        "REEXPORT",
        "ONE_OFF_PROJECT",
        "TEMPORARY_PRICE_ARBITRAGE",
        "CLASSIFICATION_DISCONTINUITY",
    }:
        return "SATISFIED"
    if cause == "OTHER":
        return "NOT_SATISFIED"
    return "NOT_CALCULABLE"


def _ex06(block: dict[str, Any]) -> str:
    finding = block.get("competition_finding")
    if finding in {
        "UNACCEPTABLE_REDUNDANT_CAPACITY",
        "UNACCEPTABLE_CROWD_OUT",
    }:
        return "SATISFIED"
    if finding == "ACCEPTABLE":
        return "NOT_SATISFIED"
    return "NOT_CALCULABLE"


_EXCLUSION_EVALUATORS = (
    _ex01,
    _ex02,
    _ex03,
    _ex04,
    _ex05,
    _ex06,
)


def evaluate_hard_exclusions(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    blocks = case.get("hard_exclusion_inputs")
    if not isinstance(blocks, dict):
        raise EvidenceIntegrityError(
            "hard_exclusion_inputs must be a mapping"
        )
    results: list[dict[str, Any]] = []
    for specification, evaluator in zip(
        _EXCLUSION_SPECS,
        _EXCLUSION_EVALUATORS,
        strict=True,
    ):
        code, block_name, narrative_key = specification
        block = blocks.get(block_name)
        if not isinstance(block, dict):
            raise EvidenceIntegrityError(
                f"hard_exclusion_inputs.{block_name} must be a mapping"
            )
        status = evaluator(block)
        evidence_ids = block.get("evidence_ids")
        if not isinstance(evidence_ids, list):
            raise EvidenceIntegrityError(
                f"hard_exclusion_inputs.{block_name}.evidence_ids "
                "must be a list"
            )
        localized = {
            locale: render_catalogue_entry(
                narrative_key,
                locale,
            )["text"]
            for locale in ("en", "ar")
        }
        results.append(
            {
                "code": code,
                "status": status,
                "reason_code": {
                    "SATISFIED": "EXCLUSION_SATISFIED",
                    "NOT_SATISFIED": "EXCLUSION_NOT_SATISFIED",
                    "NOT_CALCULABLE": "EXCLUSION_INPUT_UNAVAILABLE",
                }[status],
                "inputs": {
                    key: value
                    for key, value in block.items()
                    if key != "evidence_ids"
                },
                "evidence_ids": sorted(evidence_ids),
                "narrative": localized["en"],
                "localized_narrative": localized,
            }
        )
    return results


_GAP_ORDER = (
    "false_or_measurement",
    "quantity",
    "specification_or_quality",
    "application",
    "timing",
    "resilience",
)


def _require_one_primary(candidates: list[str]) -> str:
    if len(candidates) != 1:
        raise DecisionIntegrityError(
            "Gap taxonomy must select exactly one primary class"
        )
    return candidates[0]


def _rule_fired(
    rules: list[dict[str, Any]],
    rule_id: str,
) -> bool:
    return any(
        isinstance(row, dict)
        and row.get("rule_id") == rule_id
        and row.get("fired") is True
        for row in rules
    )


def _decision_input(
    case: dict[str, Any],
    key: str,
) -> Any:
    values = case.get("decision_inputs")
    return values.get(key) if isinstance(values, dict) else None


def _route_constraints(case: dict[str, Any]) -> set[str]:
    route_evidence = _decision_input(case, "route_evidence")
    if not isinstance(route_evidence, list):
        return set()
    return {
        item["binding_constraint"]
        for item in route_evidence
        if isinstance(item, dict)
        and isinstance(item.get("binding_constraint"), str)
    }


def _quantity_gap(case: dict[str, Any]) -> bool:
    target = _decision_input(
        case,
        "target_specification_demand",
    )
    equivalence = _decision_input(
        case,
        "specification_equivalence",
    )
    if not isinstance(target, dict) or not isinstance(equivalence, dict):
        return False
    demand = _known_number(target.get("quantity_kt"))
    availability = _known_number(
        equivalence.get("qualified_available_kt")
    )
    return bool(
        equivalence.get("domestic_product_equivalent") is True
        and demand is not None
        and availability is not None
        and demand > availability
    )


def _timing_gap(
    case: dict[str, Any],
    capability: dict[str, Any] | None = None,
) -> bool:
    if capability is not None:
        dimensions = capability.get("dimensions")
        if isinstance(dimensions, list):
            for row in dimensions:
                if (
                    isinstance(row, dict)
                    and (row.get("dimension") or row.get("identifier"))
                    == "capacity_time_window"
                    and isinstance(row.get("state"), int)
                    and not isinstance(row.get("state"), bool)
                    and row["state"] > 0
                ):
                    return True
    capability_block = case.get("domestic_capability")
    states = (
        capability_block.get("public_dimension_states")
        if isinstance(capability_block, dict)
        else None
    )
    state = (
        states.get("capacity_time_window")
        if isinstance(states, dict)
        else None
    )
    return (
        isinstance(state, int)
        and not isinstance(state, bool)
        and state > 0
    )


def classify_gap(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
    assessments: dict[str, dict[str, Any]],
    exclusions: list[dict[str, Any]],
    capability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    unresolved = any(
        assessment.get("resolution_status") != "RESOLVED"
        for assessment in assessments.values()
    )
    constraints = _route_constraints(case)
    equivalence = _decision_input(
        case,
        "specification_equivalence",
    )
    mismatch = (
        isinstance(equivalence, dict)
        and equivalence.get("domestic_product_equivalent") is False
    )
    candidates = {
        "false_or_measurement": (
            any(
                row.get("status") == "SATISFIED"
                for row in exclusions
                if isinstance(row, dict)
            )
            or _rule_fired(rules, "R11")
        ),
        "quantity": _quantity_gap(case),
        "specification_or_quality": (
            mismatch and "specification_or_grade" in constraints
        ),
        "application": (
            mismatch
            and "qualification_or_certification" in constraints
        ),
        "timing": _timing_gap(case, capability),
        "resilience": (
            _rule_fired(rules, "R3")
            or _rule_fired(rules, "R10")
        ),
    }
    business = [
        gap_class
        for gap_class in _GAP_ORDER
        if candidates[gap_class]
    ]
    if unresolved:
        primary = _require_one_primary(["evidence"])
        secondary = business
    elif business:
        primary = _require_one_primary([business[0]])
        secondary = business[1:]
    else:
        primary = _require_one_primary(["evidence"])
        secondary = []

    decision_status = (
        case.get("opportunity", {}).get("decision_object_status")
        if isinstance(case.get("opportunity"), dict)
        else None
    )
    demand_assessment = assessments.get(
        "demand_at_required_specification",
        {},
    )
    capability_assessment = assessments.get(
        "domestic_supply_or_capability",
        {},
    )
    reason_codes: list[str] = []
    if demand_assessment.get("resolution_status") != "RESOLVED":
        reason_codes.append("TARGET_SPECIFICATION_DEMAND_MISSING")
    if decision_status == "generic_hs6_only":
        reason_codes.append("TARGET_GRADE_UNRESOLVED")
    if (
        capability_assessment.get("resolution_status") != "RESOLVED"
        and decision_status != "generic_hs6_only"
    ):
        reason_codes.append("CAPABILITY_GATES_UNRESOLVED")
    if _rule_fired(rules, "R3"):
        reason_codes.append("SUPPLIER_CONCENTRATION_SIGNAL")
    if _rule_fired(rules, "R11"):
        reason_codes.append("GENERIC_CAPACITY_CONTRADICTED")

    if _rule_fired(rules, "R11"):
        constraint_class: str | None = "cost_or_competitiveness"
    elif (
        capability_assessment.get("resolution_status") != "RESOLVED"
        or primary in {"quantity", "timing"}
    ):
        constraint_class = "capacity_or_availability"
    elif primary == "specification_or_quality":
        constraint_class = "specification_or_grade"
    elif primary == "application":
        constraint_class = "qualification_or_certification"
    else:
        constraint_class = None
    localized = {
        locale: render_catalogue_entry(
            f"gap.{primary}",
            locale,
        )["text"]
        for locale in ("en", "ar")
    }
    return {
        "primary": primary,
        "secondary": secondary,
        "constraint_class": constraint_class,
        "reason_codes": reason_codes,
        "label": localized["en"],
        "localized_label": localized,
    }


_REJECTION_CODES = (
    "hard_exclusion",
    "false_or_measurement_gap",
    "equivalent_idle_qualified_supply",
    "uneconomic_at_efficient_scale",
    "structural_overcapacity",
    "generic_capacity_contradicted",
)
_MONITOR_DOMAINS = {
    "demand",
    "regulation",
    "technology",
    "supplier_concentration",
    "capacity_state",
}
_REJECTION_REASON_CODES = {
    "false_or_measurement_gap": "FALSE_OR_MEASUREMENT_GAP",
    "equivalent_idle_qualified_supply": (
        "EQUIVALENT_QUALIFIED_SUPPLY"
    ),
    "uneconomic_at_efficient_scale": (
        "UNECONOMIC_AT_EFFICIENT_SCALE"
    ),
    "structural_overcapacity": "STRUCTURAL_OVERCAPACITY",
    "generic_capacity_contradicted": "GENERIC_CAPACITY_CONTRADICTED",
}


def _aggregate_status(statuses: list[str]) -> str:
    if "SATISFIED" in statuses:
        return "SATISFIED"
    if statuses and all(
        status == "NOT_SATISFIED" for status in statuses
    ):
        return "NOT_SATISFIED"
    return "NOT_CALCULABLE"


def _rejection_row(
    code: str,
    status: str,
    reason_code: str,
    evidence_ids: list[str],
) -> dict[str, Any]:
    return {
        "code": code,
        "status": status,
        "reason_code": reason_code,
        "evidence_ids": sorted(set(evidence_ids)),
    }


def _equivalence_rejection(
    case: dict[str, Any],
) -> dict[str, Any]:
    target = _decision_input(
        case,
        "target_specification_demand",
    )
    equivalence = _decision_input(
        case,
        "specification_equivalence",
    )
    if not isinstance(target, dict) or not isinstance(equivalence, dict):
        return _rejection_row(
            "equivalent_idle_qualified_supply",
            "NOT_CALCULABLE",
            "EQUIVALENCE_INPUT_UNAVAILABLE",
            [],
        )
    demand = _known_number(target.get("quantity_kt"))
    available = _known_number(
        equivalence.get("qualified_available_kt")
    )
    equivalent = equivalence.get("domestic_product_equivalent")
    if (
        equivalent is True
        and demand is not None
        and available is not None
        and available >= demand
    ):
        status = "SATISFIED"
        reason = "EQUIVALENT_QUALIFIED_SUPPLY"
    elif (
        equivalent is False
        or (
            demand is not None
            and available is not None
            and available < demand
        )
    ):
        status = "NOT_SATISFIED"
        reason = "EQUIVALENT_QUALIFIED_SUPPLY_NOT_ESTABLISHED"
    else:
        status = "NOT_CALCULABLE"
        reason = "EQUIVALENCE_INPUT_UNAVAILABLE"
    evidence_ids = [
        evidence_id
        for block in (target, equivalence)
        for evidence_id in block.get("evidence_ids", [])
        if isinstance(evidence_id, str)
    ]
    return _rejection_row(
        "equivalent_idle_qualified_supply",
        status,
        reason,
        evidence_ids,
    )


def _generic_rejection(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    row = next(
        (
            item
            for item in rules
            if item.get("rule_id") == "R11"
        ),
        None,
    )
    if not isinstance(row, dict):
        raise DecisionIntegrityError(
            "R11 is required for public rejection conditions"
        )
    if row.get("fired") is True:
        status = "SATISFIED"
        reason = "GENERIC_CAPACITY_CONTRADICTED"
    elif row.get("fired") is False:
        status = "NOT_SATISFIED"
        reason = "GENERIC_CAPACITY_NOT_CONTRADICTED"
    else:
        status = "NOT_CALCULABLE"
        reason = "GENERIC_CAPACITY_INPUT_UNAVAILABLE"
    metrics = row.get("metrics")
    established = (
        metrics.get("established_nameplate")
        if isinstance(metrics, dict)
        else None
    )
    evidence_ids = (
        list(established.get("evidence_ids", []))
        if isinstance(established, dict)
        else []
    )
    evidence = case.get("evidence")
    if isinstance(evidence, list):
        evidence_ids.extend(
            str(passport.get("evidence_id"))
            for passport in evidence
            if isinstance(passport, dict)
            and isinstance(passport.get("supports"), list)
            and "EXPORT_IMPORT_RATIO" in passport["supports"]
        )
    return _rejection_row(
        "generic_capacity_contradicted",
        status,
        reason,
        evidence_ids,
    )


def _uneconomic_rejection(
    case: dict[str, Any],
) -> dict[str, Any]:
    route_evidence = _decision_input(case, "route_evidence")
    if not isinstance(route_evidence, list) or not route_evidence:
        return _rejection_row(
            "uneconomic_at_efficient_scale",
            "NOT_CALCULABLE",
            "EFFICIENT_SCALE_ECONOMICS_UNAVAILABLE",
            [],
        )
    results: list[bool] = []
    evidence_ids: list[str] = []
    for record in route_evidence:
        if (
            not isinstance(record, dict)
            or record.get("technical_feasibility_confirmed") is not True
        ):
            continue
        cash_flows = record.get("downside_cash_flows_m_sar")
        hurdle = _known_number(record.get("hurdle_rate"))
        if (
            not isinstance(cash_flows, list)
            or not cash_flows
            or hurdle is None
            or any(_known_number(value) is None for value in cash_flows)
        ):
            continue
        try:
            result = minimum_effective_support(
                [float(value) for value in cash_flows],
                hurdle,
            )
        except ValueError as exc:
            raise DecisionIntegrityError(
                "Route economics are invalid"
            ) from exc
        results.append(result["passes"] is True)
        evidence_ids.extend(
            item
            for item in record.get("evidence_ids", [])
            if isinstance(item, str)
        )
    if not results:
        status = "NOT_CALCULABLE"
        reason = "EFFICIENT_SCALE_ECONOMICS_UNAVAILABLE"
    elif any(results):
        status = "NOT_SATISFIED"
        reason = "ECONOMIC_ROUTE_EXISTS"
    else:
        status = "SATISFIED"
        reason = "UNECONOMIC_AT_EFFICIENT_SCALE"
    return _rejection_row(
        "uneconomic_at_efficient_scale",
        status,
        reason,
        evidence_ids,
    )


def derive_rejection_conditions(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_code = {
        row.get("code"): row
        for row in exclusions
        if isinstance(row, dict)
    }
    statuses = [
        str(row.get("status"))
        for row in exclusions
        if isinstance(row, dict)
    ]
    all_evidence = [
        evidence_id
        for row in exclusions
        if isinstance(row, dict)
        for evidence_id in row.get("evidence_ids", [])
        if isinstance(evidence_id, str)
    ]
    hard_status = _aggregate_status(statuses)
    false_status = _aggregate_status(
        [
            str(by_code.get(code, {}).get("status"))
            for code in (
                "EX-01_HETEROGENEOUS_RESIDUAL",
                "EX-05_TRANSITORY_OR_MEASUREMENT",
            )
        ]
    )
    structural_status = str(
        by_code.get(
            "EX-06_REDUNDANCY_OR_CROWD_OUT",
            {},
        ).get("status", "NOT_CALCULABLE")
    )
    return [
        _rejection_row(
            "hard_exclusion",
            hard_status,
            (
                "HARD_EXCLUSION_SATISFIED"
                if hard_status == "SATISFIED"
                else "HARD_EXCLUSION_NOT_SATISFIED"
            ),
            all_evidence,
        ),
        _rejection_row(
            "false_or_measurement_gap",
            false_status,
            (
                "FALSE_OR_MEASUREMENT_GAP"
                if false_status == "SATISFIED"
                else "FALSE_OR_MEASUREMENT_NOT_ESTABLISHED"
            ),
            all_evidence,
        ),
        _equivalence_rejection(case),
        _uneconomic_rejection(case),
        _rejection_row(
            "structural_overcapacity",
            structural_status,
            (
                "STRUCTURAL_OVERCAPACITY"
                if structural_status == "SATISFIED"
                else "STRUCTURAL_OVERCAPACITY_NOT_ESTABLISHED"
            ),
            list(
                by_code.get(
                    "EX-06_REDUNDANCY_OR_CROWD_OUT",
                    {},
                ).get("evidence_ids", [])
            ),
        ),
        _generic_rejection(case, rules),
    ]


def screen_candidate(
    *,
    has_candidate_trigger: bool,
    screen_exclusion_satisfied: bool,
) -> dict[str, Any]:
    if screen_exclusion_satisfied:
        disposition = "SCREENED_OUT"
    elif not has_candidate_trigger:
        disposition = "NO_CANDIDATE"
    else:
        disposition = "CANDIDATE"
    return {
        "screening_disposition": disposition,
        "state": None,
    }


def _named_monitor_trigger(
    case: dict[str, Any],
) -> dict[str, Any] | None:
    trigger = _decision_input(case, "monitor_trigger")
    if (
        not isinstance(trigger, dict)
        or trigger.get("domain") not in _MONITOR_DOMAINS
        or not isinstance(trigger.get("condition_code"), str)
        or not trigger["condition_code"]
        or not isinstance(trigger.get("evidence_ids"), list)
        or not trigger["evidence_ids"]
    ):
        return None
    return trigger


def _deep_state_result(
    *,
    state: str,
    route_code: int | None,
    decision_reason_code: str,
    monitor_trigger: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if decision_reason_code not in DECISION_REASON_CODES:
        raise DecisionIntegrityError(
            f"Unregistered decision reason code: {decision_reason_code}"
        )
    result: dict[str, Any] = {
        "state": state,
        "route_code": route_code,
        "screening_disposition": "CANDIDATE",
        "decision_reason_code": decision_reason_code,
    }
    if monitor_trigger is not None:
        result["monitor_trigger"] = monitor_trigger
    return result


def _no_candidate_result() -> dict[str, Any]:
    if NO_CANDIDATE_REASON_CODE not in DECISION_REASON_CODES:
        raise DecisionIntegrityError(
            f"Unregistered decision reason code: {NO_CANDIDATE_REASON_CODE}"
        )
    return {
        "state": None,
        "route_code": None,
        "screening_disposition": "NO_CANDIDATE",
        "decision_reason_code": NO_CANDIDATE_REASON_CODE,
    }


def select_deep_state(
    *,
    case: dict[str, Any],
    rules: list[dict[str, Any]],
    assessments: dict[str, dict[str, Any]],
    advance_gate: dict[str, Any],
    exclusions: list[dict[str, Any]],
    rejection_conditions: list[dict[str, Any]],
    selected_hypothesis: dict[str, Any] | None,
    preferred_hypothesis: dict[str, Any] | None,
    evidence_needs: list[dict[str, Any]],
    advance_support_signal_rule_ids: list[str],
) -> dict[str, Any]:
    del preferred_hypothesis
    if any(
        row.get("status") == "SATISFIED"
        for row in exclusions
    ):
        return _deep_state_result(
            state="REJECT",
            route_code=0,
            decision_reason_code="HARD_EXCLUSION_SATISFIED",
        )
    rejection = next(
        (
            row
            for row in rejection_conditions
            if row.get("status") == "SATISFIED"
            and row.get("code") != "hard_exclusion"
        ),
        None,
    )
    if rejection is not None:
        reason_code = str(
            rejection.get(
                "reason_code",
                _REJECTION_REASON_CODES.get(
                    str(rejection.get("code")),
                    "EVIDENCED_REJECTION",
                ),
            )
        )
        if reason_code not in REJECTION_NARRATIVE_KEYS:
            raise DecisionIntegrityError(
                f"Unregistered REJECT reason code: {reason_code}"
            )
        return _deep_state_result(
            state="REJECT",
            route_code=0,
            decision_reason_code=reason_code,
        )
    route_code = (
        selected_hypothesis.get("route_code")
        if isinstance(selected_hypothesis, dict)
        else None
    )
    route_ok = (
        isinstance(route_code, int)
        and route_code > 0
        and selected_hypothesis.get("status") == "passes"
    )
    gates_ok = (
        advance_gate.get("passes") is True
        and all(
            row.get("status") == "NOT_SATISFIED"
            for row in exclusions
        )
    )
    if route_ok and gates_ok and advance_support_signal_rule_ids:
        return _deep_state_result(
            state="ADVANCE",
            route_code=route_code,
            decision_reason_code="ALL_ADVANCE_GATES_PASS",
        )
    if route_ok and gates_ok and not advance_support_signal_rule_ids:
        return _deep_state_result(
            state="INVESTIGATE",
            route_code=None,
            decision_reason_code="ADVANCE_SUPPORT_SIGNAL_DEGRADED",
        )
    unresolved = any(
        assessment.get("resolution_status") != "RESOLVED"
        for assessment in assessments.values()
    ) or advance_gate.get("passes") is not True or any(
        row.get("status") == "NOT_CALCULABLE"
        for row in exclusions
    )
    positive_need = any(
        isinstance(row.get("route_effect"), str)
        and bool(row["route_effect"])
        for row in evidence_needs
    )
    if unresolved and positive_need:
        return _deep_state_result(
            state="INVESTIGATE",
            route_code=None,
            decision_reason_code=(
                "ROUTE_CHANGING_EVIDENCE_UNRESOLVED"
            ),
        )
    fired = signals.fired_signal_rule_ids(rules)
    material_triggers = signals.material_trigger_rule_ids(rules)
    if fired and not material_triggers:
        trigger = _named_monitor_trigger(case)
        if trigger is None:
            raise DecisionIntegrityError(
                "MONITOR requires a named allowed trigger"
            )
        return _deep_state_result(
            state="MONITOR",
            route_code=0,
            decision_reason_code="NAMED_TRIGGER_MONITOR",
            monitor_trigger=trigger,
        )
    if material_triggers and not route_ok:
        return _deep_state_result(
            state="INVESTIGATE",
            route_code=None,
            decision_reason_code="ROUTE_DETERMINATION_UNRESOLVED",
        )
    if not fired:
        return _no_candidate_result()
    raise DecisionIntegrityError(
        "Admitted deep case has no legal branch"
    )


def _literal_entry(text: str) -> dict[str, Any]:
    return {
        "text": text,
        "segments": [{"kind": "literal", "text": text}],
    }


def _route_priority_entry(
    route_code: int,
    locale: str,
) -> dict[str, Any]:
    short = render_catalogue_entry(
        f"route.{route_code}.short",
        locale,
    )["text"]
    return render_catalogue_entry(
        "route.hypothesis.priority",
        locale,
        {
            "route_short_label": NarrativeValue.localized(short)
        },
    )


def _public_product_name(
    case: dict[str, Any],
    locale: str,
) -> str:
    opportunity = case.get("opportunity")
    if not isinstance(opportunity, dict):
        raise DecisionIntegrityError(
            "Public decision opportunity is missing"
        )
    if locale == "ar":
        value = opportunity.get("commercial_name_ar")
    else:
        name = opportunity.get("commercial_name_en")
        value = (
            name.split(",", maxsplit=1)[0].strip().casefold()
            if isinstance(name, str)
            else None
        )
    if not isinstance(value, str) or not value:
        raise DecisionIntegrityError(
            "Public decision localized product name is missing"
        )
    return value


def _monitor_trigger_entry(
    trigger: dict[str, Any],
    locale: str,
) -> dict[str, Any]:
    domain = trigger.get("domain")
    if domain not in _MONITOR_DOMAINS:
        raise DecisionIntegrityError(
            "MONITOR trigger domain is invalid"
        )
    trigger_text = render_catalogue_entry(
        f"monitor.trigger.{domain}",
        locale,
    )["text"]
    return render_catalogue_entry(
        "decision.public.monitor.condition",
        locale,
        {"trigger": NarrativeValue.localized(trigger_text)},
    )


def _decision_narrative_keys(
    state_result: dict[str, Any],
    preferred: dict[str, Any] | None,
) -> tuple[str, str | None, str]:
    state = state_result["state"]
    reason = state_result["decision_reason_code"]
    if (
        state is None
        and state_result.get("screening_disposition") == "NO_CANDIDATE"
        and reason == NO_CANDIDATE_REASON_CODE
    ):
        return (
            "decision.public.no_candidate.headline",
            "decision.public.no_candidate.route",
            "decision.public.no_candidate.rationale",
        )
    if state == "INVESTIGATE":
        if preferred is None or preferred.get("route_code") == 0:
            return (
                "decision.public.investigate.headline",
                "decision.public.investigate.route.unresolved",
                "decision.public.investigate.rationale.route_unresolved",
            )
        if (
            preferred.get("selection_basis")
            == "EVIDENCE_PRIORITY_WITH_ECONOMICS_UNAVAILABLE"
            and preferred.get("route_code") == BROWNFIELD_ROUTE_CODE
        ):
            return (
                "decision.public.investigate.headline",
                None,
                "decision.public.investigate.rationale",
            )
        return (
            "decision.public.investigate.headline",
            None,
            "decision.public.investigate.rationale.preferred",
        )
    if state == "ADVANCE":
        return (
            "decision.public.advance.headline",
            None,
            "decision.public.advance.rationale",
        )
    if state == "MONITOR":
        return (
            "decision.public.monitor.headline",
            "decision.public.monitor.route",
            "decision.public.monitor.rationale",
        )
    if state == "REJECT":
        if reason not in REJECTION_NARRATIVE_KEYS:
            raise DecisionIntegrityError(
                f"Unregistered REJECT reason code: {reason}"
            )
        headline_key, route_key, rationale_key, _, _ = (
            REJECTION_NARRATIVE_KEYS[reason]
        )
        return headline_key, route_key, rationale_key
    raise DecisionIntegrityError(
        f"Unregistered decision state: {state}"
    )


def _condition_keys(
    state_result: dict[str, Any],
) -> tuple[list[str], list[str]]:
    state = state_result["state"]
    reason = state_result["decision_reason_code"]
    if (
        state is None
        and state_result.get("screening_disposition") == "NO_CANDIDATE"
        and reason == NO_CANDIDATE_REASON_CODE
    ):
        return (["decision.public.no_candidate.condition"], [])
    if state == "INVESTIGATE":
        return (
            [
                "decision.public.investigate.condition.no_greenfield"
            ],
            [
                "decision.public.investigate.kill.transitory",
                (
                    "decision.public.investigate."
                    "kill.incumbent_expansion"
                ),
            ],
        )
    if state == "ADVANCE":
        return (
            ["decision.public.advance.condition"],
            ["decision.public.advance.kill"],
        )
    if state == "MONITOR":
        return ([], [])
    if state == "REJECT":
        if reason not in REJECTION_NARRATIVE_KEYS:
            raise DecisionIntegrityError(
                f"Unregistered REJECT reason code: {reason}"
            )
        _, _, _, condition_keys, kill_keys = (
            REJECTION_NARRATIVE_KEYS[reason]
        )
        return condition_keys, kill_keys
    raise DecisionIntegrityError(
        f"Unregistered decision state: {state}"
    )


def _render_public_narrative(
    case: dict[str, Any],
    state_result: dict[str, Any],
    preferred: dict[str, Any] | None,
    exclusions: list[dict[str, Any]],
    evidence_needs: list[dict[str, Any]],
) -> dict[str, Any]:
    headline_key, route_key, rationale_key = (
        _decision_narrative_keys(state_result, preferred)
    )
    condition_keys, kill_keys = _condition_keys(state_result)
    localized: dict[str, dict[str, Any]] = {}
    for locale in ("en", "ar"):
        state = state_result["state"]
        if state == "ADVANCE":
            route_code = state_result["route_code"]
            headline = render_catalogue_entry(
                headline_key,
                locale,
                {
                    "route_code": NarrativeValue.computed(
                        route_code
                    )
                },
            )
            route_label = render_catalogue_entry(
                f"route.{route_code}.label",
                locale,
            )
        else:
            headline = render_catalogue_entry(
                headline_key,
                locale,
            )
            if route_key is not None:
                route_label = render_catalogue_entry(
                    route_key,
                    locale,
                )
            elif state == "INVESTIGATE" and preferred is not None:
                preferred_route = preferred.get("route_code")
                if not isinstance(preferred_route, int):
                    raise DecisionIntegrityError(
                        "No governed route label for state INVESTIGATE"
                    )
                route_label = _route_priority_entry(
                    preferred_route,
                    locale,
                )
            elif state == "REJECT":
                route_label = render_catalogue_entry(
                    "route.0.label",
                    locale,
                )
            else:
                raise DecisionIntegrityError(
                    f"No governed route label for state {state}"
                )

        if rationale_key == "exclusion":
            satisfied = next(
                (
                    row
                    for row in exclusions
                    if row.get("status") == "SATISFIED"
                ),
                None,
            )
            if satisfied is None:
                raise DecisionIntegrityError(
                    "Exclusion rejection has no satisfied exclusion"
                )
            rationale = _literal_entry(
                satisfied["localized_narrative"][locale]
            )
        elif rationale_key == (
            "decision.public.reject_generic.rationale"
        ):
            rationale = render_catalogue_entry(
                rationale_key,
                locale,
                {
                    "product_name": NarrativeValue.localized(
                        _public_product_name(case, locale)
                    )
                },
            )
        elif rationale_key == (
            "decision.public.investigate.rationale.preferred"
        ):
            preferred_route = preferred.get("route_code") if isinstance(
                preferred, dict
            ) else None
            if not isinstance(preferred_route, int):
                raise DecisionIntegrityError(
                    "Preferred INVESTIGATE rationale requires a route"
                )
            short = render_catalogue_entry(
                f"route.{preferred_route}.short",
                locale,
            )["text"]
            rationale = render_catalogue_entry(
                rationale_key,
                locale,
                {
                    "route_short_label": NarrativeValue.localized(
                        short
                    )
                },
            )
        else:
            rationale = render_catalogue_entry(
                rationale_key,
                locale,
            )
        conditions = [
            render_catalogue_entry(key, locale)
            for key in condition_keys
        ]
        if state == "MONITOR":
            trigger = state_result.get("monitor_trigger")
            if not isinstance(trigger, dict):
                raise DecisionIntegrityError(
                    "MONITOR narrative requires its trigger"
                )
            conditions = [
                _monitor_trigger_entry(trigger, locale)
            ]
        kills = [
            render_catalogue_entry(key, locale)
            for key in kill_keys
        ]
        missing = [
            need["localized_narrative"][locale]
            for need in evidence_needs
        ]
        localized[locale] = {
            "headline": headline,
            "route_label": route_label,
            "rationale": rationale,
            "conditions": conditions,
            "kill_conditions": kills,
            "missing_facts": missing,
        }
    english = localized["en"]
    return {
        "headline": english["headline"]["text"],
        "route_label": english["route_label"]["text"],
        "rationale": english["rationale"]["text"],
        "conditions": [
            item["text"] for item in english["conditions"]
        ],
        "kill_conditions": [
            item["text"] for item in english["kill_conditions"]
        ],
        "missing_facts": [
            item["text"] for item in english["missing_facts"]
        ],
        "localized_missing_facts": {
            locale: [
                item["text"]
                for item in localized[locale]["missing_facts"]
            ]
            for locale in ("en", "ar")
        },
        "narrative_version": "1.0.0",
        "localized_narrative": localized,
    }


def _decision_confidence(
    assessments: dict[str, dict[str, Any]],
    rules: list[dict[str, Any]],
) -> str:
    order = {"A": 0, "B": 1, "C": 2}
    supported = [
        assessment.get("evidence_class")
        for assessment in assessments.values()
        if assessment.get("evidence_class") in order
    ]
    base = (
        max(supported, key=order.__getitem__)
        if supported
        else "E"
    )
    caps: list[str] = []
    for row in rules:
        if row.get("fired") is not True:
            continue
        metrics = row.get("metrics")
        if not isinstance(metrics, dict):
            continue
        cap = metrics.get("confidence_cap")
        if cap is None:
            continue
        if cap not in order:
            raise DecisionIntegrityError(
                f"Fired rule confidence cap is invalid: {cap}"
            )
        caps.append(str(cap))
    if not caps:
        return base
    return max([base, *caps], key=order.__getitem__)


def compute_public_decision(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
    capability: dict[str, Any],
    *,
    shared_enabler: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assessments = assess_decision_critical_fields(
        case,
        capability,
    )
    advance = evaluate_advance_gate(
        assessments,
        evidence_policy_config()["advance_gate"],
    )
    exclusions = evaluate_hard_exclusions(case)
    gap = classify_gap(
        case,
        rules,
        assessments,
        exclusions,
        capability,
    )
    rejections = derive_rejection_conditions(
        case,
        rules,
        exclusions,
    )
    hypotheses = evaluate_route_hypotheses(
        case,
        rules,
        capability,
        gap,
        rejections,
        shared_enabler=shared_enabler,
    )
    preferred = select_preferred_hypothesis(hypotheses)
    selected = None
    if preferred is not None and preferred["selection_basis"] in {
        "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE",
        "EVIDENCED_NO_INTERVENTION",
        "MONITOR_NO_IMMEDIATE_ACTION",
    }:
        selected = next(
            row
            for row in hypotheses
            if row["route_code"] == preferred["route_code"]
        )
    r12 = next(
        (
            row
            for row in rules
            if row.get("rule_id") == "R12"
        ),
        None,
    )
    metrics = r12.get("metrics") if isinstance(r12, dict) else None
    evidence_needs = (
        metrics.get("evidence_needs")
        if isinstance(metrics, dict)
        else None
    )
    if not isinstance(evidence_needs, list):
        raise DecisionIntegrityError(
            "R12 evidence needs are missing"
        )
    support = signals.advance_supporting_signal_rule_ids(rules)
    state_result = select_deep_state(
        case=case,
        rules=rules,
        assessments=assessments,
        advance_gate=advance,
        exclusions=exclusions,
        rejection_conditions=rejections,
        selected_hypothesis=selected,
        preferred_hypothesis=preferred,
        evidence_needs=evidence_needs,
        advance_support_signal_rule_ids=support,
    )
    narrative = _render_public_narrative(
        case,
        state_result,
        preferred,
        exclusions,
        evidence_needs,
    )
    return {
        "state": state_result["state"],
        "route_code": state_result["route_code"],
        "screening_disposition": state_result[
            "screening_disposition"
        ],
        "decision_reason_code": state_result[
            "decision_reason_code"
        ],
        "advance_support_signal_rule_ids": support,
        **narrative,
        "confidence": _decision_confidence(assessments, rules),
        "synthetic_flag": False,
        "gap_class": gap,
        "route_hypotheses": hypotheses,
        "preferred_hypothesis": preferred,
        "evidence_class_assessment": assessments,
        "advance_gate": advance,
        "hard_exclusions": exclusions,
        "rejection_conditions": rejections,
    }
