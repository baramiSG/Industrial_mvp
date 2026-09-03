from __future__ import annotations

import math
from copy import deepcopy
from typing import Any

from .config import thresholds_config
from .economics import (
    NATIONAL_VALUE_KEYS,
    incremental_national_value,
    minimum_effective_support,
)
from .evidence import EvidenceIntegrityError
from .narratives import render_catalogue_entry
from . import signals


NOT_CALCULABLE = "NOT_CALCULABLE"
BROWNFIELD_ROUTE_CODE = 5
ROUTE_KEYS = {
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
ROUTE_CONSTRAINTS = {
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
_REASON_KEYS = {
    "INPUT_UNAVAILABLE": "route.reason.input_unavailable",
    "LOWER_ROUTE_FULLY_RESOLVES": (
        "route.reason.lower_route_resolves"
    ),
    "ECONOMICS_UNAVAILABLE": "route.reason.economics_unavailable",
    "ECONOMICS_FAILED": "route.reason.economics_failed",
    "NATIONAL_VALUE_NONPOSITIVE": (
        "route.reason.national_value_nonpositive"
    ),
    "COMPETITION_FAILED": "route.reason.competition_failed",
    "ADDITIONALITY_FAILED": "route.reason.additionality_failed",
    "POLICY_FAILED": "route.reason.policy_failed",
    "MAX_NV_SELECTED": "route.reason.max_nv_selected",
}


def _known_number(value: Any) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        return None
    return float(value)


def _localized(key: str) -> dict[str, str]:
    return {
        locale: render_catalogue_entry(key, locale)["text"]
        for locale in ("en", "ar")
    }


def _reason_key(reason_code: str, route_code: int) -> str | None:
    if reason_code in _REASON_KEYS:
        return _REASON_KEYS[reason_code]
    if reason_code in {
        "ROUTE_EVIDENCE_REQUIRED",
        "INCUMBENT_ADJACENCY_PRIORITY",
        "GRAPH_REQUIRED",
        "BINDING_CONSTRAINT_NOT_APPLICABLE",
        "ROUTE_7_CAPABILITY_BAND_FAILED",
        "ROUTE_7_MES_FAILED",
        "LOWER_NONFINANCIAL_ROUTES_UNRESOLVED",
        "LOWER_ROUTES_UNRESOLVED",
        "ROUTE_0_GAP_REQUIRES_ACTION",
    }:
        return f"route.{route_code}.reason"
    return None


def _reason_payload(
    reason_codes: list[str],
    route_code: int,
) -> tuple[list[str], dict[str, list[str]]]:
    localized = {"en": [], "ar": []}
    for reason_code in reason_codes:
        key = _reason_key(reason_code, route_code)
        if key is None:
            continue
        values = _localized(key)
        for locale in localized:
            if values[locale] not in localized[locale]:
                localized[locale].append(values[locale])
    return localized["en"], localized


def _empty_economics() -> dict[str, Any]:
    return {
        "unsupported_npv_m": NOT_CALCULABLE,
        "unsupported_irr": NOT_CALCULABLE,
        "minimum_effective_support_m": NOT_CALCULABLE,
    }


def _base_route(route_code: int) -> dict[str, Any]:
    return {
        "route_code": route_code,
        "route_key": ROUTE_KEYS[route_code],
        "status": NOT_CALCULABLE,
        "feasibility": NOT_CALCULABLE,
        "resolves_binding_constraint": NOT_CALCULABLE,
        "additionality": NOT_CALCULABLE,
        "policy_permissibility": NOT_CALCULABLE,
        "economics": _empty_economics(),
        "incremental_national_value_m_sar": NOT_CALCULABLE,
        "unrounded_incremental_national_value_m_sar": NOT_CALCULABLE,
        "competition": NOT_CALCULABLE,
        "precedence": {"blocked_by_lower_route": None},
        "reason_codes": [],
        "reasons": [],
        "localized_reasons": {"en": [], "ar": []},
        "evidence_ids": [],
    }


def _component(value: Any, *, inverse: bool = False) -> str:
    if not isinstance(value, bool):
        return NOT_CALCULABLE
    passed = not value if inverse else value
    return "passes" if passed else "fails"


def _route_evidence(
    case: dict[str, Any],
) -> dict[int, dict[str, Any]]:
    decision_inputs = case.get("decision_inputs")
    values = (
        decision_inputs.get("route_evidence")
        if isinstance(decision_inputs, dict)
        else None
    )
    if values == "UNAVAILABLE" or values is None:
        return {}
    if not isinstance(values, list):
        raise EvidenceIntegrityError(
            "decision_inputs.route_evidence must be a list or UNAVAILABLE"
        )
    indexed: dict[int, dict[str, Any]] = {}
    for record in values:
        if not isinstance(record, dict):
            raise EvidenceIntegrityError(
                "route evidence record must be a mapping"
            )
        route_code = record.get("route_code")
        if route_code == 8:
            raise EvidenceIntegrityError(
                "snapshot route 8 evidence is forbidden"
            )
        if (
            isinstance(route_code, bool)
            or not isinstance(route_code, int)
            or route_code not in ROUTE_CONSTRAINTS
            or route_code in indexed
        ):
            raise EvidenceIntegrityError(
                "route evidence route_code must be a unique value 1 through 7"
            )
        indexed[route_code] = record
    return indexed


def _route_zero(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
    rejections: list[dict[str, Any]],
    gap_class: dict[str, Any],
) -> dict[str, Any]:
    route = _base_route(0)
    rejected = any(
        row.get("status") == "SATISFIED"
        for row in rejections
    )
    decision_inputs = case.get("decision_inputs")
    trigger = (
        decision_inputs.get("monitor_trigger")
        if isinstance(decision_inputs, dict)
        else None
    )
    fired = signals.fired_signal_rule_ids(rules)
    material = signals.material_trigger_rule_ids(rules)
    monitor = (
        isinstance(trigger, dict)
        and bool(fired)
        and not material
    )
    if rejected or monitor:
        route.update(
            {
                "status": "passes",
                "feasibility": "passes",
                "resolves_binding_constraint": "passes",
                "additionality": "passes",
                "policy_permissibility": "passes",
                "incremental_national_value_m_sar": 0.0,
                "unrounded_incremental_national_value_m_sar": 0.0,
                "competition": "passes",
                "reason_codes": [
                    (
                        "EVIDENCED_NO_INTERVENTION"
                        if rejected
                        else "MONITOR_NO_IMMEDIATE_ACTION"
                    )
                ],
            }
        )
        key = "route.0.reason" if rejected else "route.0.reason.monitor"
        localized = _localized(key)
        route["reasons"] = [localized["en"]]
        route["localized_reasons"] = {
            locale: [localized[locale]]
            for locale in localized
        }
    elif gap_class.get("primary") != "evidence":
        route.update(
            {
                "status": "fails",
                "feasibility": "passes",
                "resolves_binding_constraint": "fails",
                "additionality": "passes",
                "policy_permissibility": "passes",
                "competition": "passes",
                "reason_codes": ["ROUTE_0_GAP_REQUIRES_ACTION"],
            }
        )
        route["reasons"], route[
            "localized_reasons"
        ] = _reason_payload(route["reason_codes"], 0)
    else:
        route["reason_codes"] = ["ROUTE_EVIDENCE_REQUIRED"]
        route["reasons"], route["localized_reasons"] = _reason_payload(
            route["reason_codes"],
            0,
        )
    return route


def _national_value(
    values: Any,
) -> tuple[dict[str, Any] | None, float | None]:
    if not isinstance(values, dict):
        return None, None
    if set(NATIONAL_VALUE_KEYS) - set(values):
        return None, None
    numbers = {
        key: _known_number(values.get(key))
        for key in NATIONAL_VALUE_KEYS
    }
    if any(value is None for value in numbers.values()):
        return None, None
    checked = {
        key: float(value)
        for key, value in numbers.items()
        if value is not None
    }
    result = incremental_national_value(checked)
    raw = (
        checked["domestic_value_added"]
        + checked["exports"]
        + checked["resilience_value"]
        + checked["knowledge_skills"]
        + checked["fiscal_receipts"]
        - checked["government_cost"]
        - checked["displacement"]
        - checked["resource_environment"]
        - checked["risk_allowance"]
    )
    return result, raw


def _economics(
    record: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    raw_flows = record.get("downside_cash_flows_m_sar")
    hurdle = _known_number(record.get("hurdle_rate"))
    if (
        not isinstance(raw_flows, list)
        or not raw_flows
        or hurdle is None
    ):
        return _empty_economics(), NOT_CALCULABLE
    cash_flows = [_known_number(value) for value in raw_flows]
    if any(value is None for value in cash_flows):
        return _empty_economics(), NOT_CALCULABLE
    try:
        result = minimum_effective_support(
            [float(value) for value in cash_flows if value is not None],
            hurdle,
        )
    except ValueError as exc:
        raise EvidenceIntegrityError(
            "route evidence economics are invalid"
        ) from exc
    projected = {
        "unsupported_npv_m": result["unsupported_npv_m"],
        "unsupported_irr": result["unsupported_irr"],
        "minimum_effective_support_m": result[
            "minimum_effective_support_m"
        ],
    }
    return projected, (
        "passes" if result["passes"] else "fails"
    )


def _competition(
    values: Any,
) -> tuple[dict[str, Any] | str, str]:
    if not isinstance(values, dict):
        return NOT_CALCULABLE, NOT_CALCULABLE
    existing = _known_number(
        values.get("existing_effective_capacity_kt")
    )
    proposed = _known_number(
        values.get("proposed_incremental_capacity_kt")
    )
    demand = _known_number(values.get("downside_demand_kt"))
    if (
        existing is None
        or proposed is None
        or demand is None
        or demand <= 0
    ):
        return NOT_CALCULABLE, NOT_CALCULABLE
    ratio = (existing + proposed) / demand
    warning = float(
        thresholds_config()["competition"][
            "post_entry_capacity_to_downside_demand_warning"
        ]
    )
    passed = ratio <= warning
    return {
        "capacity_ratio": round(ratio, 4),
        "warning_threshold": warning,
        "passes": passed,
    }, ("passes" if passed else "fails")


def _evaluate_record(
    route_code: int,
    record: dict[str, Any],
) -> dict[str, Any]:
    route = _base_route(route_code)
    constraint = record.get("binding_constraint")
    if constraint not in ROUTE_CONSTRAINTS[route_code]:
        reason_codes = ["BINDING_CONSTRAINT_NOT_APPLICABLE"]
        route.update(
            {
                "status": "fails",
                "reason_codes": reason_codes,
                "evidence_ids": sorted(
                    record.get("evidence_ids", [])
                ),
            }
        )
        route["reasons"], route["localized_reasons"] = _reason_payload(
            reason_codes,
            route_code,
        )
        return route
    feasibility = _component(
        record.get("technical_feasibility_confirmed")
    )
    resolution = _component(
        record.get("binding_constraint_fully_removed")
    )
    approved = _component(
        record.get("investment_already_approved_or_financed"),
        inverse=True,
    )
    proceeds = _component(
        record.get("proceeds_without_intervention"),
        inverse=True,
    )
    additionality = (
        "fails"
        if "fails" in {approved, proceeds}
        else (
            "passes"
            if approved == proceeds == "passes"
            else NOT_CALCULABLE
        )
    )
    prohibition = _component(
        record.get("policy_prohibition_identified"),
        inverse=True,
    )
    distortion = _component(
        record.get("distortion_unacceptable"),
        inverse=True,
    )
    proportionality = _component(
        record.get("intervention_proportionate_to_constraint")
    )
    policy_values = {
        prohibition,
        distortion,
        proportionality,
    }
    policy = (
        "fails"
        if "fails" in policy_values
        else (
            "passes"
            if policy_values == {"passes"}
            else NOT_CALCULABLE
        )
    )
    economics, economics_status = _economics(record)
    national_value, raw_value = _national_value(
        record.get("national_value")
    )
    if national_value is None or raw_value is None:
        national_status = NOT_CALCULABLE
        displayed_value: float | str = NOT_CALCULABLE
        raw_display: float | str = NOT_CALCULABLE
    else:
        national_status = (
            "passes" if national_value["positive"] else "fails"
        )
        displayed_value = national_value[
            "incremental_national_value_m_sar"
        ]
        raw_display = raw_value
    competition, competition_status = _competition(
        record.get("competition")
    )
    components = {
        feasibility,
        resolution,
        additionality,
        policy,
        economics_status,
        national_status,
        competition_status,
    }
    if "fails" in components:
        status = "fails"
    elif components == {"passes"}:
        status = "passes"
    else:
        status = NOT_CALCULABLE
    reason_codes: list[str] = []
    if feasibility == NOT_CALCULABLE or resolution == NOT_CALCULABLE:
        reason_codes.append("INPUT_UNAVAILABLE")
    if additionality == "fails":
        reason_codes.append("ADDITIONALITY_FAILED")
    if policy == "fails":
        reason_codes.append("POLICY_FAILED")
    if economics_status == NOT_CALCULABLE:
        reason_codes.append("ECONOMICS_UNAVAILABLE")
    elif economics_status == "fails":
        reason_codes.append("ECONOMICS_FAILED")
    if national_status == "fails":
        reason_codes.append("NATIONAL_VALUE_NONPOSITIVE")
    if competition_status == "fails":
        reason_codes.append("COMPETITION_FAILED")
    route.update(
        {
            "status": status,
            "feasibility": feasibility,
            "resolves_binding_constraint": resolution,
            "additionality": additionality,
            "policy_permissibility": policy,
            "economics": economics,
            "incremental_national_value_m_sar": displayed_value,
            "unrounded_incremental_national_value_m_sar": raw_display,
            "competition": competition,
            "reason_codes": reason_codes,
            "evidence_ids": sorted(record.get("evidence_ids", [])),
        }
    )
    route["reasons"], route["localized_reasons"] = _reason_payload(
        reason_codes,
        route_code,
    )
    return route


def _route_seven_gates(
    route: dict[str, Any],
    case: dict[str, Any],
    capability: dict[str, Any],
) -> None:
    if route["status"] != "passes":
        return
    bands = thresholds_config()["capability"]["route_bands"]
    distance = _known_number(capability.get("d_star"))
    maximum = float(bands["major_line_or_jv_max"])
    if distance is None or distance <= maximum:
        route["status"] = "fails"
        route["reason_codes"].append(
            "ROUTE_7_CAPABILITY_BAND_FAILED"
        )
    exclusion_inputs = case.get("hard_exclusion_inputs")
    market = (
        exclusion_inputs.get("downside_market_below_mes")
        if isinstance(exclusion_inputs, dict)
        else None
    )
    target = (
        case.get("decision_inputs", {}).get(
            "target_specification_demand"
        )
        if isinstance(case.get("decision_inputs"), dict)
        else None
    )
    demand = (
        _known_number(target.get("downside_quantity_kt"))
        if isinstance(target, dict)
        else None
    )
    efficient_scale = (
        _known_number(market.get("minimum_efficient_scale_kt"))
        if isinstance(market, dict)
        else None
    )
    if (
        demand is None
        or efficient_scale is None
        or demand < efficient_scale
    ):
        route["status"] = "fails"
        route["reason_codes"].append("ROUTE_7_MES_FAILED")
    route["reasons"], route["localized_reasons"] = _reason_payload(
        route["reason_codes"],
        7,
    )


def apply_precedence(
    hypotheses: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    routes = sorted(
        (deepcopy(route) for route in hypotheses),
        key=lambda route: route["route_code"],
    )
    for route in routes:
        route_code = route["route_code"]
        if route_code in {0, 8}:
            continue
        blocker = next(
            (
                lower
                for lower in routes
                if lower["route_code"] < route_code
                and lower.get("status") == "passes"
                and lower.get("resolves_binding_constraint") == "passes"
            ),
            None,
        )
        if blocker is None:
            continue
        route["status"] = "fails"
        route.setdefault("precedence", {})[
            "blocked_by_lower_route"
        ] = blocker["route_code"]
        codes = route.setdefault("reason_codes", [])
        if "LOWER_ROUTE_FULLY_RESOLVES" not in codes:
            codes.append("LOWER_ROUTE_FULLY_RESOLVES")
        route["reasons"], route["localized_reasons"] = _reason_payload(
            codes,
            route_code,
        )
    return routes


def evaluate_route_hypotheses(
    case: dict[str, Any],
    rules: list[dict[str, Any]],
    capability: dict[str, Any],
    gap_class: dict[str, Any],
    rejection_conditions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence = _route_evidence(case)
    hypotheses = [
        _route_zero(
            case,
            rules,
            rejection_conditions,
            gap_class,
        )
    ]
    for route_code in range(1, 8):
        if route_code in evidence:
            route = _evaluate_record(
                route_code,
                evidence[route_code],
            )
        else:
            route = _base_route(route_code)
            route["reason_codes"] = ["ROUTE_EVIDENCE_REQUIRED"]
            if (
                route_code == BROWNFIELD_ROUTE_CODE
                and any(
                    row.get("rule_id") == "R9-S"
                    and row.get("fired") is True
                    for row in rules
                )
                and gap_class.get("constraint_class")
                == "capacity_or_availability"
            ):
                route["priority"] = True
                route["reason_codes"] = [
                    "INCUMBENT_ADJACENCY_PRIORITY",
                    "ECONOMICS_UNAVAILABLE",
                ]
            route["reasons"], route[
                "localized_reasons"
            ] = _reason_payload(
                route["reason_codes"],
                route_code,
            )
        hypotheses.append(route)
    route_seven = hypotheses[7]
    _route_seven_gates(route_seven, case, capability)
    if route_seven["status"] == "passes" and not all(
        hypotheses[code]["status"] == "fails"
        for code in range(7)
    ):
        route_seven["status"] = NOT_CALCULABLE
        route_seven["reason_codes"].append(
            "LOWER_ROUTES_UNRESOLVED"
        )
        route_seven["reasons"], route_seven[
            "localized_reasons"
        ] = _reason_payload(
            route_seven["reason_codes"],
            7,
        )
    brownfield = hypotheses[5]
    if brownfield["status"] == "passes" and not all(
        hypotheses[code]["status"] == "fails"
        for code in range(5)
    ):
        brownfield["status"] = NOT_CALCULABLE
        brownfield["reason_codes"].append(
            "LOWER_NONFINANCIAL_ROUTES_UNRESOLVED"
        )
        brownfield["reasons"], brownfield[
            "localized_reasons"
        ] = _reason_payload(
            brownfield["reason_codes"],
            5,
        )
    graph_route = _base_route(8)
    graph_route["reason_codes"] = ["GRAPH_REQUIRED"]
    graph_route["reasons"], graph_route[
        "localized_reasons"
    ] = _reason_payload(["GRAPH_REQUIRED"], 8)
    hypotheses.append(graph_route)
    return apply_precedence(hypotheses)


def _reference(
    route: dict[str, Any],
    *,
    selection_basis: str,
    reason_code: str,
    reason_key: str,
) -> dict[str, Any]:
    localized = _localized(reason_key)
    return {
        "route_code": route["route_code"],
        "selection_basis": selection_basis,
        "incremental_national_value_m_sar": route.get(
            "incremental_national_value_m_sar",
            NOT_CALCULABLE,
        ),
        "reason_code": reason_code,
        "reason": localized["en"],
        "localized_reason": localized,
    }


def select_preferred_hypothesis(
    hypotheses: list[dict[str, Any]],
) -> dict[str, Any] | None:
    routes = sorted(
        hypotheses,
        key=lambda route: route["route_code"],
    )
    no_action = next(
        (
            route
            for route in routes
            if route.get("route_code") == 0
            and route.get("status") == "passes"
        ),
        None,
    )
    if no_action is not None:
        reason_codes = no_action.get("reason_codes", [])
        if reason_codes == ["EVIDENCED_NO_INTERVENTION"]:
            return _reference(
                no_action,
                selection_basis="EVIDENCED_NO_INTERVENTION",
                reason_code="EVIDENCED_NO_INTERVENTION",
                reason_key="route.0.reason",
            )
        if reason_codes == ["MONITOR_NO_IMMEDIATE_ACTION"]:
            return _reference(
                no_action,
                selection_basis="MONITOR_NO_IMMEDIATE_ACTION",
                reason_code="MONITOR_NO_IMMEDIATE_ACTION",
                reason_key="route.0.reason.monitor",
            )
        raise EvidenceIntegrityError(
            "Passing route 0 requires a governed reason code"
        )
    candidates = [
        route
        for route in routes
        if route.get("status") == "passes"
        and 0 < route.get("route_code", 0) < 8
        and _known_number(
            route.get(
                "unrounded_incremental_national_value_m_sar"
            )
        )
        is not None
    ]
    if candidates:
        selected = max(
            candidates,
            key=lambda route: (
                float(
                    route[
                        "unrounded_incremental_national_value_m_sar"
                    ]
                ),
                -int(route["route_code"]),
            ),
        )
        return _reference(
            selected,
            selection_basis=(
                "MAX_DEFENSIBLE_INCREMENTAL_NATIONAL_VALUE"
            ),
            reason_code="MAX_NV_SELECTED",
            reason_key="route.reason.max_nv_selected",
        )
    priority = next(
        (
            route
            for route in routes
            if route.get("priority") is True
        ),
        None,
    )
    if priority is None:
        return None
    return _reference(
        priority,
        selection_basis=(
            "EVIDENCE_PRIORITY_WITH_ECONOMICS_UNAVAILABLE"
        ),
        reason_code="BROWNFIELD_BEFORE_GREENFIELD",
        reason_key=f"route.{priority['route_code']}.reason",
    )
